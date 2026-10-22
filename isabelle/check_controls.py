"""Reproduce selected rejection controls after the genuine audited build passes.

Requires Isabelle2025-2. A nonzero exit alone is never an accepted control.
No environment variables are changed; the caller owns toolchain isolation.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROLS = {
    "false_endpoint": "Count_Wrong_Endpoint",
    "sorry": "Count_Sorry_Control",
    "extra_axiom": "Count_Extra_Axiom",
    "changed_definition": "Count_Endpoints",
}
DEFINITIONS = {"Count_Endpoints.feasible_def_raw", "Count_Endpoints.pair_box_def_raw"}
MAX_LOG_BYTES = 8 * 1024 * 1024


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(name, theory, code, timed_out, stdout, stderr):
    if timed_out or code != 1:
        return False, "timeout or exit code other than the expected build failure (1)"
    if stderr.strip() or "ENDPOINT_AUDIT_PASS" in stdout:
        return False, "stderr is nonempty or an audit acceptance marker appeared"
    errors = [
        line[3:].strip() for line in stdout.splitlines() if line.startswith("***")
    ]
    errors = [line for line in errors if line]
    context = re.compile(
        r'At command "(done|sorry|ML)" \(line \d+ of "[^"\r\n]*'
        + re.escape(theory)
        + r'\.thy"\)'
    )
    commands = [match.group(1) for line in errors if (match := context.fullmatch(line))]
    core = [line for line in errors if not context.fullmatch(line)]
    if name == "false_endpoint":
        ok = core == ["Failed to finish proof:", "goal (1 subgoal):", "1. False"]
        return ok and commands == [
            "done"
        ], "exact normalized False residual at the intended done command"
    if name == "sorry":
        ok = bool(core) and all(
            line == "Cheating requires quick_and_dirty mode!" for line in core
        )
        return ok and "sorry" in commands and set(commands) <= {
            "sorry",
            "ML",
        }, "strict batch rejection of sorry"
    if name == "extra_axiom":
        actual = [
            line.removeprefix("ACTUAL_AXIOM ")
            for line in core
            if line.startswith("ACTUAL_AXIOM ")
        ]
        expected = [
            line.removeprefix("EXPECTED_AXIOM ")
            for line in core
            if line.startswith("EXPECTED_AXIOM ")
        ]
        other = [
            line
            for line in core
            if not line.startswith(("ACTUAL_AXIOM ", "EXPECTED_AXIOM "))
        ]
        ok = (
            other == ["ENDPOINT_AUDIT: unexpected local axiom inventory"]
            and len(actual) == 3
            and set(actual)
            == DEFINITIONS | {"Count_Extra_Axiom.deliberately_extra_axiom"}
            and len(expected) == 2
            and set(expected) == DEFINITIONS
        )
        return ok and commands == [
            "ML"
        ], "specific extra axiom rejected by inventory guard"
    actual = [line for line in core if line.startswith("ACTUAL_TERM Term.")]
    expected = [line for line in core if line.startswith("EXPECTED_TERM Term.")]
    other = [
        line
        for line in core
        if not line.startswith(("ACTUAL_TERM Term.", "EXPECTED_TERM Term."))
    ]
    ok = (
        other
        == [
            "ENDPOINT_AUDIT: local defining equation differs from independent specification: Count_Endpoints.pair_box_def_raw",
            "BETA_ETA_ALPHA_EQUAL false",
        ]
        and len(actual) == len(expected) == 1
        and actual[0].removeprefix("ACTUAL_TERM ")
        != expected[0].removeprefix("EXPECTED_TERM ")
    )
    return ok and commands == [
        "ML"
    ], "specific typed defining-equation mismatch after inventory guard"


def stop_owned_process(proc):
    """Bound shutdown to this process group/tree, never a name-based kill."""
    if proc.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        finally:
            if proc.poll() is None:
                proc.kill()
    else:
        proc.kill()
    proc.wait(timeout=10)


def execute(prefix, directory, timeout):
    command = prefix + [
        "build",
        "-j",
        "1",
        "-o",
        "threads=1",
        "-o",
        f"timeout={timeout}",
        "-o",
        "quick_and_dirty=false",
        "-D",
        ".",
    ]
    result = {"command": command, "exit_code": None, "timed_out": False}
    started = time.monotonic()
    process_options = {"start_new_session": True} if os.name == "posix" else {}
    if os.name == "nt":
        process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    with (
        (directory / "stdout.txt").open("xb") as out,
        (directory / "stderr.txt").open("xb") as err,
    ):
        try:
            proc = subprocess.Popen(
                command,
                cwd=directory,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                shell=False,
                **process_options,
            )
            try:
                result["exit_code"] = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                result["timed_out"] = True
                stop_owned_process(proc)
                result["exit_code"] = proc.returncode
        except (OSError, subprocess.SubprocessError) as error:
            result["execution_error"] = f"{type(error).__name__}: {error}"
    result["elapsed_seconds"] = time.monotonic() - started
    result["logs"] = {
        name: {
            "sha256": sha(directory / name),
            "bytes": (directory / name).stat().st_size,
        }
        for name in ["stdout.txt", "stderr.txt"]
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    launcher = parser.add_mutually_exclusive_group(required=True)
    launcher.add_argument(
        "--isabelle", help="Isabelle2025-2 executable or launcher path"
    )
    launcher.add_argument(
        "--isabelle-command-json",
        type=Path,
        help="JSON file containing a fixed argv prefix",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new directory; existing paths are refused",
    )
    parser.add_argument(
        "--timeout", type=int, default=90, choices=range(1, 181), metavar="1..180"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "schema_version": 1,
        "status": "FAIL",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "runner_sha256": sha(Path(__file__)),
        "timeout_seconds_per_control": args.timeout,
        "scope": "Selected diagnostic rejection controls; the positive source-bound audited build is a separate prerequisite.",
        "controls": [],
    }
    try:
        if args.isabelle_command_json:
            prefix = json.loads(args.isabelle_command_json.read_text(encoding="utf-8"))
            receipt["launcher_prefix_file_sha256"] = sha(args.isabelle_command_json)
        else:
            prefix = [args.isabelle]
        if (
            not isinstance(prefix, list)
            or not prefix
            or not all(
                isinstance(item, str) and item and "\0" not in item for item in prefix
            )
        ):
            raise ValueError(
                "launcher prefix must be a nonempty list of nonempty strings without NUL"
            )
        executable = shutil.which(prefix[0])
        if executable is None:
            raise FileNotFoundError("launcher executable was not found")
        prefix[0] = str(Path(executable).resolve())
        receipt["launcher_prefix"] = prefix
        receipt["launcher_executable_sha256"] = sha(Path(prefix[0]))
        base = (HERE / "Count_Endpoints.thy").read_bytes()
        audit = (HERE / "endpoint_audit.ML").read_bytes()
        receipt["input_sources"] = {
            name: sha(HERE / name)
            for name in ["Count_Endpoints.thy", "endpoint_audit.ML"]
        }
        if receipt["input_sources"] != {
            "Count_Endpoints.thy": hashlib.sha256(base).hexdigest(),
            "endpoint_audit.ML": hashlib.sha256(audit).hexdigest(),
        }:
            raise RuntimeError("input source changed during capture")
        token = uuid.uuid4().hex[:12]
        for name, theory in CONTROLS.items():
            directory = output / name
            directory.mkdir()
            row = {"name": name, "status": "FAIL", "reason": "not executed"}
            receipt["controls"].append(row)
            template = HERE / "controls" / (name + ".thy.in")
            template_bytes = template.read_bytes()
            source = template_bytes.decode("utf-8")
            original = 'ML_file "../../endpoint_audit.ML"'
            if source.count(original) != (0 if name == "false_endpoint" else 1):
                raise ValueError(f"unexpected ML_file shape in {name}")
            source = source.replace(original, 'ML_file "endpoint_audit.ML"')
            (directory / "genuine_Count_Endpoints.thy.source").write_bytes(base)
            if name != "changed_definition":
                (directory / "Count_Endpoints.thy").write_bytes(base)
            (directory / "endpoint_audit.ML").write_bytes(audit)
            (directory / (theory + ".thy")).write_bytes(source.encode("utf-8"))
            session = f"Bounded_Count_Control_{name}_{token}"
            (directory / "ROOT").write_text(
                f"session {session} = HOL +\n"
                f"  options [document = false, quick_and_dirty = false, threads = 1, timeout = {args.timeout}]\n"
                f"  theories\n    {theory}\n",
                encoding="utf-8",
                newline="\n",
            )
            row.update(
                session=session,
                template_sha256=hashlib.sha256(template_bytes).hexdigest(),
                sources={
                    file.name: sha(file)
                    for file in directory.iterdir()
                    if file.is_file()
                },
            )
            row.update(execute(prefix, directory, args.timeout))
            if row["sources"] != {
                file: sha(directory / file) for file in row["sources"]
            }:
                row["reason"] = "copied control source changed during execution"
                continue
            if any(log["bytes"] > MAX_LOG_BYTES for log in row["logs"].values()):
                row["reason"] = "diagnostic logs exceed classification size bound"
                continue
            stdout = (directory / "stdout.txt").read_text(
                encoding="utf-8", errors="replace"
            )
            stderr = (directory / "stderr.txt").read_text(
                encoding="utf-8", errors="replace"
            )
            ok, reason = classify(
                name, theory, row["exit_code"], row["timed_out"], stdout, stderr
            )
            row.update(
                status="PASS" if ok and "execution_error" not in row else "FAIL",
                reason=reason,
            )
        if receipt["input_sources"] != {
            name: sha(HERE / name) for name in receipt["input_sources"]
        }:
            raise RuntimeError("input source changed while controls ran")
        if len(receipt["controls"]) == 4 and all(
            row["status"] == "PASS" for row in receipt["controls"]
        ):
            receipt["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
    finally:
        receipt["completed_utc"] = datetime.now(timezone.utc).isoformat()
        (output / "receipt.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {"status": receipt["status"], "receipt": str(output / "receipt.json")}
        )
    )
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
