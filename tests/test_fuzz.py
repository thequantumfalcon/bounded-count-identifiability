"""Reproducibility and deliberately faulty controls for the bounded fuzz target."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

import bounded_counts

TARGET = Path(__file__).resolve().parents[1] / "fuzz" / "exact_counts.py"
SPEC = importlib.util.spec_from_file_location("bounded_counts_fuzz", TARGET)
fuzz = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fuzz)


class FuzzTests(unittest.TestCase):
    def test_smoke_corpus_and_seed(self):
        result = fuzz.run(iterations=32)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["corpus_cases"], 8)
        first = list(fuzz.generated_cases(20261021, 3))
        self.assertEqual(first[0][1].hex(), "5039abdcde0c727951167748e2609ff2ef")
        self.assertEqual(first, list(fuzz.generated_cases(20261021, 3)))
        self.assertNotEqual(first, list(fuzz.generated_cases(20261022, 3)))
        self.assertEqual(
            set(result["source_sha256"]), {"target", "corpus", "installed_core"}
        )
        self.assertTrue(
            all(len(value) == 64 for value in result["source_sha256"].values())
        )

    def test_bounds_are_enforced(self):
        for seed, iterations in [
            (-1, 1),
            (2**64, 1),
            (True, 1),
            (0, -1),
            (0, 10001),
            (0, True),
        ]:
            with (
                self.subTest(seed=seed, iterations=iterations),
                self.assertRaises(ValueError),
            ):
                list(fuzz.generated_cases(seed, iterations))
        for data in [b"x" * 18, "not bytes"]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                fuzz.check_case(data)

    def test_oracle_known_values(self):
        # log(1+t/2) has cumulants (-1)^(n-1)*(n-1)!/2^n.
        self.assertEqual(
            fuzz.partition_cumulants([fuzz.F(1), fuzz.F(1, 2), fuzz.F(0), fuzz.F(0)]),
            (fuzz.F(0), fuzz.F(1, 2), fuzz.F(-1, 4), fuzz.F(1, 4)),
        )
        self.assertEqual(
            fuzz.matching_by_derangements(3, fuzz.F(1)),
            (fuzz.F(1, 3), fuzz.F(1, 2), fuzz.F(0), fuzz.F(1, 6)),
        )

    def test_faulty_implementations_are_detected(self):
        cases = [data for _, data in fuzz.corpus_cases()]
        # Modify only the injected API; installed package and oracles stay intact.
        faults = {
            "factorial_moments": lambda *a, **k: (fuzz.F(1),),
            "factorial_cumulants": lambda *a, **k: (fuzz.F(0),) * (a[1] + 1),
            "poisson_added_factorial_cumulants": lambda p, b, order: (
                bounded_counts.factorial_cumulants(p, order)
            ),
            "generalized_matching_law": lambda degree, h: (
                (fuzz.F(1),) + (fuzz.F(0),) * degree
            ),
            "validate_law": lambda p, **k: tuple(p),
        }
        for name, replacement in faults.items():
            api = SimpleNamespace(
                **{key: getattr(bounded_counts, key) for key in bounded_counts.__all__}
            )
            setattr(api, name, replacement)
            with self.subTest(fault=name):
                detected = False
                for case in cases:
                    try:
                        fuzz.check_case(case, api)
                    except AssertionError:
                        detected = True
                        break
                self.assertTrue(detected, f"undetected deliberately faulty API: {name}")


if __name__ == "__main__":
    unittest.main()
