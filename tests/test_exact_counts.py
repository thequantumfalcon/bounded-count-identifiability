"""Finite independent controls, not a substitute for the universal proof."""

import contextlib
import io
import json
import unittest
from fractions import Fraction as F
from itertools import permutations
from math import comb, factorial

from bounded_counts import (
    factorial_cumulants,
    factorial_cumulants_from_moments,
    factorial_moments,
    generalized_matching_law,
    poisson_added_factorial_cumulants,
    poisson_added_factorial_moments,
    validate_law,
)
from bounded_counts.__main__ import main


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def multiply_truncated(a, b, order):
    return [
        sum((a[j] * b[r - j] for j in range(r + 1)), F(0)) for r in range(order + 1)
    ]


def independent_formal_log_cumulants(p, order):
    # Direct finite log(1+u) expansion. It shares no moment/cumulant recurrence
    # with the package, and forms coefficients straight from the probability law.
    u = [F(0)] + [
        sum((mass * comb(x, r) for x, mass in enumerate(p) if x >= r), F(0))
        for r in range(1, order + 1)
    ]
    power = [F(1)] + [F(0)] * order
    logarithm = [F(0)] * (order + 1)
    for k in range(1, order + 1):
        power = multiply_truncated(power, u, order)
        for r in range(order + 1):
            logarithm[r] += F((-1) ** (k + 1), k) * power[r]
    return tuple(coefficient * factorial(r) for r, coefficient in enumerate(logarithm))


def matching_via_permutations(degree, h):
    # Independent combinatorial construction: enumerate permutations, then
    # retain each fixed point with Bernoulli probability h.
    result = [F(0)] * (degree + 1)
    for perm in permutations(range(degree)):
        fixed = sum(value == position for position, value in enumerate(perm))
        for retained in range(fixed + 1):
            result[retained] += (
                F(comb(fixed, retained), factorial(degree))
                * h**retained
                * (1 - h) ** (fixed - retained)
            )
    return tuple(result)


class LawValidationTests(unittest.TestCase):
    def test_exact_validation_and_support_padding(self):
        self.assertEqual(
            validate_law([F(1, 3), F(2, 3)], support_bound=3),
            (F(1, 3), F(2, 3), F(0), F(0)),
        )
        self.assertEqual(validate_law([1, 0, 0], support_bound=0), (F(1),))
        self.assertEqual(validate_law(iter([1])), (F(1),))
        self.assertEqual(validate_law([1, 0]), (F(1), F(0)))

    def test_invalid_laws(self):
        for p in [[], [F(1, 3), F(1, 3)], [-1, 2], [0], [1, 1]]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                validate_law(p)
        for p in [[0.5, 0.5], [float("nan")], [True], ["1"]]:
            with self.subTest(p=p), self.assertRaises(TypeError):
                validate_law(p)
        with self.assertRaises(ValueError):
            validate_law([0, 1], support_bound=0)

    def test_invalid_parameters(self):
        for bad in [-1, 0.5, True, "2"]:
            with self.subTest(order=bad), self.assertRaises((ValueError, TypeError)):
                factorial_moments([1], bad)
            with self.subTest(bound=bad), self.assertRaises((ValueError, TypeError)):
                validate_law([1], support_bound=bad)
        for bad in [-1, 0.5, True]:
            with (
                self.subTest(background=bad),
                self.assertRaises((ValueError, TypeError)),
            ):
                poisson_added_factorial_moments([1], bad, 2)
        for bad in [[], [0], [1, -1]]:
            with self.subTest(moments=bad), self.assertRaises(ValueError):
                factorial_cumulants_from_moments(bad)


