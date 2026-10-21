"""Input and emission controls; mathematical verdicts are checked by Lean in CI."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "examples/d1_certificates.py"
SPEC = importlib.util.spec_from_file_location("d1_certificates", SOURCE)
emitter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(emitter)


class CertificateTests(unittest.TestCase):
    def test_rejects_inexact_expressions_and_code(self):
        for value in (
            "0.5",
            "1e2",
            "1/0",
            "1/-2",
            "01",
            " 1",
            "1\n",
            "1 + 2",
            "1); axiom bad : False",
            "９",
            "9" * 65,
            "1/" + "9" * 65,
            True,
            0.5,
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                emitter.parse_rational(value)

    def test_normalizes_numbers_and_binds_every_argument(self):
        text = emitter.certificate(
            "source", True, ["+2/2", "-2/4", "3", "0", "4", "2/6"]
        )
        self.assertIn("B=1, a=-1/2, c=3, d=0, e=4, p=1/3", text)
        self.assertIn("(a := ((-1) / 2 : ℚ))", text)
        self.assertIn("(p := ((1) / 3 : ℚ))", text)
        self.assertIn("checkSource_eq_true_iff", text)
        self.assertNotIn("native_decide", text)

    def test_rejects_wrong_arity_and_verdict_type(self):
        for kind, verdict, values in (
            ("unknown", True, []),
            ("source", 1, ["0"] * 6),
            ("pair", True, ["0"] * 6),
            ("nonempty", False, ["0"] * 6),
        ):
            with self.assertRaises(ValueError):
                emitter.certificate(kind, verdict, values)

    def test_global_rejection_quantifies_over_real_probabilities(self):
        text = emitter.certificate("nonempty", False, ["1", "0", "0", "1", "1"])
        self.assertIn("¬ (∃ p : ℝ, CountConfidenceProjection.Feasible", text)
        self.assertIn("checkNonempty_eq_false_iff", text)

    def test_cli_failure_emits_no_partial_certificate(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SOURCE),
                "--kind",
                "source",
                "--expect",
                "accept",
                "--values=1,0,1,0,1,0.5",
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")

    def test_cli_handles_negative_fractions_and_utf8_output(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SOURCE),
                "--kind",
                "source",
                "--expect",
                "reject",
                "--values=1,0,1,0,1,-1/2",
            ],
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(p := ((-1) / 2 : ℚ))", result.stdout.decode("utf-8"))

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "Query.lean"
            output.write_bytes(b"preserve existing evidence\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SOURCE),
                    "--kind",
                    "pair",
                    "--expect",
                    "accept",
                    "--values=1,0,2,0,3,1/2,1/2",
                    "--output",
                    str(output),
                ],
                capture_output=True,
                timeout=10,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b"preserve existing evidence\n")


if __name__ == "__main__":
    unittest.main()
