"""Bounded, offline checks for this repository or a freshly extracted sdist.

Uses only Python 3.11's standard library. It checks common Markdown links,
declared metadata, exact source bindings and explicit exclusion/pinning patterns.
It is not a general Markdown/YAML parser, secret scanner, dependency audit,
proof checker or assessment of scientific truth. No network access is performed.

Run ``python tools/check_repository.py`` or add ``--json`` for a concise report.
``--self-test`` exercises the checker's parsing and rejection controls without
auditing the assembling repository. Optional ``--private-token`` values are
checked literally but never echoed in diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import unquote, urlsplit

PERSONA = "The Quantum Falcon"
MODULES = {
    "CountSeriesCore.lean",
    "CountLawEncoding.lean",
    "CountIdentification.lean",
    "CountPoissonChannel.lean",
    "CountObservedIdentification.lean",
    "CountSharpness.lean",
}
LAKE_PACKAGES = {
    "mathlib",
    "plausible",
    "LeanSearchClient",
    "importGraph",
    "proofwidgets",
    "aesop",
    "Qq",
    "batteries",
    "Cli",
}
COMMON_REQUIRED = {
    "README.md",
    "LICENSE.txt",
    "NOTICE.md",
    "PROVENANCE.md",
    "CITATION.cff",
    "CHANGELOG.md",
    "pyproject.toml",
    "MANIFEST.in",
    "requirements-dev.lock",
    "Makefile",
    "ruff.toml",
    ".coveragerc",
    "docs/theorem.md",
    "docs/claims.md",
    "docs/roadmap.md",
    "docs/references.md",
    "docs/reproduction.md",
    "evidence/README.md",
    "src/bounded_counts/__init__.py",
    "src/bounded_counts/core.py",
    "src/bounded_counts/__main__.py",
    "tests/test_exact_counts.py",
    "examples/d1_projection_sage.py",
    "tools/tasks.py",
    "tools/check_repository.py",
    "lean/README.md",
    "lean/verify.py",
    "lean/lean-toolchain",
    "lean/lakefile.toml",
    "lean/lake-manifest.json",
    "lean/source_manifest.json",
    "lean/third_party/provenance.json",
} | {"lean/" + name for name in MODULES}
REPOSITORY_REQUIRED = {
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "AGENTS.md",
    ".github/CODE_OF_CONDUCT.md",
    ".github/CODEOWNERS",
    ".github/CONTRIBUTING.md",
    ".github/SECURITY.md",
    ".github/SUPPORT.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/correction.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/dependency-review.yml",
    ".github/workflows/scorecard.yml",
}
ARTIFACT_DIRS = {
    ".venv",
    "venv",
    ".lake",
    ".verification",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "build",
    "dist",
    "verification-output",
    "node_modules",
}
ARTIFACT_SUFFIXES = {".pyc", ".pyo", ".olean", ".ilean", ".trace", ".whl"}
HEX40 = re.compile(r"[0-9a-fA-F]{40}\Z")
HEX64 = re.compile(r"[0-9a-fA-F]{64}\Z")
LEAN_ADMISSIONS = re.compile(r"\b(?:sorry|admit|sorryAx|native_decide|axiom)\b")
PRIVATE_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/]"),
    re.compile(r"/mnt/[A-Za-z]/(?:Users|Documents and Settings)/", re.I),
    re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/"),
    re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_lean_comments_and_strings(text: str) -> str:
    """Small lexical filter including nested Lean block comments."""
    output = []
    index = depth = 0
    while index < len(text):
        pair = text[index : index + 2]
        if depth:
            if pair == "/-":
                depth += 1
                index += 2
            elif pair == "-/":
                depth -= 1
                index += 2
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif pair == "/-":
            depth = 1
            output.append(" ")
            index += 2
        elif pair == "--":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            output.append(" ")
        elif text[index] == '"':
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                elif text[index] == '"':
                    index += 1
                    break
                else:
                    index += 1
            output.append(" ")
        else:
            output.append(text[index])
            index += 1
    return "".join(output)


def prose_without_code(text: str) -> str:
    result = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            current = marker.group(1)
            if fence is None:
                fence = current
            elif current[0] == fence[0] and len(current) >= len(fence):
                fence = None
            result.append("")
        elif fence is None:
            result.append(line)
    prose = re.sub(r"<!--.*?-->", "", "\n".join(result), flags=re.S)
    return re.sub(r"(`+).*?\1", "", prose)


def markdown_targets(text: str) -> tuple[list[str], list[str]]:
    """Common inline links/images and explicit reference links; no anchor check."""
    prose = prose_without_code(text)
    definitions = {}
    targets = []
    missing_references = []
    for match in re.finditer(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", prose, re.M):
        key = " ".join(match.group(1).lower().split())
        target = match.group(2).strip("<>")
        definitions[key] = target
        targets.append(target)
    for match in re.finditer(r"\[([^\]]*)\]\[([^\]]*)\]", prose):
        key = " ".join((match.group(2) or match.group(1)).lower().split())
        if key in definitions:
            targets.append(definitions[key])
        else:
            missing_references.append(key)
    for match in re.finditer(r"\[[^\]\n]*\]\(", prose):
        start = match.end()
        if start < len(prose) and prose[start] == "<":
            end = prose.find(">", start + 1)
            if end >= 0:
                targets.append(prose[start + 1 : end])
            continue
        index, depth = start, 1
        while index < len(prose) and depth:
            char = prose[index]
            if char == "\\":
                index += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            if depth:
                index += 1
        if depth == 0:
            # Whitespace introduces an optional title in ordinary inline syntax.
            target = prose[start:index].strip().split(maxsplit=1)
            if target:
                targets.append(target[0])
    return targets, missing_references


def local_link_problem(root: Path, document: Path, target: str) -> str | None:
    if not target or target.startswith(("#", "?", "//")):
        return None
    if re.match(r"(?i)^[a-z]:[\\/]", target) or target.lower().startswith("file:"):
        return "local filesystem link"
    parsed = urlsplit(target)
    if parsed.scheme:
        return None  # Includes http(s), mailto and other explicit URI schemes.
    path = unquote(parsed.path)
    if not path:
        return None
    destination = (
        (root / path.lstrip("/")) if path.startswith("/") else (document.parent / path)
    )
    destination = destination.resolve()
    if not destination.is_relative_to(root.resolve()):
        return "relative link escapes the repository"
    if not destination.exists():
        return "relative link target does not exist"
    return None


def parse_hashed_lock(text: str) -> dict[str, str]:
    """Strict project lock syntax: exact pins and one or more SHA256 hashes."""
    logical = re.sub(r"\\\r?\n", " ", text)
    entries = {}
    for line in logical.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(
            r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)\s+(.+)", line
        )
        if not match:
            raise ValueError(
                "development lock has a non-exact or unsupported requirement"
            )
        name, version, hashes = match.groups()
        name = re.sub(r"[-_.]+", "-", name).lower()
        if name in entries:
            raise ValueError("development lock repeats a package")
        if not all(
            re.fullmatch(r"--hash=sha256:[0-9a-fA-F]{64}", token)
            for token in hashes.split()
        ):
            raise ValueError(
                "development lock has an invalid hash or unsupported option"
            )
        entries[name] = version
    if not entries:
        raise ValueError("development lock is empty")
    return entries


def action_is_pinned(value: str) -> bool:
    if value.startswith("./"):
        return True  # Existence is checked separately against the same tree.
    if value.startswith("docker://"):
        return bool(re.fullmatch(r"docker://[^\s@]+@sha256:[0-9a-fA-F]{64}", value))
    return bool(
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-fA-F]{40}", value)
    )


def inventory_files(root: Path, mode: str) -> tuple[list[Path], str]:
    if mode == "repository" and (root / ".git").exists():
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ],
                capture_output=True,
                check=False,
                timeout=30,
            )
            if result.returncode == 0:
                paths = {
                    root / os.fsdecode(value)
                    for value in result.stdout.split(b"\0")
                    if value
                }
                return sorted(paths), "git tracked plus untracked nonignored files"
        except (OSError, subprocess.TimeoutExpired):
            pass
    paths = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        # A fresh sdist is audited strictly. Repository fallback ignores ordinary
        # local build/cache directories because Git's exclusion engine is absent.
        excluded = {".git"} | (ARTIFACT_DIRS if mode == "repository" else set())
        dirs[:] = [name for name in dirs if name not in excluded]
        paths.extend(Path(directory) / name for name in files)
    return (
        sorted(paths),
        "filesystem fallback (no Git index); fresh sdist strictness"
        if mode == "sdist"
        else "filesystem fallback excluding local build/cache directories",
    )


def audit(root: Path, mode: str, private_tokens: list[str]) -> dict:
    root = root.resolve()
    errors = []
    counts = {"markdown_links": 0, "lean_sources": 0, "workflow_uses": 0}

    def fail(message):
        errors.append(message)

    def read(relative):
        path = root / relative
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    def load_json(relative):
        try:
            return json.loads(read(relative))
        except (ValueError, OSError) as exc:
            fail(f"{relative}: cannot read JSON ({type(exc).__name__})")
            return {}

    required = COMMON_REQUIRED | (
        REPOSITORY_REQUIRED if mode == "repository" else set()
    )
    for name in sorted(required):
        if not (root / name).is_file():
            fail(f"missing required file: {name}")
    files, selection = inventory_files(root, mode)
    for path in files:
        name = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            fail(f"unsupported symlink or escaped path: {name}")
            continue
        if not path.is_file():
            fail(f"listed file is absent: {name}")
            continue
        if (
            any(part in ARTIFACT_DIRS for part in path.relative_to(root).parts)
            or path.suffix in ARTIFACT_SUFFIXES
        ):
            fail(f"generated artifact included in audited source files: {name}")
        if name in {".coverage", "coverage.xml", ".env"} or name.endswith(
            (".tar.gz", ".zip")
        ):
            fail(f"generated/archive/private artifact included in source files: {name}")
        if mode == "repository" and any(
            part.endswith(".egg-info") for part in path.relative_to(root).parts
        ):
            fail(f"build metadata included in repository files: {name}")
        if path.suffix == ".lean" and name not in {
            "lean/" + module for module in MODULES
        }:
            fail(f"Lean source is outside the six-module manifest: {name}")
        raw = path.read_bytes()
        if b"\x00" in raw:
            fail(f"unexpected binary file in this source-only artifact: {name}")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            fail(f"non-UTF-8 source file: {name}")
            continue
        if any(pattern.search(text) for pattern in PRIVATE_PATTERNS):
            fail(f"private-path or private-key pattern found: {name}")
        if any(
            token and token.casefold() in text.casefold() for token in private_tokens
        ):
            fail(f"additional private identifier found (value redacted): {name}")
        if path.suffix.lower() == ".md":
            targets, missing = markdown_targets(text)
            counts["markdown_links"] += len(targets)
            for reference in missing:
                fail(f"{name}: unresolved Markdown reference [{reference}]")
            for target in targets:
                problem = local_link_problem(root, path, target)
                if problem:
                    fail(f"{name}: {problem}")

    try:
        metadata = tomllib.loads(read("pyproject.toml"))
        project = metadata.get("project", {})
        if project.get("name") != "bounded-count-identifiability":
            fail("pyproject.toml: wrong project name")
        if project.get("authors") != [{"name": PERSONA}]:
            fail("pyproject.toml: expected the sole declared author persona")
        if project.get("maintainers", [{"name": PERSONA}]) != [{"name": PERSONA}]:
            fail("pyproject.toml: unexpected declared maintainer identity")
        if project.get("license") != "MIT" or project.get("license-files") != [
            "LICENSE.txt"
        ]:
            fail("pyproject.toml: expected MIT SPDX license and LICENSE.txt")
        if project.get("readme") != "README.md" or project.get("dependencies") != []:
            fail("pyproject.toml: expected README.md and no runtime dependencies")
        lock = parse_hashed_lock(read("requirements-dev.lock"))
        build_system = metadata.get("build-system", {})
        build_requirements = build_system.get("requires", [])
        if (
            build_system.get("build-backend") != "setuptools.build_meta"
            or not build_requirements
        ):
            fail("pyproject.toml: expected setuptools backend and explicit build pins")
        for requirement in build_requirements:
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s]+)", requirement)
            if not match or lock.get(
                re.sub(r"[-_.]+", "-", match.group(1)).lower()
            ) != match.group(2):
                fail(
                    "pyproject.toml: build dependency is not an exact matching development-lock pin"
                )
    except (ValueError, TypeError) as exc:
        fail(f"package metadata/lock parse failed ({type(exc).__name__}): {exc}")

    citation = read("CITATION.cff")
    author_block = re.search(r"^authors:\s*\n((?:[ \t]+.*\n|\s*\n)+)", citation, re.M)
    names = (
        re.findall(r"^\s*-\s*name:\s*['\"]?([^'\"\n]+)", author_block.group(1), re.M)
        if author_block
        else []
    )
    if names != [PERSONA] or (
        author_block and len(re.findall(r"^\s*-\s", author_block.group(1), re.M)) != 1
    ):
        fail("CITATION.cff: expected one author using the declared persona")
    if not re.search(
        r"Copyright \(c\) \d{4}(?:-\d{4})? " + re.escape(PERSONA), read("LICENSE.txt")
    ):
        fail("LICENSE.txt: missing original-work copyright for the declared persona")

    manifest = load_json("lean/source_manifest.json").get("sources", {})
    if set(manifest) != MODULES:
        fail("lean/source_manifest.json: expected exactly six named proof modules")
    for name in sorted(MODULES):
        path = root / "lean" / name
        entry = manifest.get(name, {})
        if not path.is_file():
            continue
        counts["lean_sources"] += 1
        if not isinstance(entry, dict) or not HEX64.fullmatch(
            str(entry.get("sha256", ""))
        ):
            fail(f"lean/source_manifest.json: invalid hash entry for {name}")
        elif sha256(path) != entry[
            "sha256"
        ].lower() or path.stat().st_size != entry.get("bytes"):
            fail(f"lean/{name}: source hash or byte count differs from the manifest")
        code = strip_lean_comments_and_strings(path.read_text(encoding="utf-8"))
        if LEAN_ADMISSIONS.search(code):
            fail(f"lean/{name}: forbidden proof-admission/axiom/native-decide token")
        if re.search(r"\bset_option\s+debug\.skipKernelTC\s+true\b", code):
            fail(f"lean/{name}: kernel-check skipping option")

    lake = load_json("lean/lake-manifest.json")
    packages = lake.get("packages", [])
    package_map = {
        item.get("name"): item for item in packages if isinstance(item, dict)
    }
    if len(packages) != len(LAKE_PACKAGES) or set(package_map) != LAKE_PACKAGES:
        fail("lean/lake-manifest.json: expected the complete nine-package lock")
    if lake.get("fixedToolchain") is not True:
        fail("lean/lake-manifest.json: toolchain is not marked fixed")
    for name, package in package_map.items():
        if package.get("type") != "git" or not HEX40.fullmatch(
            str(package.get("rev", ""))
        ):
            fail(f"lean/lake-manifest.json: non-pinned Git revision for {name}")
        if not str(package.get("url", "")).startswith("https://github.com/"):
            fail(
                f"lean/lake-manifest.json: unexpected non-HTTPS/local dependency URL for {name}"
            )
    try:
        lake_config = tomllib.loads(read("lean/lakefile.toml"))
        requirements = lake_config.get("require", [])
        if (
            len(requirements) != 1
            or requirements[0].get("name") != "mathlib"
            or requirements[0].get("rev") != package_map.get("mathlib", {}).get("rev")
        ):
            fail("lean/lakefile.toml: mathlib declaration does not match the lock")
        libraries = lake_config.get("lean_lib", [])
        if len(libraries) != 1 or "--trust=0" not in libraries[0].get(
            "moreLeanArgs", []
        ):
            fail("lean/lakefile.toml: expected trust=0 for the proof library")
    except (ValueError, TypeError) as exc:
        fail(f"lean/lakefile.toml: cannot parse configuration ({type(exc).__name__})")
    if not re.fullmatch(
        r"leanprover/lean4:v\d+\.\d+\.\d+", read("lean/lean-toolchain").strip()
    ):
        fail("lean/lean-toolchain: expected a fixed released Lean version")
    provenance = load_json("lean/third_party/provenance.json")
    notices = provenance.get("packages", [])
    if (
        len(notices) != len(LAKE_PACKAGES)
        or {item.get("name") for item in notices} != LAKE_PACKAGES
    ):
        fail(
            "lean/third_party/provenance.json: dependency notices do not cover the lock"
        )
    for item in notices:
        name = item.get("name")
        if item.get("revision") != package_map.get(name, {}).get("rev"):
            fail(f"third-party notice revision differs from lock: {name}")
        relative = item.get("license_file", "")
        path = (root / "lean" / relative).resolve()
        if (
            not path.is_relative_to(root / "lean")
            or not path.is_file()
            or sha256(path) != item.get("license_sha256")
        ):
            fail(f"third-party license hash/path does not match notice: {name}")

    workflows = sorted((root / ".github/workflows").glob("*.yml")) + sorted(
        (root / ".github/workflows").glob("*.yaml")
    )
    if mode == "repository" and not workflows:
        fail("no repository CI workflow found")
    for path in workflows:
        for match in re.finditer(
            r"^\s*(?:-\s*)?uses:\s*(.*?)\s*$", path.read_text(encoding="utf-8"), re.M
        ):
            counts["workflow_uses"] += 1
            value = match.group(1).split("#", 1)[0].strip().strip("'\"")
            if not action_is_pinned(value):
                fail(
                    f"{path.relative_to(root).as_posix()}: external action is not SHA-pinned"
                )
            elif value.startswith("./") and local_link_problem(
                root, root / "README.md", value
            ):
                fail(
                    f"{path.relative_to(root).as_posix()}: local action/workflow target is missing or outside the tree"
                )
    if mode == "repository":
        ignores = set(read(".gitignore").splitlines())
        for required_ignore in [
            "__pycache__/",
            "*.py[cod]",
            "*.egg-info/",
            ".venv/",
            "build/",
            "dist/",
            ".lake/",
            "*.olean",
            "*.ilean",
        ]:
            if required_ignore not in ignores:
                fail(
                    f".gitignore: missing required artifact exclusion {required_ignore}"
                )
    return {
        "status": "PASS" if not errors else "FAIL",
        "mode": mode,
        "file_selection": selection,
        "files_scanned": len(files),
        "checks": counts,
        "errors": errors,
        "limits": [
            "Offline bounded checks; not a complete security, personal-information or scientific audit.",
            "Common Markdown syntax/file targets only; fragments, shortcut references, HTML links and external URLs are not validated.",
            "Workflow checks inspect conventional uses lines, not full YAML semantics or action behavior.",
            "Pinned revisions and source hashes bind declared artifacts; no dependency is fetched and no Lean proof is compiled here.",
        ],
    }


def self_test() -> dict:
    lean = '/- sorry /- admit -/ -/\n theorem ok : True := by trivial\n-- axiom\n#print axioms ok\n#eval "sorryAx"'
    assert not LEAN_ADMISSIONS.search(strip_lean_comments_and_strings(lean))
    for token in ("sorry", "admit", "sorryAx", "native_decide", "axiom"):
        assert LEAN_ADMISSIONS.search(strip_lean_comments_and_strings("by " + token))
    targets, missing = markdown_targets(
        '[a](docs/a.md#x) [b][ref]\n[ref]: <with space.md> "title"\n```\n[x](ignored.md)\n```'
    )
    assert set(targets) == {"docs/a.md#x", "with space.md"} and not missing
    assert markdown_targets("[a][missing]")[1] == ["missing"]
    assert action_is_pinned("actions/checkout@" + "a" * 40)
    assert action_is_pinned("docker://example/image@sha256:" + "b" * 64)
    assert not action_is_pinned("actions/checkout@v4")
    assert not action_is_pinned("actions/checkout@" + "a" * 39)
    assert parse_hashed_lock("example==1.2.3 --hash=sha256:" + "c" * 64) == {
        "example": "1.2.3"
    }
    for bad in ["example>=1", "example==1.2.3", "example==1 --hash=sha256:abc"]:
        try:
            parse_hashed_lock(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid lock input accepted")
    with tempfile.TemporaryDirectory(prefix="bounded-repository-audit-") as directory:
        root = Path(directory).resolve()
        (root / "with space.md").write_text("example", encoding="utf-8")
        document = root / "README.md"
        for target in [
            "with%20space.md#part",
            "https://example.invalid/x",
            "mailto:example@example.invalid",
            "#heading",
        ]:
            assert local_link_problem(root, document, target) is None
        for target in ["missing.md", "../escape.md", "file:///example"]:
            assert local_link_problem(root, document, target) is not None
    return {
        "status": "PASS",
        "scope": "parser/rejection controls only; repository not audited",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--mode", choices=["auto", "repository", "sdist"], default="auto"
    )
    parser.add_argument(
        "--private-token",
        action="append",
        default=[],
        help="additional private literal to reject; value is not printed",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        mode = (
            ("sdist" if (args.root / "PKG-INFO").is_file() else "repository")
            if args.mode == "auto"
            else args.mode
        )
        result = audit(args.root, mode, args.private_token)
    if args.json or args.self_test:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Repository audit: {result['status']} ({result['mode']}; {result['files_scanned']} files)"
        )
        for error in result["errors"]:
            print("- " + error)
        print(
            "Bounded offline checks only; no proof compilation or complete security audit."
        )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