class ExactIdentityTests(unittest.TestCase):
    def test_degree_zero_and_zero_order(self):
        self.assertEqual(factorial_moments([1], 4), (F(1), F(0), F(0), F(0), F(0)))
        self.assertEqual(factorial_cumulants([1], 4), (F(0),) * 5)
        self.assertEqual(factorial_cumulants_from_moments([1]), (F(0),))
        self.assertEqual(poisson_added_factorial_moments([1], F(2, 3), 0), (F(1),))
        self.assertEqual(poisson_added_factorial_cumulants([1], F(2, 3), 0), (F(0),))
        self.assertEqual(
            poisson_added_factorial_moments([1], F(2, 3), 8),
            tuple(F(2, 3) ** r for r in range(9)),
        )

    def test_degree_one_boundaries(self):
        for p in [F(0), F(1, 3), F(1)]:
            actual = factorial_cumulants([1 - p, p], 6)
            expected = (F(0),) + tuple(
                (-1) ** (r - 1) * factorial(r - 1) * p**r for r in range(1, 7)
            )
            self.assertEqual(actual, expected)

    def test_small_rational_laws_against_independent_log(self):
        examined = 0
        for degree in range(5):
            signatures = {}
            for numerators in compositions(4, degree + 1):
                law = tuple(F(n, 4) for n in numerators)
                order = degree + 3
                moments = factorial_moments(law, order)
                for r in range(order + 1):
                    direct = sum(
                        (
                            mass * (factorial(x) // factorial(x - r))
                            for x, mass in enumerate(law)
                            if x >= r
                        ),
                        F(0),
                    )
                    self.assertEqual(moments[r], direct)
                actual = factorial_cumulants(law, order)
                self.assertEqual(actual, independent_formal_log_cumulants(law, order))
                signature = actual[2 : degree + 2]
                self.assertNotIn(
                    signature,
                    signatures,
                    "distinct enumerated laws collided through D+1",
                )
                signatures[signature] = law
                examined += 1
        self.assertEqual(examined, 126)

    def test_fixed_poisson_changes_only_mean(self):
        laws = [
            (F(1),),
            (F(2, 3), F(1, 3)),
            (F(1, 5), F(2, 5), F(2, 5)),
            (F(0), F(0), F(1)),
        ]
        for law in laws:
            source = factorial_cumulants(law, 7)
            for background in [F(0), F(1, 3), F(2)]:
                observed = poisson_added_factorial_cumulants(law, background, 7)
                self.assertEqual(observed[0], 0)
                self.assertEqual(observed[1], source[1] + background)
                self.assertEqual(observed[2:], source[2:])


class KnownFamilyTests(unittest.TestCase):
    def test_against_independent_permutation_enumeration(self):
        for degree in range(7):
            for h in [F(0), F(1, 3), F(1, 2), F(1)]:
                with self.subTest(degree=degree, h=h):
                    self.assertEqual(
                        generalized_matching_law(degree, h),
                        matching_via_permutations(degree, h),
                    )

    def test_matched_moments_and_first_different_cumulant(self):
        for degree in range(1, 9):
            for h in [F(1, 3), F(1, 2), F(1)]:
                law = generalized_matching_law(degree, h)
                self.assertEqual(
                    factorial_moments(law, degree + 1),
                    tuple(h**r for r in range(degree + 1)) + (F(0),),
                )
                ka = poisson_added_factorial_cumulants(law, 0, degree + 1)
                kb = poisson_added_factorial_cumulants([1], h, degree + 1)
                self.assertEqual(ka[1 : degree + 1], kb[1 : degree + 1])
                self.assertEqual(ka[degree + 1], -(h ** (degree + 1)))
                self.assertEqual(kb[degree + 1], 0)
                self.assertNotEqual(law, (F(1),) + (F(0),) * degree)

    def test_family_invalid_parameters(self):
        for h in [F(-1, 2), F(3, 2), 0.5, True]:
            with self.subTest(h=h), self.assertRaises((ValueError, TypeError)):
                generalized_matching_law(3, h)
        for degree in [-1, True, 2.5]:
            with (
                self.subTest(degree=degree),
                self.assertRaises((ValueError, TypeError)),
            ):
                generalized_matching_law(degree, F(1, 2))


class CommandLineTests(unittest.TestCase):
    def test_json_example_is_exact(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(main(["--degree", "3", "--strength", "1/2", "--json"]), 0)
        result = json.loads(stream.getvalue())
        self.assertTrue(result["equal_through_degree"])
        self.assertTrue(result["different_at_degree_plus_one"])
        self.assertEqual(
            result["source_a"]["observed_factorial_cumulants"],
            ["1/2", "0", "0", "-1/16"],
        )
        self.assertEqual(
            result["source_b"]["observed_factorial_cumulants"], ["1/2", "0", "0", "0"]
        )

    def test_degree_one_example(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(main(["--degree", "1", "--strength", "1/3"]), 0)
        self.assertIn("2 | -1/9 | 0", stream.getvalue())

    def test_invalid_cli_inputs(self):
        for args in [
            ["--degree", "0"],
            ["--strength", "0"],
            ["--strength", "1"],
            ["--strength", "1/0"],
            ["--strength", "nan"],
        ]:
            with (
                self.subTest(args=args),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as raised,
            ):
                main(args)
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
