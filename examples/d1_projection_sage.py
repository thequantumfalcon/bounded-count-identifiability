"""Optional exact D=1 population-moment-box projection with SageMath.

Run: sage -python examples/d1_projection_sage.py --self-test

For X~Bernoulli(p), independent Z~Poisson(b), and 0<=b<=B, let
m=E[X+Z]=p+b and f=E[(X+Z)(X+Z-1)]=m*m-p*p. This script projects
a specified rectangular (m,f) box onto p and constructs admissible b values.
It does not obtain a confidence box from data or validate a detector model.
All feasibility decisions use exact real algebraic comparisons, not floats.
Sage is optional and is not a dependency of the bounded_counts package.
"""

import argparse
import json
from fractions import Fraction
from itertools import combinations_with_replacement

from sage.all import AA, QQ, ZZ, parent
from sage.version import version as sage_version


def exact(value):
    """Reject approximate numeric inputs and Boolean pseudo-counts."""
    if not isinstance(value, bool) and (
        isinstance(value, (int, Fraction)) or parent(value) in (ZZ, QQ, AA)
    ):
        return AA(value)
    raise TypeError("use exact integer, rational or real algebraic inputs")


def project_moment_box(
    background_ceiling, mean_low, mean_high, second_low, second_high
):
    """Return a closed exact p interval, or None for an empty model intersection.

    Reversed boxes and negative background ceilings are input errors, not empty
    statistical confidence sets. The model requires a known finite B>=0.
    """
    ceiling, low, high, second_min, second_max = map(
        exact, (background_ceiling, mean_low, mean_high, second_low, second_high)
    )
    if ceiling < 0:
        raise ValueError("background_ceiling must be nonnegative")
    if low > high or second_min > second_max:
        raise ValueError("moment box endpoints must be ordered")
    a, c = max(AA(0), low), min(AA(1) + ceiling, high)
    d, e = max(AA(0), second_min), min(ceiling**2 + 2 * ceiling, second_max)
    if a > c or d > e:
        return None
    if ceiling == 0:
        return (a, c) if d == 0 else None
    if c * c < d:
        return None
    lower = max(
        AA(0),
        a - ceiling,
        max(AA(0), a * a - e).sqrt(),
        (d - ceiling**2) / (2 * ceiling),
    )
    upper = min(AA(1), c, (c * c - d).sqrt())
    return (lower, upper) if lower <= upper else None


def background_witness(background_ceiling, moment_box, source_probability):
    """Construct b for a p in the projection, checking the original constraints."""
    ceiling, p = exact(background_ceiling), exact(source_probability)
    bounds = tuple(map(exact, moment_box))
    interval = project_moment_box(ceiling, *bounds)
    if interval is None or not interval[0] <= p <= interval[1]:
        raise ValueError("source_probability is outside the feasible projection")
    first_low, first_high, second_low, second_high = bounds
    mean = max(AA(0), first_low, p, (max(AA(0), second_low) + p * p).sqrt())
    background = mean - p
    if not (
        0 <= p <= 1
        and 0 <= background <= ceiling
        and first_low <= mean <= first_high
        and second_low <= mean * mean - p * p <= second_high
    ):
        raise ArithmeticError(
            "constructed witness failed the original model constraints"
        )
    return background


def direct_mean_feasible(ceiling, box, probability):
    """Independent test route: intersect mean intervals without eliminating p."""
    ceiling, p = exact(ceiling), exact(probability)
    first_low, first_high, second_low, second_high = map(exact, box)
    if p < 0 or p > 1 or second_high + p * p < 0:
        return False
    lowest_mean = max(AA(0), first_low, p, max(AA(0), second_low + p * p).sqrt())
    highest_mean = min(first_high, p + ceiling, (second_high + p * p).sqrt())
    return lowest_mean <= highest_mean


