"""Run the published exact identity controls against the installed package."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


class ReconstructionExampleTests(unittest.TestCase):
    def test_exact_identity_controls(self):
        script = (
            Path(__file__).resolve().parents[1] / "examples/largest_root_identity.py"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["grid_laws"], 461)
        self.assertEqual(report["generalized_matching_cases"], 24)
        self.assertTrue(report["changed_constant_rejected"])


if __name__ == "__main__":
    unittest.main()
