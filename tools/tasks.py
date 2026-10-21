"""Shared local and CI commands. Publication is deliberately a separate operation."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args: str, cwd: Path = ROOT) -> None:
    print("+ " + " ".join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def setup() -> None:
    run(
        PYTHON,
        "-m",
        "pip",
        "install",
        "--require-hashes",
        "-r",
        "requirements-dev.txt",
    )
    run(PYTHON, "-m", "pip", "install", "--no-build-isolation", "--no-deps", ".")


def lint() -> None:
    run(PYTHON, "-m", "ruff", "check", ".")
    run(PYTHON, "-m", "ruff", "format", "--check", ".")
    run(PYTHON, "tools/check_repository.py")


def test() -> None:
    run(
        PYTHON,
        "-m",
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
    )
    run(PYTHON, "-m", "coverage", "report", "--fail-under=95")


def build() -> None:
    run(PYTHON, "-m", "build", "--no-isolation")


def test_wheel(wheel: Path, destination: Path, tests: Path = ROOT / "tests") -> None:
    venv.EnvBuilder(with_pip=True).create(destination)
    executable = destination / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    run(executable, "-m", "pip", "install", "--no-index", "--no-deps", wheel)
    run(
        executable,
        "-I",
        "-B",
        "-c",
        'import bounded_counts; assert "site-packages" in bounded_counts.__file__; '
        'print("Installed package:", bounded_counts.__file__)',
    )
    run(executable, "-I", "-B", "-m", "unittest", "discover", "-s", tests, "-v")
    run(
        executable,
        "-I",
        "-B",
        "-m",
        "bounded_counts",
        "--degree",
        "3",
        "--strength",
        "1/2",
    )


def artifacts() -> None:
    if not hasattr(tarfile, "data_filter"):
        raise RuntimeError("Artifact verification requires Python 3.11.4 or newer")
    wheels = list((ROOT / "dist").glob("*.whl"))
    sources = list((ROOT / "dist").glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise RuntimeError(
            "Expected exactly one current wheel and one source distribution"
        )
    with tempfile.TemporaryDirectory(prefix="bounded-count-artifacts-") as temporary:
        location = Path(temporary)
        test_wheel(wheels[0], location / "wheel-env")
        extracted = location / "source"
        extracted.mkdir()
        with tarfile.open(sources[0], "r:gz") as archive:
            for entry in archive.getmembers():
                target = (extracted / entry.name).resolve()
                if not target.is_relative_to(extracted.resolve()) or not (
                    entry.isfile() or entry.isdir()
                ):
                    raise RuntimeError("Unsafe source distribution member")
            archive.extractall(extracted, filter="data")
        roots = list(extracted.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise RuntimeError("Unexpected source distribution layout")
        run(PYTHON, "tools/check_repository.py", cwd=roots[0])
        run(
            PYTHON,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            location / "rebuilt",
            cwd=roots[0],
        )
        rebuilt = list((location / "rebuilt").glob("*.whl"))
        if len(rebuilt) != 1:
            raise RuntimeError("Source distribution did not rebuild one wheel")
        test_wheel(rebuilt[0], location / "source-env", roots[0] / "tests")


def formal() -> None:
    run("lake", "exe", "cache", "get", cwd=ROOT / "lean")
    run("lake", "build", cwd=ROOT / "lean")
    run(PYTHON, "lean/verify.py", "--run", "local-check")
    run(PYTHON, "lean/extensions/d1/verify_stability.py", "--run", "local-check")
    run(
        PYTHON,
        "lean/extensions/d1-law/verify_law_bridge.py",
        "--suite",
        "research",
        "--run",
        "local-check",
    )


def release() -> None:
    lint()
    test()
    build()
    artifacts()
    print("Release checks passed. No package, tag or release was published.")


def main() -> None:
    commands = {
        name: globals()[name]
        for name in ("setup", "lint", "test", "build", "artifacts", "formal", "release")
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", nargs="?", default="help", choices=["help", *commands]
    )
    command = parser.parse_args().command
    if command == "help":
        print("Commands: setup, lint, test, build, artifacts, formal, release")
        print("Use a virtual environment; release runs local checks only.")
    else:
        commands[command]()


if __name__ == "__main__":
    main()
