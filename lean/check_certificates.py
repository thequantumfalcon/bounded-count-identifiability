"""Kernel-check rational confidence queries after a source-bound research run.

Without --kind, check the boundary fixtures and deliberately inverted answers.
With --kind/--expect/--values, check one proposed answer. Output is always fresh.
This uses the same Lean kernel and trusted dependencies as the research suite.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
from types import ModuleType


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
COUNT_EMITTER_PATH = REPOSITORY / "examples/d1_count_certificates.py"


def load_emitter(name: str, path: Path) -> tuple[ModuleType, str]:
    """Execute the fingerprinted source snapshot, bypassing cached bytecode."""
    source = path.read_bytes()
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module, hashlib.sha256(source).hexdigest()


EMITTER, EMITTER_LOADED_HASH = load_emitter("certificate_emitter", EMITTER_PATH)
COUNT_EMITTER, COUNT_EMITTER_LOADED_HASH = load_emitter(
    "count_certificate_emitter", COUNT_EMITTER_PATH
)


def check_emitter_snapshots() -> None:
    for path, expected in (
        (EMITTER_PATH, EMITTER_LOADED_HASH),
        (COUNT_EMITTER_PATH, COUNT_EMITTER_LOADED_HASH),
    ):
        if DRIVER.digest(path) != expected:
            raise ValueError("emitter changed after its source snapshot was loaded")


COUNT_FIXTURES = (
    (["0", "1", "2", "4"], "1", "1/20", 6),
    (["0"], "0", "1/20", 6),
    (["0", "1", "1", "0"], "0", "1/2", 6),
    (["2", "0", "1", "3", "0"], "1/7", "1/3", 3),
    (["0"] * COUNT_EMITTER.MAX_COUNTS, "1", "1/20", 6),
    (["999999999999", "0"], "1", "1/20", 1),
)


def count_cases(fixtures: list | tuple) -> list[tuple[dict, str]]:
    return [
        (
            {"counts": counts, "background": B, "alpha": alpha, "digits": digits},
            COUNT_EMITTER.certificate(counts, B, alpha, digits),
        )
        for counts, B, alpha, digits in fixtures
    ]


def count_controls() -> list[tuple[str, str]]:
    """Propose false aggregation, moment, radius and endpoint statements."""
    counts, values = COUNT_EMITTER.prepare(*COUNT_FIXTURES[0])
    mutations = (
        ("WrongMean", {"m1": values["m1"] + 1}),
        ("WrongMoment", {"m2": Fraction(sum(x * x for x in counts), len(counts))}),
        ("WrongRadius", {"R1": Fraction(0), "a": values["m1"], "c": values["m1"]}),
        (
            "WrongSign",
            {
                "R2": -values["R2"],
                "d": values["m2"] + values["R2"],
                "e": values["m2"] - values["R2"],
            },
        ),
        ("WrongEndpoint", {"e": values["e"] - 1}),
    )
    return [
        (name, COUNT_EMITTER.render(counts, values | edits))
        for name, edits in mutations
    ]


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
    parser.add_argument(
        "--suite", choices=("feasibility", "counts"), default="feasibility"
    )
    parser.add_argument("--kind", choices=tuple(EMITTER.PARAMETERS))
    parser.add_argument("--expect", choices=("accept", "reject"))
    parser.add_argument(
        "--values", help="comma-separated exact values; use --values=..."
    )
    parser.add_argument(
        "--counts", help="comma-separated natural counts (counts suite)"
    )
    parser.add_argument(
        "--background", help="exact fixed background ceiling (counts suite)"
    )
    parser.add_argument("--alpha", help="preselected exact error level (counts suite)")
    parser.add_argument("--digits", type=int, default=6)
    args = parser.parse_args()
    if any(
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", x) for x in (args.run, args.proof_run)
    ):
        parser.error("invalid run name")
    feasibility_custom = any(
        x is not None for x in (args.kind, args.expect, args.values)
    )
    counts_custom = any(
        x is not None for x in (args.counts, args.background, args.alpha)
    )
    if args.suite == "counts" and feasibility_custom:
        parser.error("--kind/--expect/--values require the feasibility suite")
    if args.suite == "feasibility" and (counts_custom or args.digits != 6):
        parser.error("count arguments require --suite counts")
    if feasibility_custom and any(
        x is None for x in (args.kind, args.expect, args.values)
    ):
        parser.error("a custom query requires --kind, --expect and --values")
    if counts_custom and any(
        x is None for x in (args.counts, args.background, args.alpha)
    ):
        parser.error(
            "a custom count record requires --counts, --background and --alpha"
        )
    if not counts_custom and args.digits != 6:
        parser.error("--digits applies only to a custom count record")
    custom = feasibility_custom or counts_custom
    # Validate every input before environment discovery or creating output.
    check_emitter_snapshots()
    if args.suite == "counts":
        cases = count_cases(
            [(args.counts.split(","), args.background, args.alpha, args.digits)]
            if custom
            else COUNT_FIXTURES
        )
        wrong_cases = [] if custom else count_controls()
    else:
        queries = (
            [(args.kind, args.expect == "accept", args.values.split(","))]
            if custom
            else [(kind, verdict, values.split()) for kind, verdict, values in FIXTURES]
        )
        cases = [
            (
                {"kind": kind, "accept": verdict, "values": values},
                EMITTER.certificate(kind, verdict, values),
            )
            for kind, verdict, values in queries
        ]
        wrong_cases = (
            []
            if custom
            else [
                (f"Wrong{index:02}", EMITTER.certificate(kind, not verdict, values))
                for index in (0, 9, 15)
                for kind, verdict, values in [queries[index]]
            ]
        )
    check_emitter_snapshots()
    initial = DRIVER.source_inputs("research")
    initial.update(
        {
            "runner": Path(__file__).resolve(),
            "emitter": EMITTER_PATH,
            "count_emitter": COUNT_EMITTER_PATH,
            "replay_runner": PROJECT / "replay.py",
        }
    )
    initial_hashes = {name: DRIVER.digest(path) for name, path in initial.items()}
    check_emitter_snapshots()
    lean, libraries = DRIVER.resolve_environment(args)
    if any(
        DRIVER.digest(path) != initial_hashes[name] for name, path in initial.items()
    ):
        raise ValueError("inputs changed during environment discovery")
    paths = REPLAY.bind_proofs(args.proof_run, lean) | initial
    before = {name: DRIVER.digest(path) for name, path in paths.items()}
    folder = "count-certificates" if args.suite == "counts" else "certificates"
    output = REPOSITORY / "build" / folder / args.run
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
    for index, (query, text) in enumerate(cases):
        row = execute(f"Case{index:02}", text, True)
        row["query"] = query
        rows.append(row)
        if row["status"] != "PASS":
            break
    controls = []
    if (
        not custom
        and len(rows) == len(cases)
        and all(r["status"] == "PASS" for r in rows)
    ):
        for module, text in wrong_cases:
            controls.append(execute(module, text, False))
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
        and len(rows) == len(cases)
        and all(r["status"] == "PASS" for r in rows)
        and len(controls) == len(wrong_cases)
        and all(r["status"] == "PASS" for r in controls)
    )
    record = {
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "proof_run": args.proof_run,
        "suite": args.suite,
        "custom_query": custom,
        "input_sha256": before,
        "inputs_unchanged": unchanged,
        "outputs_unchanged": outputs_unchanged,
        "certificates": rows,
        "incorrect_answer_controls": controls,
        "scope": "Closed exact queries checked by Lean using proved equivalences and count/radius definitions. Count certificates link the encoded observations to rational boxes; coverage retains the universal theorem's model assumptions. Same kernel and trusted upstream objects; no parser/compiler verification, full Sage verification or physical validation.",
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