def algebraic_descriptor(value):
    """Return a minimal polynomial and an exact isolating rational interval."""
    value = exact(value)
    polynomial = value.minpoly()
    roots = polynomial.roots(AA, multiplicities=False)
    bits = 32
    while True:
        denominator = ZZ(2) ** bits
        lower = QQ((value * denominator).floor()) / denominator
        upper = QQ((value * denominator).ceil()) / denominator
        contained_roots = [root for root in roots if lower <= root <= upper]
        if contained_roots == [value]:
            return {
                "minimal_polynomial_coefficients_low_to_high": [
                    str(c) for c in polynomial.list()
                ],
                "isolating_interval_rational": [str(lower), str(upper)],
            }
        bits *= 2


def self_test():
    fixtures = [
        (0, (0, 1, 0, 0), (AA(0), AA(1))),
        (0, (0, 1, QQ(1) / 4, 1), None),
        (1, (-2, -1, 0, 1), None),
        (1, (0, 2, -2, -1), None),
        (1, (0, QQ(1) / 2, 1, 1), None),
        (1, (1, 1, QQ(1) / 2, QQ(1) / 2), (AA(QQ(1) / 2).sqrt(),) * 2),
        (1, (2, 2, 3, 3), (AA(1), AA(1))),
    ]
    for ceiling, box, expected in fixtures:
        assert project_moment_box(ceiling, *box) == expected
    checked_memberships = 0
    checked_witnesses = 0
    first_intervals = list(
        combinations_with_replacement(
            map(QQ, [0, Fraction(1, 2), 1, Fraction(3, 2), 2]), 2
        )
    )
    second_intervals = list(
        combinations_with_replacement(map(QQ, [0, Fraction(1, 2), 1, 2, 3]), 2)
    )
    for ceiling in [QQ(0), QQ(1) / 2, QQ(1)]:
        for first in first_intervals:
            for second in second_intervals:
                box = first + second
                interval = project_moment_box(ceiling, *box)
                for p in [QQ(j) / 4 for j in range(5)]:
                    accepted = interval is not None and interval[0] <= p <= interval[1]
                    assert accepted == direct_mean_feasible(ceiling, box, p)
                    checked_memberships += 1
                if interval is not None:
                    for p in [interval[0], sum(interval) / 2, interval[1]]:
                        background_witness(ceiling, box, p)
                        checked_witnesses += 1
    for invalid in [True, 0.5, "1/2"]:
        try:
            project_moment_box(invalid, 0, 1, 0, 1)
        except TypeError:
            pass
        else:
            raise AssertionError("an inexact or unsupported input was accepted")
    for args in [(-1, 0, 1, 0, 1), (1, 1, 0, 0, 1), (1, 0, 1, 1, 0)]:
        try:
            project_moment_box(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid model bounds were accepted")
    assert checked_memberships == 3375
    return {
        "boundary_fixtures": len(fixtures),
        "exact_membership_comparisons": checked_memberships,
        "original_constraint_witness_checks": checked_witnesses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="also check finite exact boundary and grid controls",
    )
    args = parser.parse_args()
    ceiling = QQ(1)
    box = (QQ(1), QQ(1), QQ(1) / 4, QQ(3) / 4)
    lower, upper = project_moment_box(ceiling, *box)
    assert lower == QQ(1) / 2 and upper == AA(3).sqrt() / 2
    result = {
        "sage_version": sage_version,
        "input_kind": "illustrative population-moment box; no measured data or confidence-level claim",
        "background_ceiling": str(ceiling),
        "moment_box": list(map(str, box)),
        "source_probability_interval": [
            algebraic_descriptor(lower),
            algebraic_descriptor(upper),
        ],
        "endpoint_background_witnesses": [
            algebraic_descriptor(background_witness(ceiling, box, p))
            for p in (lower, upper)
        ],
        "scope": "D=1 exact projection for a specified independent fixed-Poisson model; finite controls are not formal verification.",
    }
    if args.self_test:
        result["self_tests"] = self_test()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
