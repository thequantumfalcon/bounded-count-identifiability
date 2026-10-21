"""Compile the frozen proof sources afresh and write portable verification receipts.

Default: python verify.py --run lake-check
The default resolves Lean and its dependency path through `lake env`.
Existing-cache mode takes explicit local paths but never writes them to receipts.
No dependencies are installed or updated by the existing-cache mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = (
    "CountSeriesCore",
    "CountLawEncoding",
    "CountIdentification",
    "CountPoissonChannel",
    "CountObservedIdentification",
    "CountSharpness",
)
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    verifier_before = digest(Path(__file__))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("lake", "existing-cache"), default="lake")
    parser.add_argument("--run", default="lake-check")
    parser.add_argument("--lean-executable")
    parser.add_argument("--library", action="append", default=[])
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.run):
        parser.error("--run must contain only letters, digits, underscores, or hyphens")
    if args.mode == "existing-cache":
        if not args.lean_executable or not args.library:
            parser.error("existing-cache mode requires --lean-executable and --library")
        resolved_lean = shutil.which(args.lean_executable)
        lean = Path(resolved_lean or args.lean_executable).resolve()
        libraries = [Path(item).resolve() for item in args.library]
    else:
        if args.lean_executable or args.library:
            parser.error("custom compiler and libraries require existing-cache mode")
        probe = (
            "import json,os,shutil; "
            "print(json.dumps({'lean':shutil.which('lean'),"
            "'lean_path':os.environ.get('LEAN_PATH','')}))"
        )
        result = subprocess.run(
            ["lake", "env", sys.executable, "-c", probe],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=True,
        )
        resolved = json.loads(result.stdout)
        lean = Path(resolved["lean"]).resolve()
        # Lake can advertise libraries for optional packages not built by this
        # target. Retain existing search directories; missing required imports
        # will still be rejected by Lean itself.
        candidates = [
            (ROOT / item).resolve()
            for item in resolved["lean_path"].split(os.pathsep)
            if item
        ]
        libraries = [item for item in candidates if item.is_dir()]
    if not lean.is_file() or any(not item.is_dir() for item in libraries):
        raise ValueError("Compiler or dependency library is missing")

    # The new directory is first on the import path. Original campaign .olean
    # files are not needed. Refuse a collision in explicitly supplied libraries.
    if args.mode == "existing-cache" and any(
        (lib / f"{module}.olean").exists() for lib in libraries for module in MODULES
    ):
        raise ValueError(
            "Existing-cache libraries must not contain project module artifacts"
        )
    receipt_dir = ROOT / "verification" / args.run
    build_dir = ROOT / ".verification" / args.run
    if receipt_dir.exists() or build_dir.exists():
        raise FileExistsError(
            "Run name already exists; choose a new --run to preserve evidence"
        )
    manifest = json.loads((ROOT / "source_manifest.json").read_text(encoding="utf-8"))
    for module in MODULES:
        name = f"{module}.lean"
        if digest(ROOT / name) != manifest["sources"][name]["sha256"]:
            raise ValueError(f"Frozen source hash mismatch: {name}")
        source = (ROOT / name).read_text(encoding="utf-8")
        if re.search(
            r"\b(sorry|admit|native_decide)\b|^\s*axiom\s", source, re.MULTILINE
        ):
            raise ValueError(f"Admission or axiom declaration found: {name}")
    receipt_dir.mkdir(parents=True)
    build_dir.mkdir(parents=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = os.pathsep.join(str(p) for p in [build_dir, *libraries])
    replacements = [
        (str(ROOT), "<project>"),
        (str(lean.parent.parent), "<lean-installation>"),
    ]
    replacements.extend(
        (str(lib), f"<dependency-library-{i}>") for i, lib in enumerate(libraries)
    )
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)

    def sanitize(data: bytes) -> str:
        value = data.decode("utf-8", errors="replace")
        for path, replacement in replacements:
            value = value.replace(path, replacement).replace(
                path.replace("\\", "/"), replacement
            )
        # Suppress any remaining absolute filesystem location before storing logs.
        value = re.sub(r"[A-Za-z]:[\\/][^\s\"<>]*", "<absolute-path>", value)
        return value

    version_result = subprocess.run(
        [str(lean), "--version"], capture_output=True, timeout=30, check=True
    )
    version = sanitize(version_result.stdout).strip()
    if not re.search(r"\bversion 4\.35\.0\b", version):
        raise ValueError("Expected the pinned Lean 4.35.0 compiler")
    records = []
    for module in MODULES:
        source = ROOT / f"{module}.lean"
        target = build_dir / f"{module}.olean"
        command = [
            str(lean),
            "--trust=0",
            "-o",
            str(target.relative_to(ROOT)),
            source.name,
        ]
        timed_out = False
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                capture_output=True,
                timeout=240,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            timed_out = True
            result = subprocess.CompletedProcess(
                command, 124, error.stdout or b"", error.stderr or b""
            )
        stdout, stderr = sanitize(result.stdout), sanitize(result.stderr)
        stdout_path = receipt_dir / f"{module}.stdout.txt"
        stderr_path = receipt_dir / f"{module}.stderr.txt"
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        axiom_lists = {}
        for theorem, raw in re.findall(
            r"'([^']+)' depends on axioms: \[([^]]*)\]", stdout
        ):
            axioms = [item.strip() for item in raw.split(",") if item.strip()]
            axiom_lists[theorem] = axioms
        source_unchanged = digest(source) == manifest["sources"][source.name]["sha256"]
        axiom_check = bool(axiom_lists) and all(
            set(items) <= ALLOWED_AXIOMS for items in axiom_lists.values()
        )
        no_diagnostics = not re.search(r"\b(error|warning):|sorryAx", stdout + stderr)
        passed = (
            result.returncode == 0
            and source_unchanged
            and axiom_check
            and no_diagnostics
        )
        records.append(
            {
                "module": module,
                "source_sha256": digest(source),
                "source_unchanged": source_unchanged,
                "command": [
                    "lean",
                    "--trust=0",
                    "-o",
                    f"<fresh-build>/{module}.olean",
                    source.name,
                ],
                "exit_code": result.returncode,
                "timed_out": timed_out,
                "status": "PASS" if passed else "FAIL",
                "printed_axiom_lists": axiom_lists,
                "printed_axioms_checked": axiom_check,
                "no_error_or_warning_diagnostics": no_diagnostics,
                "stdout_sha256": digest(stdout_path),
                "stderr_sha256": digest(stderr_path),
                "olean_sha256": digest(target) if target.is_file() else None,
            }
        )
        print(f"{module}: {'PASS' if passed else 'FAIL'}", flush=True)
        if not passed:
            break
    verifier_unchanged = digest(Path(__file__)) == verifier_before
    passed = (
        verifier_unchanged
        and len(records) == len(MODULES)
        and all(row["status"] == "PASS" for row in records)
    )
    summary = {
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verification_mode": args.mode,
        "compiler_version": version,
        "compiler_sha256": digest(lean),
        "dependency_library_count": len(libraries),
        "project_artifacts_recompiled_in_dependency_order": True,
        "uses_preexisting_dependency_artifacts": True,
        "clean_network_dependency_build_claimed": False,
        "independent_kernel_recheck_claimed": False,
        "source_manifest_sha256": digest(ROOT / "source_manifest.json"),
        "dependency_lock_sha256": digest(ROOT / "lake-manifest.json"),
        "verifier_sha256": verifier_before,
        "verifier_unchanged": verifier_unchanged,
        "modules": records,
        "scope": "Fresh elaboration and compilation of the six project sources with Lean --trust=0; dependencies use existing compiled libraries. Printed axiom lists are checked. This is not a clean rebuild of Lean or mathlib, nor an additional independent proof-kernel check.",
    }
    write_json(receipt_dir / "result.json", summary)
    print(f"Overall: {summary['status']}; receipt: verification/{args.run}/result.json")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
