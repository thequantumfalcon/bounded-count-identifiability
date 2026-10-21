"""Portable acceptance-gate tests; the compiler subprocess is mocked.

These tests do not validate Lean proofs. The formal CI job runs real Lean.
All mutations affect disposable copies of the extension and its configuration.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
INPUTS = (
    "lean/extensions/d1/CountD1Stability.lean",
    "lean/extensions/d1/verify_stability.py",
    "lean/extensions/d1/source_manifest.json",
    "lean/lake-manifest.json",
    "lean/lakefile.toml",
    "lean/lean-toolchain",
)
EXPECTED_ROOTS = (
    "CountD1Stability.squared_parameter_error_le",
    "CountD1Stability.parameter_error_le_sqrt",
    "CountD1Stability.parameter_error_from_cumulant",
    "CountD1Stability.background_error_le",
    "CountD1Stability.bounded_observation_error",
)


class StabilityVerifierTests(unittest.TestCase):
    def run_case(self, variant):
        with tempfile.TemporaryDirectory(
            prefix="stability-verifier-test-"
        ) as directory:
            root = Path(directory).resolve()
            for relative in INPUTS:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPOSITORY / relative, target)
            source, verifier, manifest, lock, config, toolchain = (
                root / relative for relative in INPUTS
            )
            compiler = root / "mock-compiler.bin"
            compiler.write_bytes(b"mocked, never executed")
            library = root / "library"
            library.mkdir()
            output = root / "build/stability/test"
            if variant == "source_tamper":
                source.write_bytes(source.read_bytes() + b"\n")
            elif variant == "schema":
                data = json.loads(manifest.read_text(encoding="utf-8"))
                data["schema_version"] = 2
                manifest.write_text(json.dumps(data), encoding="utf-8")
            elif variant == "reused_run":
                output.mkdir(parents=True)
                (output / "sentinel").write_bytes(b"keep")

            spec = importlib.util.spec_from_file_location("stability_fixture", verifier)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            roots = list(EXPECTED_ROOTS)
            if variant == "missing_root":
                roots.pop()
            elif variant == "duplicate_root":
                roots.append(roots[0])
            elif variant == "unexpected_root":
                roots[-1] = "Unrelated.theorem"
            axioms = "propext, Classical.choice, Quot.sound"
            if variant == "unexpected_axiom":
                axioms += ", Untrusted.custom"
            elif variant == "duplicate_axiom":
                axioms += ", propext"
            elif variant == "missing_axiom":
                axioms = "propext, Quot.sound"
            stdout = "\n".join(
                f"'{theorem}' depends on axioms: [{axioms}]" for theorem in roots
            ).encode()
            if variant == "warning":
                stdout += b"\nwarning: fixture warning\n"

            def fake_run(command, **kwargs):
                if command[-1] == "--version":
                    return subprocess.CompletedProcess(
                        command, 0, b"Lean (version 4.35.0, fixture)", b""
                    )
                self.assertIn("--trust=0", command)
                self.assertEqual(command[-1], source.name)
                target = Path(command[command.index("-o") + 1])
                self.assertEqual(target, output / "CountD1Stability.olean")
                if variant != "no_output":
                    target.write_bytes(b"" if variant == "empty_output" else b"mock")
                changed = {
                    "source_changed": source,
                    "manifest_changed": manifest,
                    "verifier_changed": verifier,
                    "lock_changed": lock,
                    "config_changed": config,
                    "toolchain_changed": toolchain,
                }.get(variant)
                if changed is not None:
                    changed.write_bytes(changed.read_bytes() + b"\n")
                if variant == "timeout":
                    raise subprocess.TimeoutExpired(command, 240, output=stdout)
                return subprocess.CompletedProcess(
                    command, 1 if variant == "nonzero" else 0, stdout, b""
                )

            argv = [
                str(verifier),
                "--mode",
                "existing-cache",
                "--lean-executable",
                str(compiler),
                "--library",
                str(library),
                "--run",
                "../escape" if variant == "path_escape" else "test",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(module.subprocess, "run", side_effect=fake_run),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                try:
                    code = module.main()
                except SystemExit as error:
                    code = error.code
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    subprocess.SubprocessError,
                ):
                    code = 1
            receipt_path = output / "result.json"
            receipt = (
                json.loads(receipt_path.read_text(encoding="utf-8"))
                if receipt_path.is_file()
                else None
            )
            if variant == "reused_run":
                self.assertEqual((output / "sentinel").read_bytes(), b"keep")
            if variant == "positive":
                self.assertEqual(code, 0)
                self.assertEqual(receipt["status"], "PASS")
                self.assertTrue(all(receipt["checks"].values()))
            else:
                self.assertNotEqual(code, 0)
                if receipt is not None:
                    self.assertEqual(receipt["status"], "FAIL")
            return receipt

    def test_mock_positive_control(self):
        self.run_case("positive")

    def test_source_identity_and_schema(self):
        for variant in ("source_tamper", "schema"):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_exact_theorem_roots_required(self):
        for variant in ("missing_root", "duplicate_root", "unexpected_root"):
            with self.subTest(variant=variant):
                receipt = self.run_case(variant)
                self.assertFalse(receipt["checks"]["exact_five_unique_printed_roots"])

    def test_exact_axiom_records_required(self):
        for variant in ("missing_axiom", "duplicate_axiom", "unexpected_axiom"):
            with self.subTest(variant=variant):
                receipt = self.run_case(variant)
                self.assertFalse(receipt["checks"]["printed_axioms_allowed"])

    def test_success_requires_fresh_nonempty_output(self):
        for variant in ("no_output", "empty_output"):
            with self.subTest(variant=variant):
                receipt = self.run_case(variant)
                self.assertFalse(receipt["checks"]["fresh_nonempty_olean"])

    def test_input_mutations_fail_even_with_mock_success(self):
        for name in ("source", "manifest", "verifier", "lock", "config", "toolchain"):
            with self.subTest(input=name):
                self.run_case(name + "_changed")

    def test_bad_process_results_fail(self):
        for variant in ("nonzero", "timeout", "warning"):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_fresh_local_output_directory_required(self):
        for variant in ("reused_run", "path_escape"):
            with self.subTest(variant=variant):
                self.run_case(variant)


if __name__ == "__main__":
    unittest.main()
