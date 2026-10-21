"""Acceptance controls for the shared auditor and standalone core verifier.

Compiler processes are mocked and all mutations affect disposable copies.
These controls test the audit boundary, not the truth of any Lean theorem.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]


def load_module(name, source):
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("proof_audit_tests", REPOSITORY / "lean/proof_audit.py")


def axiom_output(roots, axioms="propext, Classical.choice, Quot.sound"):
    return "\n".join(
        f"'{root}' depends on axioms: [{axioms}]"
        if axioms is not None
        else f"'{root}' does not depend on any axioms"
        for root in roots
    )


class ProofAuditPolicyTests(unittest.TestCase):
    def test_comment_and_string_contents_are_not_commands(self):
        AUDIT.validate_source(
            "/- outer sorry /- run_elab -/ set_option -/\n"
            '-- #eval Lean.logInfo "forged output"\n'
            'def label : String := "axiom \\"run_cmd\\""\n'
            "theorem valid : True := by trivial\n"
        )
        AUDIT.validate_source("theorem valid : True := by trivial -- sorryAx\n")

    def test_admissions_metaprogramming_and_escaped_names_fail(self):
        for command in (
            "theorem bad : False := by sorry",
            "theorem bad : False := by admit",
            "theorem bad : False := sorryAx _ true",
            "axiom bad : False",
            "theorem bad : False := by native_decide",
            "set_option debug.skipKernelTC true",
            'run_elab Lean.logInfo "forged output"',
            'run_cmd Lean.logInfo "forged output"',
            "run_meta pure ()",
            'elab "custom" : command => pure ()',
            'macro "custom" : command => `(theorem bad : True := by trivial)',
            'syntax "custom" : command',
            "initialize fixture : Nat ← pure 0",
            "builtin_initialize fixture : Nat ← pure 0",
            "unsafe def fixture : Nat := 0",
            "opaque fixture : Nat := 0",
            "#eval IO.println 1",
            "theorem bad : False := «sorryAx» _ true",
        ):
            with self.subTest(command=command), self.assertRaises(ValueError):
                AUDIT.validate_source(command)
        for malformed in ("/- open", 'def label := "open', "theorem x\x00 : True"):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                AUDIT.validate_source(malformed)

    def test_generated_query_has_only_fixed_import_and_complete_roots(self):
        self.assertEqual(
            AUDIT.audit_source("Fixture", ["Fixture.first", "Fixture.second"]),
            "import Fixture\n\n#print axioms Fixture.first\n#print axioms Fixture.second\n",
        )
        for module, roots in (
            ("Fixture", []),
            ("Fixture", ["Fixture.first", "Fixture.first"]),
            ("Fixture\n#eval 1", ["Fixture.first"]),
            ("Fixture", ["Fixture.first\n#eval 1"]),
            ("Fixture", ["Fixture.«first»"]),
        ):
            with (
                self.subTest(module=module, roots=roots),
                self.assertRaises(ValueError),
            ):
                AUDIT.audit_source(module, roots)

    def test_permitted_axiom_subsets_and_zero_are_accepted(self):
        roots = ["Fixture.first", "Fixture.second"]
        for axioms in (None, "", "propext", "Quot.sound, Classical.choice"):
            with self.subTest(axioms=axioms):
                parsed = AUDIT.parse_axioms(axiom_output(roots, axioms), roots)
                expected = [] if not axioms else axioms.split(", ")
                self.assertEqual(parsed, dict.fromkeys(roots, expected))
        wrapped = "'Fixture.first' depends on axioms: [propext,\n Classical.choice]\n"
        self.assertEqual(
            AUDIT.parse_axioms(wrapped, roots[:1]),
            {"Fixture.first": ["propext", "Classical.choice"]},
        )

    def test_incomplete_duplicate_unexpected_or_forged_output_fails(self):
        roots = ["Fixture.first", "Fixture.second"]
        good = axiom_output(roots)
        variants = (
            "",
            axiom_output(roots[:1]),
            axiom_output(roots + roots[:1]),
            axiom_output(roots + ["Fixture.third"]),
            axiom_output(list(reversed(roots))),
            axiom_output(roots, "propext, propext"),
            axiom_output(roots, "propext, Untrusted.custom"),
            axiom_output(roots, "sorryAx"),
            "info: " + good,
            good + "\nwarning: unexpected output",
            "prefix" + good,
        )
        for output in variants:
            with self.subTest(output=output), self.assertRaises(ValueError):
                AUDIT.parse_axioms(output, roots)

    def test_audit_receipt_rechecks_query_logs_and_metadata(self):
        for variant in ("positive", "query", "stdout", "stderr", "record", "axiom"):
            with (
                self.subTest(variant=variant),
                tempfile.TemporaryDirectory() as directory,
            ):
                output = Path(directory)
                roots = ["Fixture.first"]
                good = axiom_output(roots).encode()
                with patch.object(
                    AUDIT.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, good, b""),
                ):
                    record = AUDIT.run_axiom_audit(
                        Path("mock-lean"), "Fixture", roots, output, {}, bytes.decode
                    )
                self.assertEqual(record["status"], "PASS")
                if variant == "query":
                    (output / "Fixture.audit.lean").write_text("import Other\n")
                elif variant in ("stdout", "stderr"):
                    with (output / f"Fixture.audit.{variant}.txt").open("a") as stream:
                        stream.write("changed")
                elif variant == "record":
                    changed = {**record, "exit_code": 1}
                    (output / "Fixture.audit.json").write_text(json.dumps(changed))
                elif variant == "axiom":
                    # Rewriting hashes and matching record fields does not avoid
                    # semantic re-parsing of the now-forbidden axiom report.
                    stdout = output / "Fixture.audit.stdout.txt"
                    stdout.write_text(axiom_output(roots, "Untrusted.custom"))
                    record["stdout_sha256"] = AUDIT.digest(stdout)
                    record["printed_axiom_lists"] = {roots[0]: ["Untrusted.custom"]}
                    (output / "Fixture.audit.json").write_text(json.dumps(record))
                if variant == "positive":
                    AUDIT.validate_audit_record(output, "Fixture", roots, record)
                else:
                    with self.assertRaises(ValueError):
                        AUDIT.validate_audit_record(output, "Fixture", roots, record)

    def test_audit_process_failures_and_output_reuse_fail(self):
        roots = ["Fixture.first"]
        for variant in ("timeout", "nonzero", "stderr", "query_changed", "reuse"):
            with (
                self.subTest(variant=variant),
                tempfile.TemporaryDirectory() as directory,
            ):
                output = Path(directory)
                if variant == "reuse":
                    (output / "Fixture.audit.json").write_text("preserve")

                def fake_run(command, **kwargs):
                    self.assertEqual(command[1:], ["--trust=0", "Fixture.audit.lean"])
                    self.assertEqual(kwargs["cwd"], output)
                    if variant == "timeout":
                        raise subprocess.TimeoutExpired(command, 240)
                    if variant == "query_changed":
                        (output / "Fixture.audit.lean").write_text("import Other\n")
                    return subprocess.CompletedProcess(
                        command,
                        1 if variant == "nonzero" else 0,
                        axiom_output(roots).encode(),
                        b"unexpected stderr" if variant == "stderr" else b"",
                    )

                with patch.object(AUDIT.subprocess, "run", side_effect=fake_run):
                    if variant == "reuse":
                        with self.assertRaises(ValueError):
                            AUDIT.run_axiom_audit(
                                Path("mock-lean"),
                                "Fixture",
                                roots,
                                output,
                                {},
                                bytes.decode,
                            )
                        self.assertEqual(
                            (output / "Fixture.audit.json").read_text(), "preserve"
                        )
                    else:
                        record = AUDIT.run_axiom_audit(
                            Path("mock-lean"),
                            "Fixture",
                            roots,
                            output,
                            {},
                            bytes.decode,
                        )
                        self.assertEqual(record["status"], "FAIL")


class CoreVerifierTests(unittest.TestCase):
    def run_case(self, variant):
        with tempfile.TemporaryDirectory(prefix="core-audit-test-") as directory:
            root = Path(directory).resolve()
            source_root = root / "lean"
            source_root.mkdir()
            names = (
                "verify.py",
                "proof_audit.py",
                "source_manifest.json",
                "lake-manifest.json",
                "lakefile.toml",
                "lean-toolchain",
                *(name + ".lean" for name in AUDIT.CORE),
            )
            for name in names:
                shutil.copyfile(REPOSITORY / "lean" / name, source_root / name)
            verifier = source_root / "verify.py"
            module = load_module("core_audit_fixture", verifier)
            compiler = root / "mock-compiler.bin"
            compiler.write_bytes(b"never executed")
            library = root / "library"
            library.mkdir()
            output = source_root / "verification/test"
            build = source_root / ".verification/test"
            first, last = AUDIT.CORE[0], AUDIT.CORE[-1]
            first_source = source_root / (first + ".lean")
            manifest_path = source_root / "source_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if variant == "source_tamper":
                first_source.write_bytes(first_source.read_bytes() + b"\n")
            elif variant == "missing_manifest_source":
                del manifest["sources"][first + ".lean"]
            elif variant == "wrong_size":
                manifest["sources"][first + ".lean"]["bytes"] += 1
            elif variant == "source_policy":
                first_source.write_text(
                    first_source.read_text(encoding="utf-8")
                    + '\nrun_elab Lean.logInfo "forged axiom report"\n',
                    encoding="utf-8",
                )
                manifest["sources"][first + ".lean"] = {
                    "sha256": module.digest(first_source),
                    "bytes": first_source.stat().st_size,
                }
            if variant in ("missing_manifest_source", "wrong_size", "source_policy"):
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            elif variant == "shadow_import":
                (library / (first + ".olean")).write_bytes(b"stale")
            elif variant == "reused_run":
                output.mkdir(parents=True)
                (output / "sentinel").write_bytes(b"preserve")

            calls = {"compile": 0, "audit": 0}

            def fake_run(command, **kwargs):
                if command[-1] == "--version":
                    version = (
                        b"Lean (version 0.0.0)"
                        if variant == "wrong_compiler"
                        else b"Lean (version 4.35.0, fixture)"
                    )
                    return subprocess.CompletedProcess(command, 0, version, b"")
                self.assertIn("--trust=0", command)
                self.assertEqual(
                    kwargs["env"]["LEAN_PATH"].split(os.pathsep)[0], str(build)
                )
                if "-o" in command:
                    calls["compile"] += 1
                    name = Path(command[-1]).stem
                    target = source_root / command[command.index("-o") + 1]
                    if variant != "no_olean":
                        target.write_bytes(
                            b"" if variant == "empty_olean" else b"mock olean"
                        )
                    if variant == "compile_timeout":
                        raise subprocess.TimeoutExpired(command, 240)
                    # Valid-looking reports at source elaboration must never
                    # replace the separate audit's results.
                    stdout = axiom_output(AUDIT.full_roots(name)).encode()
                    if variant == "no_compile_prints":
                        stdout = b""
                    if variant == "compile_warning":
                        stdout += b"\nwarning: fixture"
                    return subprocess.CompletedProcess(
                        command, 1 if variant == "compile_nonzero" else 0, stdout, b""
                    )
                calls["audit"] += 1
                self.assertEqual(kwargs["cwd"], output)
                name = command[-1].removesuffix(".audit.lean")
                roots = AUDIT.full_roots(name)
                self.assertEqual(
                    (output / command[-1]).read_text(encoding="utf-8"),
                    AUDIT.audit_source(name, roots),
                )
                if variant == "missing_root":
                    roots = roots[:-1]
                elif variant == "duplicate_root":
                    roots = roots + roots[:1]
                elif variant == "extra_root":
                    roots = roots + ["Unrelated.theorem"]
                axioms = "propext, Classical.choice, Quot.sound"
                if variant == "fake_compile_prints":
                    axioms += ", Untrusted.custom"
                elif variant == "subset_axioms":
                    axioms = "Quot.sound"
                elif variant == "zero_axioms":
                    axioms = None
                if variant == "audit_timeout":
                    raise subprocess.TimeoutExpired(command, 240)
                if variant == "query_tamper":
                    (output / command[-1]).write_text("import Other\n")
                if name == last:
                    changed = {
                        "source_changed": first_source,
                        "manifest_changed": manifest_path,
                        "policy_changed": source_root / "proof_audit.py",
                        "verifier_changed": verifier,
                        "compiler_changed": compiler,
                        "lock_changed": source_root / "lake-manifest.json",
                        "config_changed": source_root / "lakefile.toml",
                        "toolchain_changed": source_root / "lean-toolchain",
                        "earlier_olean_changed": build / (first + ".olean"),
                        "earlier_compile_log_changed": output / (first + ".stdout.txt"),
                        "earlier_query_changed": output / (first + ".audit.lean"),
                        "earlier_audit_log_changed": output
                        / (first + ".audit.stdout.txt"),
                        "earlier_audit_record_changed": output
                        / (first + ".audit.json"),
                    }.get(variant)
                    if changed is not None:
                        changed.write_bytes(changed.read_bytes() + b"changed")
                return subprocess.CompletedProcess(
                    command,
                    1 if variant == "audit_nonzero" else 0,
                    axiom_output(roots, axioms).encode(),
                    b"unexpected stderr" if variant == "audit_stderr" else b"",
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
                "test",
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(module.subprocess, "run", side_effect=fake_run),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                try:
                    code = module.main()
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    subprocess.SubprocessError,
                ):
                    code = 1
            result_path = output / "result.json"
            receipt = (
                json.loads(result_path.read_text(encoding="utf-8"))
                if result_path.is_file()
                else None
            )
            if variant in (
                "positive",
                "no_compile_prints",
                "subset_axioms",
                "zero_axioms",
            ):
                self.assertEqual(code, 0)
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(calls, {"compile": 6, "audit": 6})
                self.assertEqual(
                    sum(len(row["printed_axiom_lists"]) for row in receipt["modules"]),
                    23,
                )
                self.assertTrue(all(receipt["checks"].values()))
            else:
                self.assertNotEqual(code, 0)
                if receipt is not None:
                    self.assertEqual(receipt["status"], "FAIL")
            if variant == "reused_run":
                self.assertEqual((output / "sentinel").read_bytes(), b"preserve")
            return receipt

    def test_separate_query_supplies_evidence_and_accepts_permitted_subsets(self):
        for variant in (
            "positive",
            "no_compile_prints",
            "subset_axioms",
            "zero_axioms",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_forged_compilation_messages_do_not_override_query(self):
        receipt = self.run_case("fake_compile_prints")
        self.assertFalse(receipt["modules"][0]["printed_axioms_checked"])

    def test_complete_unique_roots_are_required(self):
        for variant in ("missing_root", "duplicate_root", "extra_root"):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_fresh_output_and_successful_processes_are_required(self):
        for variant in (
            "no_olean",
            "empty_olean",
            "compile_timeout",
            "compile_nonzero",
            "compile_warning",
            "audit_timeout",
            "audit_nonzero",
            "audit_stderr",
            "query_tamper",
            "wrong_compiler",
            "reused_run",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_bound_sources_manifest_policy_and_imports_are_checked(self):
        for variant in (
            "source_tamper",
            "missing_manifest_source",
            "wrong_size",
            "source_policy",
            "shadow_import",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)

    def test_inputs_and_earlier_evidence_are_rechecked_before_success(self):
        for variant in (
            "source_changed",
            "manifest_changed",
            "policy_changed",
            "verifier_changed",
            "compiler_changed",
            "lock_changed",
            "config_changed",
            "toolchain_changed",
            "earlier_olean_changed",
            "earlier_compile_log_changed",
            "earlier_query_changed",
            "earlier_audit_log_changed",
            "earlier_audit_record_changed",
        ):
            with self.subTest(variant=variant):
                self.run_case(variant)


if __name__ == "__main__":
    unittest.main()
