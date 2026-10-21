"""Boundary and enclosure controls for the deterministic scale diagnostic."""

import importlib.util
from fractions import Fraction as F
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "examples/d1_confidence_scale.py"
SPEC = importlib.util.spec_from_file_location("d1_confidence_scale", SOURCE)
scale = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scale)


class ConfidenceScaleTests(unittest.TestCase):
    def test_sqrt_enclosures_cover_exact_input(self):
        for value in [F(0), F(1, 4), F(2), F(7, 13), F(10**30, 7)]:
            low, high = scale.sqrt_fraction(value)
            self.assertLessEqual(low**2, value)
            self.assertGreaterEqual(high**2, value)
            self.assertLessEqual(high - low, F(1, scale.SCALE))
        self.assertEqual(scale.sqrt_fraction(F(1, 4)), (F(1, 2), F(1, 2)))
        with self.assertRaises(ValueError):
            scale.sqrt_fraction(-1)

    def test_zero_background_closed_form_and_endpoint_clipping(self):
        # With B=0, the second radius vanishes and rho1=sqrt(10/N).
        middle = scale.centered_projection(F(3, 10), 0, 0, 4000)
        self.assertEqual(middle["lower"], (F(1, 4), F(1, 4)))
        self.assertEqual(middle["upper"], (F(7, 20), F(7, 20)))
        self.assertEqual(middle["width"], (F(1, 10), F(1, 10)))
        at_zero = scale.centered_projection(0, 0, 0, 1000)
        at_one = scale.centered_projection(1, 0, 0, 1000)
        self.assertEqual(at_zero["width"], (F(1, 10), F(1, 10)))
        self.assertEqual(at_one["width"], (F(1, 10), F(1, 10)))

    def test_fixed_parameter_threshold_has_adjacent_integer_certificate(self):
        threshold = scale.first_centered_width(F(1, 10))
        self.assertGreater(threshold, 1_600_000)
        self.assertLess(threshold, 1_700_000)
        self.assertGreater(scale.at_windows(threshold - 1)["width"][0], F(1, 10))
        self.assertLessEqual(scale.at_windows(threshold)["width"][1], F(1, 10))
        previous = None
        for n in (10**k for k in range(4, 9)):
            result = scale.at_windows(n)
            self.assertLessEqual(result["lower"][1], F(3, 10))
            self.assertGreaterEqual(result["upper"][0], F(3, 10))
            if previous is not None:
                self.assertLess(result["width"][1], previous[0])
            previous = result["width"]

    def test_invalid_parameters_fail(self):
        for n in (0, -1, True, F(2, 3)):
            with self.assertRaises(ValueError):
                scale.centered_projection(F(3, 10), 0, 1, n)
        for p in (True, 0.3, "3/10"):
            with self.assertRaises(TypeError):
                scale.centered_projection(p, 0, 1, 100)
        for args in ((-1, 0, 1), (0, 2, 1), (0, 0, -1)):
            with self.assertRaises(ValueError):
                scale.centered_projection(*args, 100)
        for target in (0, 1, -1):
            with self.assertRaises(ValueError):
                scale.first_centered_width(target)


if __name__ == "__main__":
    unittest.main()
