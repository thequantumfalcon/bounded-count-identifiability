"""Kernel-check rational confidence queries after a source-bound research run.

Without --kind, check the boundary fixtures and deliberately inverted answers.
With --kind/--expect/--values, check one proposed answer. Output is always fresh.
This uses the same Lean kernel and trusted dependencies as the research suite.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess


PROJECT = Path(__file__).resolve().parent
REPOSITORY = PROJECT.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPLAY = load("certificate_replay", PROJECT / "replay.py")
DRIVER = REPLAY.DRIVER
AUDIT = DRIVER.AUDIT
EMITTER_PATH = REPOSITORY / "examples/d1_certificates.py"
EMITTER = load("certificate_emitter", EMITTER_PATH)

# Independent hand-selected model boundaries, not a second answer algorithm.
FIXTURES = (
    ("source", True, "1 7/10 9/10 2/5 7/10 3/10"),
    ("source", False, "1 7/10 9/10 2/5 7/10 1"),
    ("source", True, "0 -1 2 -1 1 1"),
    ("source", False, "0 -1 2 -1 1 3/2"),
    ("source", False, "-1 0 1 0 1 0"),
    ("source", False, "1 2 1 0 3 1/2"),
    ("source", False, "1 0 2 2 1 1/2"),
    ("source", False, "1 -2 -1 0 1 0"),
    ("source", False, "1 1 1 1/2 1/2 7/10"),
    # This set contains only p=sqrt(1/2), an irrational probability.
    ("nonempty", True, "1 1 1 1/2 1/2"),
    ("nonempty", True, "0 1/3 1/3 0 0"),
    ("nonempty", False, "0 0 1 1/4 1"),
    ("nonempty", False, "1 1 1 2 2"),
    ("nonempty", True, "1 2 2 3 3"),
    ("nonempty", False, "-1 0 1 0 1"),
    ("pair", True, "1 7/10 9/10 2/5 7/10 3/10 1/2"),
    ("pair", False, "1 7/10 9/10 2/5 7/10 3/10 9/10"),
    ("pair", True, "0 0 1 0 0 1 0"),
    ("pair", False, "1 0 1 0 1 -1/2 1/2"),
)


def diagnosed_false(
    module: str,
    stdout: str,
    stderr: str,
    *,
    exit_code: int,
    timed_out: bool,
    object_exists: bool,
    split_objects_exist: bool,
) -> bool:
    """Recognize only the pinned compiler's complete normalized-False failure."""
    if (
        exit_code != 1
        or timed_out
        or object_exists
        or split_objects_exist
        or stderr != ""
    ):
        return False
    pattern = (
        re.escape(module) + r"\.lean:[1-9][0-9]*:[1-9][0-9]*: error: "
        r"unsolved goals\n⊢ False\n?"
    )
    return re.fullmatch(pattern, stdout) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("lake", "existing-cache"), default="lake")
    parser.add_argument("--proof-run", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--lean-executable")
    parser.add_argument("--library", action="append", default=[])
    parser.add_argument("--kind", choices=tuple(EMITTER.PARAMETERS))
    parser.add_argument("--expect", choices=("accept", "reject"))
    parser.add_argument(
        "--values", help="comma-separated exact values; use --values=..."
    )
    args = parser.parse_args()
    if any(
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", x) for x in (args.run, args.proof_run)
    ):
        parser.error("invalid run name")
    custom = any(x is not None for x in (args.kind, args.expect, args.values))
    if custom and any(x is None for x in (args.kind, args.expect, args.values)):
        parser.error("a custom query requires --kind, --expect and --values")
    queries = (
        [(args.kind, args.expect == "accept", args.values.split(","))]
        if custom
        else [(kind, verdict, values.split()) for kind, verdict, values in FIXTURES]
    )
    # Validate every input before environment discovery or creating output.
    texts = [EMITTER.certificate(*query) for query in queries]
    initial = DRIVER.source_inputs("research")
    initial.update(
        {
            "runner": Path(__file__).resolve(),
            "emitter": EMITTER_PATH,
            "replay_runner": PROJECT / "replay.py",
        }
    )
    initial_hashes = {name: DRIVER.digest(path) for name, path in initial.items()}
    lean, libraries = DRIVER.resolve_environment(args)
    if any(
        DRIVER.digest(path) != initial_hashes[name] for name, path in initial.items()
    ):
        raise ValueError("inputs changed during environment discovery")
    paths = REPLAY.bind_proofs(args.proof_run, lean) | initial
    before = {name: DRIVER.digest(path) for name, path in paths.items()}
    output = REPOSITORY / "build/certificates" / args.run
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env["LEAN_NUM_THREADS"] = "2"
    env["LEAN_PATH"] = os.pathsep.join(
        map(
            str,
            [
                output,
                REPOSITORY / "build/research" / args.proof_run,
                PROJECT / ".verification" / ("d1-law-research-" + args.proof_run),
                *libraries,
            ],
        )
    )

    def sanitize(data: bytes) -> str:
        text = data.decode("utf-8", errors="replace")
        for path in [REPOSITORY, lean.parent.parent, *libraries]:
            text = text.replace(str(path), "<bound-path>").replace(
                path.as_posix(), "<bound-path>"
            )
        return text

    def execute(module: str, text: str, should_pass: bool) -> dict:
        source = output / (module + ".lean")
        source.write_text(text, encoding="utf-8", newline="\n")
        source_hash = DRIVER.digest(source)
        target = output / (module + ".olean")
        timed_out = False
        command = [str(lean), "--trust=0", "-o", str(target), source.name]
        try:
            result = subprocess.run(
                command,
                cwd=output,
                env=env,
                capture_output=True,
                timeout=90,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            timed_out = True
            result = subprocess.CompletedProcess(
                command, 124, error.stdout or b"", error.stderr or b""
            )
        stdout, stderr = sanitize(result.stdout), sanitize(result.stderr)
        for label, value in (("stdout", stdout), ("stderr", stderr)):
            (output / f"{module}.{label}.txt").write_text(
                value, encoding="utf-8", newline="\n"
            )
        audit = None
        if should_pass:
            passed = result.returncode == 0 and not timed_out and target.is_file()
            passed = (
                passed
                and target.stat().st_size > 0
                and not (stdout.strip() or stderr.strip())
            )
            if passed:
                object_hash = DRIVER.digest(target)
                audit = AUDIT.run_axiom_audit(
                    lean, module, ["certificate"], output, env, sanitize
                )
                passed = (
                    audit["status"] == "PASS" and DRIVER.digest(target) == object_hash
                )
        else:
            # A timeout, missing import or arbitrary compiler failure is not a
            # normalized-False rejection of the deliberately incorrect answer.
            passed = diagnosed_false(
                module,
                stdout,
                stderr,
                exit_code=result.returncode,
                timed_out=timed_out,
                object_exists=target.exists(),
                split_objects_exist=any(
                    (output / (module + suffix)).exists()
                    for suffix in (".olean.server", ".olean.private")
                ),
            )
        passed = passed and DRIVER.digest(source) == source_hash
        artifact_names = [
            module + suffix for suffix in (".lean", ".stdout.txt", ".stderr.txt")
        ]
        if target.exists():
            artifact_names.append(module + ".olean")
        if audit is not None:
            artifact_names.extend(
                module + suffix
                for suffix in (
                    ".audit.lean",
                    ".audit.stdout.txt",
                    ".audit.stderr.txt",
                    ".audit.json",
                )
            )
        return {
            "module": module,
            "status": "PASS" if passed else "FAIL",
            "expected_to_compile": should_pass,
            "exit_code": result.returncode,
            "timed_out": timed_out,
            "source_sha256": source_hash,
            "olean_sha256": DRIVER.digest(target) if target.is_file() else None,
            "stdout_sha256": DRIVER.digest(output / (module + ".stdout.txt")),
            "stderr_sha256": DRIVER.digest(output / (module + ".stderr.txt")),
            "audit": audit,
            "artifact_sha256": {
                name: DRIVER.digest(output / name) for name in artifact_names
            },
        }

    rows = []
    for index, (query, text) in enumerate(zip(queries, texts)):
        row = execute(f"Case{index:02}", text, True)
        row["query"] = {"kind": query[0], "accept": query[1], "values": query[2]}
        rows.append(row)
        if row["status"] != "PASS":
            break
    controls = []
    if (
        not custom
        and len(rows) == len(queries)
        and all(r["status"] == "PASS" for r in rows)
    ):
        for index in (0, 9, 15):
            kind, accepted, values = queries[index]
            controls.append(
                execute(
                    f"Wrong{index:02}",
                    EMITTER.certificate(kind, not accepted, values),
                    False,
                )
            )
    unchanged = all(
        path.is_file() and DRIVER.digest(path) == before[name]
        for name, path in paths.items()
    )
    REPLAY.bind_proofs(args.proof_run, lean)
    for row in rows:
        if row["audit"] is not None:
            AUDIT.validate_audit_record(
                output, row["module"], ["certificate"], row["audit"]
            )
    outputs_unchanged = True
    expected_outputs = set()
    for row in [*rows, *controls]:
        module = row["module"]
        REPLAY.reject_unbound_parts(output, module)
        expected_outputs.update(row["artifact_sha256"])
        outputs_unchanged = outputs_unchanged and all(
            (output / name).is_file() and DRIVER.digest(output / name) == digest
            for name, digest in row["artifact_sha256"].items()
        )
        for key, suffix in (
            ("source_sha256", ".lean"),
            ("stdout_sha256", ".stdout.txt"),
            ("stderr_sha256", ".stderr.txt"),
            ("olean_sha256", ".olean"),
        ):
            path = output / (module + suffix)
            expected = row[key]
            outputs_unchanged = outputs_unchanged and (
                not path.exists()
                if expected is None
                else path.is_file() and DRIVER.digest(path) == expected
            )
    outputs_unchanged = (
        outputs_unchanged
        and {path.name for path in output.iterdir() if path.is_file()}
        == expected_outputs
        and all(path.is_file() for path in output.iterdir())
    )
    passed = (
        unchanged
        and outputs_unchanged
        and len(rows) == len(queries)
        and all(r["status"] == "PASS" for r in rows)
        and (custom or len(controls) == 3)
        and all(r["status"] == "PASS" for r in controls)
    )
    record = {
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "proof_run": args.proof_run,
        "custom_query": custom,
        "input_sha256": before,
        "inputs_unchanged": unchanged,
        "outputs_unchanged": outputs_unchanged,
        "certificates": rows,
        "incorrect_answer_controls": controls,
        "scope": "Closed rational queries checked by Lean using the proved checker equivalences. Same kernel and trusted upstream objects; no parser/compiler verification, full Sage verification or physical validation.",
    }
    (output / "result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": record["status"],
                "certificates": len(rows),
                "incorrect_answers_rejected": len(controls),
            }
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
