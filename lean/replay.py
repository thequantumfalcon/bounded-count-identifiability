"""Replay freshly audited project declarations with Lean's bundled kernel.

Run after the research suite: python lean/replay.py --proof-run ci-check --run ci-check
This is the same Lean kernel, not an independent proof implementation. Imported
dependencies are trusted; the separate axiom audit is still required.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
REPOSITORY = PROJECT.parent
_spec = importlib.util.spec_from_file_location(
    "replay_proof_driver", PROJECT / "extensions/d1-law/verify_law_bridge.py"
)
assert _spec is not None and _spec.loader is not None
DRIVER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DRIVER)
AUDIT = DRIVER.AUDIT


def reject_unbound_parts(objects: Path, module: str) -> None:
    # LeanChecker loads these optional files when present. Current legacy
    # project sources produce neither; require an explicit binding upgrade
    # before accepting Lean's split module format here.
    if any(
        (objects / (module + suffix)).exists()
        for suffix in (".olean.server", ".olean.private")
    ):
        raise ValueError("Unbound split module artifact")


def bind_proofs(proof_run: str, lean: Path) -> dict[str, Path]:
    """Require source-bound, independently reread audits for every replay target."""
    paths = DRIVER.source_inputs("research")
    paths["compiler"] = lean
    before = {name: DRIVER.digest(path) for name, path in paths.items()}
    DRIVER.check_sources(paths, "research")
    core_name = "d1-law-research-" + proof_run
    core_dir = PROJECT / "verification" / core_name
    core_build = PROJECT / ".verification" / core_name
    core_ok, core_files = DRIVER.check_core_receipt(core_dir, core_build, before)
    if not core_ok:
        raise ValueError("Core source/artifact/audit binding failed")
    extension_dir = REPOSITORY / "build/research" / proof_run
    receipt_path = extension_dir / "result.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected = list(AUDIT.ROOTS | AUDIT.RESEARCH_ROOTS)
    if (
        receipt.get("schema_version") != 2
        or receipt.get("status") != "PASS"
        or receipt.get("axiom_audit_method") != "separate-generated-import-query"
        or receipt.get("suite") != "research"
        or receipt.get("input_sha256") != before
        or receipt.get("core_output_sha256") != core_files
        or not receipt.get("checks")
        or not all(value is True for value in receipt["checks"].values())
        or [row.get("module") for row in receipt.get("modules", [])] != expected
    ):
        raise ValueError("Research receipt is incomplete or no longer source-bound")
    paths["research_receipt"] = receipt_path
    paths["core_receipt"] = core_dir / "result.json"
    core = json.loads(paths["core_receipt"].read_text(encoding="utf-8"))
    for row in [*core["modules"], *receipt["modules"]]:
        module = row["module"]
        is_core = module in AUDIT.CORE
        logs = core_dir if is_core else extension_dir
        objects = core_build if is_core else extension_dir
        reject_unbound_parts(objects, module)
        other = extension_dir if is_core else core_build
        if any(
            (other / (module + suffix)).exists()
            for suffix in (".olean", ".olean.server", ".olean.private")
        ):
            raise ValueError("Project artifact would shadow the bound replay target")
        if (
            row.get("status") != "PASS"
            or row.get("source_sha256") != before[module]
            or row.get("exit_code") != 0
            or row.get("timed_out") is not False
            or (
                not is_core
                and (
                    not row.get("checks")
                    or not all(v is True for v in row["checks"].values())
                )
            )
        ):
            raise ValueError("Module source identity/status failed")
        for kind, path in AUDIT.validate_audit_record(
            logs, module, AUDIT.full_roots(module), row.get("audit")
        ).items():
            paths[module + "/audit/" + kind] = path
        expected_printed = row["audit"]["printed_axiom_lists"]
        if not is_core:
            expected_printed = [
                {"theorem": name, "axioms": axioms}
                for name, axioms in expected_printed.items()
            ]
        if row.get("printed_axiom_lists") != expected_printed:
            raise ValueError("Module audit summary changed")
        for kind, path in (
            ("olean", objects / (module + ".olean")),
            ("stdout", logs / (module + ".stdout.txt")),
            ("stderr", logs / (module + ".stderr.txt")),
        ):
            if not path.is_file() or DRIVER.digest(path) != row.get(kind + "_sha256"):
                raise ValueError("Compiled object or log binding failed")
            paths[module + "/" + kind] = path
        if not is_core:
            snapshot = extension_dir / (module + ".lean")
            if DRIVER.digest(snapshot) != before[module]:
                raise ValueError("Compiled source snapshot changed")
            paths[module + "/snapshot"] = snapshot
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("lake", "existing-cache"), default="lake")
    parser.add_argument("--proof-run", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--lean-executable")
    parser.add_argument("--library", action="append", default=[])
    args = parser.parse_args()
    if any(
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", tag)
        for tag in (args.run, args.proof_run)
    ):
        raise ValueError("Invalid proof/replay run name")
    initial = DRIVER.source_inputs("research")
    initial["replay_runner"] = Path(__file__).resolve()
    initial_hashes = {name: DRIVER.digest(path) for name, path in initial.items()}
    lean, libraries = DRIVER.resolve_environment(args)
    if any(
        not path.is_file() or DRIVER.digest(path) != initial_hashes[name]
        for name, path in initial.items()
    ):
        raise ValueError("Replay/proof inputs changed during environment discovery")
    checker = lean.with_name("leanchecker" + lean.suffix)
    if not checker.is_file():
        raise ValueError("Pinned compiler installation has no leanchecker")
    paths = bind_proofs(args.proof_run, lean)
    paths.update({"replay_runner": Path(__file__).resolve(), "leanchecker": checker})
    before = {name: DRIVER.digest(path) for name, path in paths.items()}
    output = REPOSITORY / "build/replay" / args.run
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env["LEAN_NUM_THREADS"] = "2"
    # LeanChecker.findSysroot otherwise shells out to `lean` from PATH. Outside
    # the project that may select an Elan shim with no default toolchain, or a
    # different installation. Bind both lookup routes to the audited compiler.
    env["LEAN_SYSROOT"] = str(lean.parent.parent)
    env["PATH"] = str(lean.parent) + os.pathsep + env.get("PATH", "")
    env["LEAN_PATH"] = os.pathsep.join(
        map(
            str,
            [
                REPOSITORY / "build/research" / args.proof_run,
                PROJECT / ".verification" / ("d1-law-research-" + args.proof_run),
                *libraries,
            ],
        )
    )

    def sanitize(data: bytes) -> str:
        value = data.decode("utf-8", errors="replace")
        for path, label in [
            (REPOSITORY, "<repository>"),
            (lean.parent.parent, "<lean>"),
            *[(p, "<dependency>") for p in libraries],
        ]:
            value = value.replace(str(path), label).replace(path.as_posix(), label)
        value = re.sub(r"[A-Za-z]:[\\/][^\s\"<>]*", "<absolute-path>", value)
        return re.sub(
            r"(?<![\w<>])/(?:[^\s/\"<>]+/)+[^\s\"<>]*", "<absolute-path>", value
        )

    records = []
    modules = [*AUDIT.CORE, *AUDIT.ROOTS, *AUDIT.RESEARCH_ROOTS]
    for module in modules:
        command = [str(checker), "--verbose", module]
        timed_out = False
        try:
            result = subprocess.run(
                command,
                cwd=output,
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
        log_paths = {}
        for kind, value in (("stdout", stdout), ("stderr", stderr)):
            path = output / (module + "." + kind + ".txt")
            path.write_bytes(value.encode("utf-8"))
            log_paths[kind + "_sha256"] = DRIVER.digest(path)
        passed = (
            result.returncode == 0
            and not timed_out
            and stdout.strip() == "replaying " + module
            and not stderr.strip()
        )
        records.append(
            {
                "module": module,
                "status": "PASS" if passed else "FAIL",
                "command": ["leanchecker", "--verbose", module],
                "exit_code": result.returncode,
                "timed_out": timed_out,
                **log_paths,
            }
        )
        print(f"Kernel replay {module}: {'PASS' if passed else 'FAIL'}", flush=True)
        if not passed:
            break
    unchanged = all(
        path.is_file() and DRIVER.digest(path) == before[name]
        for name, path in paths.items()
    )
    try:
        bind_proofs(args.proof_run, lean)
        bindings_valid = True
    except (OSError, ValueError, KeyError, TypeError):
        bindings_valid = False
    logs_unchanged = all(
        (output / (row["module"] + "." + kind + ".txt")).is_file()
        and DRIVER.digest(output / (row["module"] + "." + kind + ".txt"))
        == row[kind + "_sha256"]
        for row in records
        for kind in ("stdout", "stderr")
    )
    passed = (
        logs_unchanged
        and unchanged
        and bindings_valid
        and len(records) == len(modules)
        and all(row["status"] == "PASS" for row in records)
    )
    DRIVER.write_json(
        output / "result.json",
        {
            "schema_version": 1,
            "status": "PASS" if passed else "FAIL",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "proof_run": args.proof_run,
            "input_sha256": before,
            "inputs_unchanged": unchanged,
            "logs_unchanged": logs_unchanged,
            "proof_bindings_valid": bindings_valid,
            "modules": records,
            "independent_kernel_recheck_claimed": False,
            "scope": "Same bundled Lean kernel replays safe, total declarations of each selected project module from trusted imported dependencies. Unsafe and partial declarations are outside the replay scope; current project sources use neither. Separate generated axiom audits remain required. No independent kernel or dependency rebuild is claimed.",
        },
    )
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
        print(f"Kernel replay failed ({type(error).__name__})")
        raise SystemExit(1) from None
