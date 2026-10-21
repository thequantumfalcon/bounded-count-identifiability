"""Freshly check the separate D=1 proof using Python 3.11's standard library.

After building the pinned Lean project, run from the repository root:
    python lean/extensions/d1/verify_stability.py --run ci-check
Outputs go to build/stability/<run>; a run name cannot be reused.
Existing-cache mode installs nothing and takes explicit local library paths.
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

EXTENSION = Path(__file__).resolve().parent
LEAN_PROJECT = EXTENSION.parents[1]
REPOSITORY = LEAN_PROJECT.parent
MODULE = "CountD1Stability"
ROOTS = (
    "CountD1Stability.squared_parameter_error_le",
    "CountD1Stability.parameter_error_le_sqrt",
    "CountD1Stability.parameter_error_from_cumulant",
    "CountD1Stability.background_error_le",
    "CountD1Stability.bounded_observation_error",
)
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def resolve_environment(args: argparse.Namespace) -> tuple[Path, list[Path]]:
    if args.mode == "existing-cache":
        if not args.lean_executable or not args.library:
            raise ValueError("Existing-cache mode requires compiler and libraries")
        lean = Path(
            shutil.which(args.lean_executable) or args.lean_executable
        ).resolve()
        libraries = [Path(item).resolve() for item in args.library]
    else:
        if args.lean_executable or args.library:
            raise ValueError("Custom paths require existing-cache mode")
        probe = (
            "import json,os,shutil; "
            "print(json.dumps({'lean':shutil.which('lean'),"
            "'lean_path':os.environ.get('LEAN_PATH','')}))"
        )
        result = subprocess.run(
            ["lake", "env", sys.executable, "-c", probe],
            cwd=LEAN_PROJECT,
            capture_output=True,
            text=True,
            timeout=180,
            check=True,
        )
        resolved = json.loads(result.stdout)
        if not resolved.get("lean"):
            raise ValueError("Lake did not resolve a Lean compiler")
        lean = Path(resolved["lean"]).resolve()
        # Optional packages can advertise absent build directories. Missing
        # required imports remain compiler errors; no downloads are requested.
        candidates = [
            (LEAN_PROJECT / item).resolve()
            for item in resolved["lean_path"].split(os.pathsep)
            if item
        ]
        libraries = [item for item in candidates if item.is_dir()]
    if (
        not lean.is_file()
        or not libraries
        or any(not item.is_dir() for item in libraries)
    ):
        raise ValueError("Compiler or dependency library is missing")
    if any((item / f"{MODULE}.olean").exists() for item in libraries):
        raise ValueError("A dependency library contains an existing D=1 artifact")
    return lean, libraries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("lake", "existing-cache"), default="lake")
    parser.add_argument("--run", default="lake-check")
    parser.add_argument("--lean-executable")
    parser.add_argument("--library", action="append", default=[])
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", args.run):
        parser.error("--run requires 1 to 64 letters, digits, underscores or hyphens")

    source = EXTENSION / f"{MODULE}.lean"
    manifest_file = EXTENSION / "source_manifest.json"
    inputs = {
        "source": source,
        "verifier": Path(__file__).resolve(),
        "source_manifest": manifest_file,
        "dependency_lock": LEAN_PROJECT / "lake-manifest.json",
        "lake_config": LEAN_PROJECT / "lakefile.toml",
        "toolchain": LEAN_PROJECT / "lean-toolchain",
    }
    before = {name: digest(path) for name, path in inputs.items()}
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported extension manifest schema version")
    if (
        set(manifest.get("sources", {})) != {source.name}
        or tuple(manifest.get("theorem_roots", [])) != ROOTS
    ):
        raise ValueError("Expected one D=1 source and the exact five theorem roots")
    declared = manifest["sources"][source.name]
    if before["source"] != declared.get(
        "sha256"
    ) or source.stat().st_size != declared.get("bytes"):
        raise ValueError("D=1 source identity differs from its manifest")
    code = source.read_text(encoding="utf-8")
    if re.search(r"\b(sorry|admit|sorryAx|native_decide|axiom)\b", code) or re.search(
        r"\bset_option\s+debug\.skipKernelTC\s+true\b", code
    ):
        raise ValueError(
            "Source contains a prohibited proof admission or kernel bypass"
        )
    if inputs["toolchain"].read_text(encoding="utf-8").strip() != (
        "leanprover/lean4:v4.35.0"
    ):
        raise ValueError("Expected the pinned Lean 4.35.0 toolchain")

    output = (REPOSITORY / "build" / "stability" / args.run).resolve()
    if not output.is_relative_to(REPOSITORY) or output.exists():
        raise ValueError("Output must be a fresh directory inside the repository")
    lean, libraries = resolve_environment(args)
    compiler_before = digest(lean)
    output.mkdir(parents=True)
    target = output / f"{MODULE}.olean"
    replacements = [(str(REPOSITORY), "<repository>")]
    replacements.append((str(lean.parent.parent), "<lean-installation>"))
    replacements.extend(
        (str(path), f"<dependency-library-{index}>")
        for index, path in enumerate(libraries)
    )
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    def sanitize(data: bytes) -> str:
        value = data.decode("utf-8", errors="replace")
        for path, label in replacements:
            value = value.replace(path, label).replace(path.replace("\\", "/"), label)
        value = re.sub(r"[A-Za-z]:[\\/][^\s\"<>]*", "<absolute-path>", value)
        return re.sub(
            r"(?<![\w<>])/(?:[^\s/\"<>]+/)+[^\s\"<>]*", "<absolute-path>", value
        )

    version_result = subprocess.run(
        [str(lean), "--version"], capture_output=True, timeout=30, check=True
    )
    version = sanitize(version_result.stdout).strip()
    if not re.search(r"\bversion 4\.35\.0\b", version):
        raise ValueError("Compiler version does not match the pinned toolchain")
    env = os.environ.copy()
    env["LEAN_PATH"] = os.pathsep.join(str(path) for path in [output, *libraries])
    command = [str(lean), "--trust=0", "-o", str(target), source.name]
    timed_out = False
    try:
        result = subprocess.run(
            command,
            cwd=EXTENSION,
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
    stdout_file = output / f"{MODULE}.stdout.txt"
    stderr_file = output / f"{MODULE}.stderr.txt"
    stdout_file.write_text(stdout, encoding="utf-8")
    stderr_file.write_text(stderr, encoding="utf-8")
    printed = [
        {"theorem": theorem, "axioms": [x.strip() for x in raw.split(",") if x.strip()]}
        for theorem, raw in re.findall(
            r"'([^']+)' depends on axioms: \[([^]]*)\]", stdout
        )
    ]
    exact_roots = tuple(item["theorem"] for item in printed) == ROOTS
    axioms_allowed = exact_roots and all(
        len(item["axioms"]) == len(ALLOWED_AXIOMS)
        and set(item["axioms"]) == ALLOWED_AXIOMS
        for item in printed
    )
    unchanged = {
        name: path.is_file() and digest(path) == before[name]
        for name, path in inputs.items()
    }
    compiler_unchanged = lean.is_file() and digest(lean) == compiler_before
    artifact_exists = target.is_file() and target.stat().st_size > 0
    no_diagnostics = not re.search(r"\b(error|warning):|sorryAx", stdout + stderr)
    checks = {
        "compiler_exit_zero": result.returncode == 0,
        "not_timed_out": not timed_out,
        "exact_five_unique_printed_roots": exact_roots,
        "printed_axioms_allowed": axioms_allowed,
        "no_error_or_warning_diagnostics": no_diagnostics,
        "fresh_nonempty_olean": artifact_exists,
        "compiler_unchanged": compiler_unchanged,
        **{name + "_unchanged": value for name, value in unchanged.items()},
    }
    passed = all(checks.values())
    summary = {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verification_mode": args.mode,
        "compiler_version": version,
        "compiler_sha256": compiler_before,
        "dependency_library_count": len(libraries),
        "input_sha256": before,
        "checks": checks,
        "command": [
            "lean",
            "--trust=0",
            "-o",
            f"<fresh-build>/{MODULE}.olean",
            source.name,
        ],
        "exit_code": result.returncode,
        "timed_out": timed_out,
        "printed_axiom_lists": printed,
        "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "stdout_sha256": digest(stdout_file),
        "stderr_sha256": digest(stderr_file),
        "olean_sha256": digest(target) if artifact_exists else None,
        "uses_preexisting_dependency_artifacts": True,
        "clean_dependency_rebuild_claimed": False,
        "independent_kernel_recheck_claimed": False,
        "scope": (
            "Fresh Lean --trust=0 compilation of the separate D=1 algebraic "
            "stability proof, with exact printed theorem roots and a standard "
            "axiom allowlist. Reuses existing compiled dependencies; does not "
            "recheck the six-module core, build a probability model, establish "
            "data-error guarantees, or run an additional proof kernel."
        ),
    }
    write_json(output / "result.json", summary)
    print(f"D=1 stability: {summary['status']}; build/stability/{args.run}/result.json")
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
        # Do not expose environment paths or subprocess arguments on failures.
        print(
            f"D=1 verification failed during setup/execution ({type(error).__name__})"
        )
        raise SystemExit(1) from None
