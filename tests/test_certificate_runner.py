"""Diagnostic controls; these do not independently verify Lean or its proofs."""

import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "lean/check_certificates.py"
SPEC = importlib.util.spec_from_file_location("certificate_runner", SOURCE)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

# Pinned Lean 4.35.0 residual from an intentionally wrong normalized query.
# This rejection diagnostic is not itself an additional proof of negation.
MODULE = "Wrong00"
FALSE_DIAGNOSTIC = "Wrong00.lean:9:170: error: unsolved goals\n⊢ False\n"
# Actual kernel-decision failure: it must not count as a diagnosed false goal.
STUCK_DIAGNOSTIC = (
    "StuckKernelDecision.lean:4:43: error: Tactic `decide` failed to reduce\n"
    "  @decide (hidden = false) (instDecidableEqBool hidden false)\n"
    "to `true` or `false`.\n\n"
    "Reduction got stuck at\n"
    "  hidden\n"
)


class CertificateDiagnosticTests(unittest.TestCase):
    def classify(self, **changes):
        arguments = {
            "module": MODULE,
            "stdout": FALSE_DIAGNOSTIC,
            "stderr": "",
            "exit_code": 1,
            "timed_out": False,
            "object_exists": False,
            "split_objects_exist": False,
        }
        return runner.diagnosed_false(**(arguments | changes))

    def test_accepts_actual_normalized_false_diagnostic(self):
        self.assertTrue(self.classify())
        self.assertTrue(self.classify(stdout=FALSE_DIAGNOSTIC.rstrip("\n")))

    def test_rejects_actual_stuck_decision(self):
        self.assertFalse(
            self.classify(module="StuckKernelDecision", stdout=STUCK_DIAGNOSTIC)
        )

    def test_rejects_extra_or_forged_diagnostics(self):
        for text in (
            "warning: earlier warning\n" + FALSE_DIAGNOSTIC,
            FALSE_DIAGNOSTIC + "Other.lean:1:1: error: unrelated failure\n",
            FALSE_DIAGNOSTIC.replace(": error: ", ": warning: "),
            FALSE_DIAGNOSTIC.replace("unsolved goals", "failed to reduce"),
            FALSE_DIAGNOSTIC.replace("⊢ False\n", ""),
            FALSE_DIAGNOSTIC.replace("⊢ False\n", "⊢ True\n"),
            FALSE_DIAGNOSTIC.replace("⊢ False\n", "h : False\n⊢ False\n"),
            FALSE_DIAGNOSTIC.replace("⊢ False\n", "⊢ False\n⊢ False\n"),
            FALSE_DIAGNOSTIC.replace("⊢ False\n", "  False\n"),
            "Wrong00.lean:1:1: error: unknown module prefix 'Missing'\n",
            "error: decide false\n",
            "",
        ):
            with self.subTest(text=text):
                self.assertFalse(self.classify(stdout=text))

    def test_rejects_wrong_module_or_location(self):
        for changes in (
            {"module": "Other"},
            {"module": MODULE + "."},
            {"stdout": FALSE_DIAGNOSTIC.replace(":9:170:", ":0:170:")},
            {"stdout": FALSE_DIAGNOSTIC.replace(":9:170:", ":9:0:")},
        ):
            with self.subTest(changes=changes):
                self.assertFalse(self.classify(**changes))

    def test_rejects_incompatible_process_or_object_outcome(self):
        for changes in (
            {"exit_code": 0},
            {"exit_code": 2},
            {"exit_code": 124},
            {"timed_out": True},
            {"object_exists": True},
            {"split_objects_exist": True},
        ):
            with self.subTest(changes=changes):
                self.assertFalse(self.classify(**changes))

    def test_requires_empty_stderr(self):
        for text in ("unrelated error\n", "\n", " "):
            with self.subTest(stderr=text):
                self.assertFalse(self.classify(stderr=text))


if __name__ == "__main__":
    unittest.main()
