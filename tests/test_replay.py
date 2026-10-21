"""Replay-runner rejection controls; actual Lean replay runs in formal CI.

The proof-binding layer is replaced by a deterministic fixture here. Its audit
and receipt controls are covered by the law-verifier tests, while these cases
exercise replay process outcomes, evidence preservation and input mutation.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY = Path(__file__).resolve().parents[1]


class ReplayTests(unittest.TestCase):
    def load_part_policy(self):
        spec = importlib.util.spec_from_file_location(
            "replay_part_policy_fixture", REPOSITORY / "lean/replay.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.reject_unbound_parts

    def test_unbound_split_objects_rejected_without_modification(self):
        reject_parts = self.load_part_policy()
        for suffix in (".olean.server", ".olean.private"):
            for contents in (b"", b"unbound compiled declarations"):
                with self.subTest(suffix=suffix, contents=contents):
                    with tempfile.TemporaryDirectory(prefix="replay-parts-") as temp:
                        objects = Path(temp)
                        main = objects / "CountSharpness.olean"
                        main.write_bytes(b"bound main object")
                        part = objects / ("CountSharpness" + suffix)
                        part.write_bytes(contents)
                        with self.assertRaisesRegex(ValueError, "Unbound split"):
                            reject_parts(objects, "CountSharpness")
                        self.assertEqual(part.read_bytes(), contents)
                        self.assertEqual(main.read_bytes(), b"bound main object")

    def test_split_object_directories_also_fail_closed(self):
        reject_parts = self.load_part_policy()
        for suffix in (".olean.server", ".olean.private"):
            with self.subTest(suffix=suffix):
                with tempfile.TemporaryDirectory(prefix="replay-parts-") as temp:
                    objects = Path(temp)
                    part = objects / ("CountSharpness" + suffix)
                    part.mkdir()
                    with self.assertRaisesRegex(ValueError, "Unbound split"):
                        reject_parts(objects, "CountSharpness")
                    self.assertTrue(part.is_dir())

    def test_legacy_objects_and_other_modules_do_not_trigger_part_rejection(self):
        reject_parts = self.load_part_policy()
        with tempfile.TemporaryDirectory(prefix="replay-parts-") as temp:
            objects = Path(temp)
            (objects / "CountSharpness.olean").write_bytes(b"bound main object")
            (objects / "CountSharpness.ilean").write_bytes(b"editor information")
            (objects / "Unrelated.olean.server").write_bytes(b"another module")
            (objects / "Unrelated.olean.private").write_bytes(b"another module")
            reject_parts(objects, "CountSharpness")

    def run_case(self, variant: str) -> None:
        with tempfile.TemporaryDirectory(prefix="replay-test-") as temporary:
            root = Path(temporary).resolve()
            paths = [
                *REPOSITORY.glob("lean/*.py"),
                *REPOSITORY.glob("lean/*.lean"),
                *REPOSITORY.glob("lean/*.json"),
                *REPOSITORY.glob("lean/*.toml"),
                REPOSITORY / "lean/lean-toolchain",
                *REPOSITORY.glob("lean/extensions/*/*.lean"),
                *REPOSITORY.glob("lean/extensions/*/source_manifest.json"),
                REPOSITORY / "lean/extensions/d1-law/verify_law_bridge.py",
            ]
            for source in paths:
                destination = root / source.relative_to(REPOSITORY)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            runner = root / "lean/replay.py"
            spec = importlib.util.spec_from_file_location("replay_fixture", runner)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            compiler = root / "bin/lean.exe"
            compiler.parent.mkdir()
            compiler.write_bytes(b"fixture compiler")
            checker = compiler.with_name("leanchecker.exe")
            if variant != "missing_checker":
                checker.write_bytes(b"fixture checker")
            library = root / "dependencies"
            library.mkdir()
            object_path = root / "bound-object.olean"
            object_path.write_bytes(b"fixture object")
            inputs = module.DRIVER.source_inputs("research")
            inputs.update({"compiler": compiler, "fixture_object": object_path})
            output = root / "build/replay/check"
            if variant == "existing_output":
                output.mkdir(parents=True)
                (output / "sentinel").write_bytes(b"preserved")
            modules = [
                *module.AUDIT.CORE,
                *module.AUDIT.ROOTS,
                *module.AUDIT.RESEARCH_ROOTS,
            ]
            binding_calls = 0

            def bind_proofs(proof_run, selected_compiler):
                nonlocal binding_calls
                binding_calls += 1
                self.assertEqual(proof_run, "proof")
                self.assertEqual(selected_compiler, compiler)
                if variant == "bad_binding" or (
                    variant == "late_bad_binding" and binding_calls == 2
                ):
                    raise ValueError("Fixture proof binding failed")
                return inputs.copy()

            def resolve_environment(args):
                if variant == "environment_runner_mutation":
                    runner.write_bytes(runner.read_bytes() + b"\n")
                elif variant == "environment_policy_mutation":
                    helper = root / "lean/proof_audit.py"
                    helper.write_bytes(helper.read_bytes() + b"\n")
                return compiler, [library]

            def run(command, **kwargs):
                name = command[-1]
                self.assertEqual(command, [str(checker), "--verbose", name])
                self.assertIn(name, modules)
                self.assertEqual(kwargs["cwd"], output)
                self.assertEqual(
                    kwargs["env"]["LEAN_PATH"].split(os.pathsep),
                    [
                        str(root / "build/research/proof"),
                        str(root / "lean/.verification/d1-law-research-proof"),
                        str(library),
                    ],
                )
                stdout = ("replaying " + name + "\n").encode()
                stderr = b""
                if variant == "timeout":
                    raise subprocess.TimeoutExpired(command, 240, output=stdout)
                if variant == "empty_output":
                    stdout = b""
                elif variant == "wrong_module":
                    stdout = b"replaying Unrelated\n"
                elif variant == "extra_output":
                    stdout += b"unexpected output\n"
                elif variant == "stderr":
                    stderr = b"warning: fixture warning"
                elif variant == "object_mutation":
                    object_path.write_bytes(b"changed during replay")
                elif variant == "checker_mutation":
                    checker.write_bytes(b"changed during replay")
                elif variant == "prior_log_mutation" and name == modules[-1]:
                    (output / (modules[0] + ".stdout.txt")).write_bytes(b"changed")
                return subprocess.CompletedProcess(
                    command, 1 if variant == "nonzero" else 0, stdout, stderr
                )

            argv = [
                str(runner),
                "--proof-run",
                "../escape" if variant == "proof_escape" else "proof",
                "--run",
                "../escape" if variant == "output_escape" else "check",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(module.DRIVER, "resolve_environment", resolve_environment),
                patch.object(module, "bind_proofs", bind_proofs),
                patch.object(module.subprocess, "run", run),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                try:
                    code = module.main()
                except (OSError, ValueError, KeyError, TypeError):
                    code = 1
            if variant == "positive":
                self.assertEqual(code, 0)
                self.assertEqual(binding_calls, 2)
            else:
                self.assertNotEqual(code, 0)
            if variant == "existing_output":
                self.assertEqual((output / "sentinel").read_bytes(), b"preserved")

    def test_successful_replay_fixture(self):
        self.run_case("positive")

    def test_failed_replay_processes_and_diagnostics(self):
        for variant in (
            "nonzero",
            "timeout",
            "empty_output",
            "wrong_module",
            "extra_output",
            "stderr",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_changed_inputs_or_evidence_rejected(self):
        for variant in (
            "object_mutation",
            "checker_mutation",
            "prior_log_mutation",
            "environment_runner_mutation",
            "environment_policy_mutation",
            "bad_binding",
            "late_bad_binding",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_fresh_paths_and_checker_required(self):
        for variant in (
            "missing_checker",
            "existing_output",
            "proof_escape",
            "output_escape",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)


if __name__ == "__main__":
    unittest.main()
