"""Exact finite controls for docs/reconstruction.md, using the installed package.

This checks identities starting from known laws; it is not a root-isolation
solver, a universal proof, or an analysis of measured counts.
"""

from fractions import Fraction as F
from math import comb, factorial
import json

from bounded_counts import factorial_cumulants, generalized_matching_law


def moment_polynomials(cumulants):
    """Bell recurrence with the first cumulant replaced by the variable u."""
    result = [[F(1)]]
    for r in range(1, len(cumulants)):
        polynomial = [F(0)] + result[r - 1]
        for j in range(2, r + 1):
            factor = comb(r - 1, j - 1) * cumulants[j]
            for k, coefficient in enumerate(result[r - j]):
                polynomial[k] += factor * coefficient
        result.append(polynomial)
    return result


def evaluate(polynomial, value):
    return sum((a * value**i for i, a in enumerate(polynomial)), F(0))


def translate(polynomial, shift):
    return [
        sum(
            (
                polynomial[j] * comb(j, k) * shift ** (j - k)
                for j in range(k, len(polynomial))
            ),
            F(0),
        )
        for k in range(len(polynomial))
    ]


def recover_probabilities(moments):
    degree = len(moments) - 1
    return tuple(
        sum(
            (
                (-1) ** (k - j) * moments[k] / factorial(k - j)
                for k in range(j, degree + 1)
            ),
            F(0),
        )
        / factorial(j)
        for j in range(degree + 1)
    )


def check_law(probabilities, *, corrupt=False):
    """Compare cumulant-derived polynomials with direct finite-law moments."""
    degree = len(probabilities) - 1
    n = degree + 1
    cumulants = factorial_cumulants(probabilities, n)
    polynomials = moment_polynomials(cumulants)
    target = list(polynomials[n])
    if corrupt:
        target[0] += 1
    moments = [
        sum(
            (
                probabilities[x] * factorial(x) / factorial(x - r)
                for x in range(r, degree + 1)
            ),
            F(0),
        )
        for r in range(degree + 1)
    ]
    mean = moments[1]
    shifted = translate(target, mean)
    expected = [F(0)] + [comb(n, n - k) * moments[n - k] for k in range(1, n + 1)]
    if shifted != expected:
        raise AssertionError("Shifted-polynomial identity failed")
    assert shifted[0] == 0 and shifted[-1] == 1
    assert all(value >= 0 for value in shifted)
    actual_support = max(
        i for i, probability in enumerate(probabilities) if probability > 0
    )
    multiplicity = next(i for i, value in enumerate(shifted) if value)
    assert multiplicity == n - actual_support
    recovered_moments = [evaluate(p, mean) for p in polynomials[:n]]
    assert recovered_moments == moments
    assert recover_probabilities(recovered_moments) == tuple(probabilities)
    return target


def compositions(total, length):
    if length == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in compositions(total - first, length - 1):
                yield (first,) + tail


def run_checks():
    grid_count = 0
    for degree in range(1, 7):
        for weights in compositions(4, degree + 1):
            check_law(tuple(F(weight, 4) for weight in weights))
            grid_count += 1
    family_count = 0
    for degree in range(1, 9):
        for strength in (F(1, 5), F(1, 2), F(4, 5)):
            law = generalized_matching_law(degree, strength)
            check_law(law)
            cumulants = factorial_cumulants(law, degree + 1)
            assert cumulants[1] == strength
            assert all(k == 0 for k in cumulants[2 : degree + 1])
            assert cumulants[degree + 1] == -(strength ** (degree + 1))
            family_count += 1
    bernoulli = (F(1, 2), F(1, 2), F(0))
    assert check_law(bernoulli) == [F(1, 4), F(-3, 4), F(0), F(1)]
    assert check_law((F(0), F(0), F(1), F(0))) == [0, 16, -12, 0, 1]
    try:
        check_law(bernoulli, corrupt=True)
    except AssertionError as error:
        assert str(error) == "Shifted-polynomial identity failed"
    else:
        raise AssertionError("Deliberately changed coefficient was accepted")
    return {
        "status": "PASS",
        "grid_laws": grid_count,
        "generalized_matching_cases": family_count,
        "displayed_polynomials": 2,
        "changed_constant_rejected": True,
        "arithmetic": "fractions.Fraction; no floating-point decisions",
        "scope": "Finite identity controls from known laws, not a general solver or proof",
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
