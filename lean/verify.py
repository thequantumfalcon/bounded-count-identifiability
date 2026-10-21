"""Compile the frozen proof sources afresh and write portable verification receipts.

Default: python verify.py --run lake-check
The default resolves Lean and its dependency path through `lake env`.
Existing-cache mode takes explicit local paths but never writes them to receipts.
No dependencies are installed or updated by the existing-cache mode.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_policy_spec = importlib.util.spec_from_file_location(
    "core_proof_audit", ROOT / "proof_audit.py"
)
assert _policy_spec is not None and _policy_spec.loader is not None
AUDIT = importlib.util.module_from_spec(_policy_spec)
_policy_spec.loader.exec_module(AUDIT)
MODULES = AUDIT.CORE


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    inputs = {
        "verifier": Path(__file__).resolve(),
        "proof_audit": ROOT / "proof_audit.py",
        "source_manifest": ROOT / "source_manifest.json",
        "dependency_lock": ROOT / "lake-manifest.json",
        "lake_config": ROOT / "lakefile.toml",
        "toolchain": ROOT / "lean-toolchain",
        **{module: ROOT / (module + ".lean") for module in MODULES},
    }
    before = {name: digest(path) for name, path in inputs.items()}
    verifier_before = before["verifier"]
    if (
        inputs["toolchain"].read_text(encoding="utf-8").strip()
        != "leanprover/lean4:v4.35.0"
    ):
        raise ValueError("Expected pinned Lean toolchain")
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
    if manifest.get("schema_version") != 1 or set(manifest.get("sources", {})) != {
        module + ".lean" for module in MODULES
    }:
        raise ValueError("Unexpected core source manifest")
    for module in MODULES:
        name = f"{module}.lean"
        if digest(ROOT / name) != manifest["sources"][name]["sha256"]:
            raise ValueError(f"Frozen source hash mismatch: {name}")
        source = (ROOT / name).read_text(encoding="utf-8")
        if (ROOT / name).stat().st_size != manifest["sources"][name]["bytes"]:
            raise ValueError("Core source size differs from its manifest")
        AUDIT.validate_source(source)
    if any(digest(path) != before[name] for name, path in inputs.items()):
        raise ValueError("Proof inputs changed during environment discovery")
    inputs["compiler"] = lean
    before["compiler"] = digest(lean)
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
        compiled_hash = (
            digest(target) if target.is_file() and target.stat().st_size > 0 else None
        )
        audit = (
            AUDIT.run_axiom_audit(
                lean, module, AUDIT.full_roots(module), receipt_dir, env, sanitize
            )
            if result.returncode == 0 and target.is_file() and target.stat().st_size > 0
            else None
        )
        axiom_lists = audit["printed_axiom_lists"] if audit else {}
        axiom_check = audit is not None and audit["status"] == "PASS"
        source_unchanged = digest(source) == before[module]
        no_diagnostics = not re.search(r"\b(error|warning):|sorryAx", stdout + stderr)
        passed = (
            result.returncode == 0
            and not timed_out
            and source_unchanged
            and axiom_check
            and no_diagnostics
            and compiled_hash is not None
            and target.is_file()
            and digest(target) == compiled_hash
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
                "audit": audit,
                "printed_axiom_lists": axiom_lists,
                "printed_axioms_checked": axiom_check,
                "no_error_or_warning_diagnostics": no_diagnostics,
                "stdout_sha256": digest(stdout_path),
                "stderr_sha256": digest(stderr_path),
                "olean_sha256": compiled_hash,
            }
        )
        print(f"{module}: {'PASS' if passed else 'FAIL'}", flush=True)
        if not passed:
            break
    unchanged = {
        name: path.is_file() and digest(path) == before[name]
        for name, path in inputs.items()
    }
    verifier_unchanged = unchanged["verifier"]
    evidence_valid = True
    for row in records:
        module = row["module"]
        try:
            AUDIT.validate_audit_record(
                receipt_dir, module, AUDIT.full_roots(module), row["audit"] or {}
            )
            for kind, path in (
                ("olean", build_dir / (module + ".olean")),
                ("stdout", receipt_dir / (module + ".stdout.txt")),
                ("stderr", receipt_dir / (module + ".stderr.txt")),
            ):
                if not path.is_file() or digest(path) != row[kind + "_sha256"]:
                    raise ValueError("Core artifact/log changed")
        except (OSError, ValueError, TypeError, KeyError):
            evidence_valid = False
    passed = (
        all(unchanged.values())
        and evidence_valid
        and len(records) == len(MODULES)
        and all(row["status"] == "PASS" for row in records)
    )
    summary = {
        "schema_version": 2,
        "axiom_audit_method": "separate-generated-import-query",
        "proof_audit_sha256": before["proof_audit"],
        "input_sha256": before,
        "checks": {
            **{k + "_unchanged": v for k, v in unchanged.items()},
            "evidence_unchanged_and_valid": evidence_valid,
        },
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verification_mode": args.mode,
        "compiler_version": version,
        "compiler_sha256": before["compiler"],
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
        "scope": "Fresh elaboration and compilation of the six project sources with Lean --trust=0; dependencies use existing compiled libraries. A separate generated import-only query checks the complete registered roots and permitted axiom subsets; source compilation output is diagnostic only. This is not a clean rebuild of Lean or mathlib, nor an additional independent proof-kernel check.",
    }
    write_json(receipt_dir / "result.json", summary)
    print(f"Overall: {summary['status']}; receipt: verification/{args.run}/result.json")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"Core verification failed ({type(error).__name__})")
        raise SystemExit(1) from None
