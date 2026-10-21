"""Run bounded Atheris checks and preserve source-bound execution evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from bounded_counts import core
import bounded_counts


HERE = Path(__file__).resolve().parent
FAULT_MARKER = "BCI_DELIBERATE_FAULT_DETECTED"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output, seconds=60, runs=10000, seed=20261021):
    if platform.system() != "Linux" or version("atheris") != "3.1.0":
        raise ValueError("use Linux and the hash-pinned Atheris 3.1.0 wheels")
    if not 1 <= seconds <= 90 or not 1 <= runs <= 10000 or not 1 <= seed < 2**31:
        raise ValueError("seconds must be 1..90, runs 1..10000, seed 1..2**31-1")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    corpus = output / "corpus"
    corpus.mkdir()
    crashes = output / "crashes"
    crashes.mkdir()
    control = output / "fault-control"
    control.mkdir()
    entries = json.loads((HERE / "corpus.json").read_text(encoding="utf-8"))
    for entry in entries:
        data = bytes.fromhex(entry["hex"])
        if len(data) > 17:
            raise ValueError("seed corpus exceeds the 17-byte input limit")
        (corpus / hashlib.sha256(data).hexdigest()).write_bytes(data)
    paths = {
        "driver": Path(__file__).resolve(),
        "target": HERE / "atheris_target.py",
        "oracle": HERE / "exact_counts.py",
        "corpus": HERE / "corpus.json",
        "requirements": HERE / "requirements.txt",
        "installed_core": Path(core.__file__).resolve(),
        "installed_package_init": Path(bounded_counts.__file__).resolve(),
    }
    sources = {name: digest(path) for name, path in paths.items()}
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    base = [sys.executable, "-B", str(HERE / "atheris_target.py")]
    limits = [
        "-max_len=17",
        "-timeout=5",
        "-rss_limit_mb=512",
        "-malloc_limit_mb=128",
        f"-seed={seed}",
        "-print_final_stats=1",
    ]
    record = {
        "status": "FAIL",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "bounded Atheris coverage-guided differential fuzzing",
        "python": platform.python_version(),
        "atheris": version("atheris"),
        "limits": {
            "seconds": seconds,
            "runs": runs,
            "input_bytes": 17,
            "rss_mb": 512,
            "per_input_timeout_seconds": 5,
            "seed": seed,
        },
        "source_sha256": sources,
        "processes": [],
        "scope": "Finite software checks sharing the existing exact oracle; not formal software verification, mathematical proof, physical validation or independent human review.",
    }

    def execute(label, arguments, timeout):
        command = base + arguments
        stdout, stderr = output / f"{label}.stdout.txt", output / f"{label}.stderr.txt"
        attempt = {"label": label, "arguments": arguments, "timeout_seconds": timeout}
        record["processes"].append(attempt)
        try:
            with stdout.open("wb") as out, stderr.open("wb") as err:
                completed = subprocess.run(
                    command,
                    stdout=out,
                    stderr=err,
                    env=env,
                    timeout=timeout,
                    check=False,
                )
            attempt["exit_code"] = completed.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            attempt["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            attempt["stdout_sha256"] = digest(stdout)
            attempt["stderr_sha256"] = digest(stderr)
        return completed.returncode, (
            stdout.read_text(encoding="utf-8", errors="replace")
            + "\n"
            + stderr.read_text(encoding="utf-8", errors="replace")
        )

    try:
        code, log = execute(
            "fuzz",
            [
                str(corpus),
                f"-max_total_time={seconds}",
                f"-runs={runs}",
                f"-artifact_prefix={crashes}/",
            ]
            + limits,
            seconds + 45,
        )
        if code != 0 or not re.search(r"cov: [1-9][0-9]*", log):
            raise RuntimeError("fuzz run failed or reported no positive coverage")
        if "Instrumenting bounded_counts.core" not in log:
            raise RuntimeError("package core bytecode instrumentation was not observed")
        record["package_instrumentation_observed"] = True
        if list(crashes.iterdir()):
            raise RuntimeError("normal run wrote a failure artifact")
        record["final_stats"] = {
            name: int(value)
            for name, value in re.findall(r"stat::([a-z_]+):\s+([0-9]+)", log)
        }
        if record["final_stats"].get("number_of_executed_units", 0) <= 0:
            raise RuntimeError("engine did not report any executed inputs")
        code, fault_log = execute(
            "fault",
            ["--fault-control", "-runs=1", f"-artifact_prefix={control}/"] + limits,
            30,
        )
        fault_files = sorted(control.glob("crash-*"))
        if code != 77 or FAULT_MARKER not in fault_log or len(fault_files) != 1:
            raise RuntimeError("engine did not capture the injected API fault")
        code, _ = execute("replay", [str(fault_files[0]), "-runs=1"] + limits, 30)
        if code != 0:
            raise RuntimeError("control input also failed against the genuine API")
        record["fault_detected_and_genuine_replay_passed"] = True
        record["sources_unchanged"] = sources == {
            name: digest(path) for name, path in paths.items()
        }
        if not record["sources_unchanged"]:
            raise RuntimeError("source changed during the check")
        record["status"] = "PASS"
    except Exception as exc:
        record["failure"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        record["artifacts"] = [
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
            for path in sorted(output.rglob("*"))
            if path.is_file()
        ]
        (output / "result.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--runs", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261021)
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.seconds, args.runs, args.seed), indent=2))


if __name__ == "__main__":
    main()
