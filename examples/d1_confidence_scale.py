"""Deterministic scale diagnostic for the documented D=1 confidence formula.

Run with Python 3.11+: python examples/d1_confidence_scale.py
Only the standard library is used. Rational outward square-root enclosures
bound the formula; this is not a simulation or a formal software proof.
Population-centered boxes are not typical-data, best-case or lower-bound claims.
"""

import json
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import isqrt

SCALE = 10**60


def point(x):
    return F(x), F(x)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def sub(x, y):
    return x[0] - y[1], x[1] - y[0]


def mul(x, y):
    products = [a * b for a in x for b in y]
    return min(products), max(products)


def maximum(*xs):
    return max(x[0] for x in xs), max(x[1] for x in xs)


def minimum(*xs):
    return min(x[0] for x in xs), min(x[1] for x in xs)


def sqrt_fraction(value):
    """Enclose a nonnegative rational using integer square roots."""
    value = F(value)
    if value < 0:
        raise ValueError("square-root argument must be nonnegative")
    floor_scaled = isqrt(value.numerator * SCALE**2 // value.denominator)
    low = F(floor_scaled, SCALE)
    high = low if low * low == value else F(floor_scaled + 1, SCALE)
    assert low * low <= value <= high * high
    return low, high


def sqrt_interval(bounds):
    return sqrt_fraction(bounds[0])[0], sqrt_fraction(bounds[1])[1]


def centered_projection(p, b, ceiling, windows, alpha=F(1, 20)):
    """Enclose projection endpoints for boxes centered at population moments.

    Exact rational parameters only. The box contains its true model point;
    arbitrary empirical boxes and emptiness decisions are outside this helper.
    """
    values = (p, b, ceiling, alpha)
    if any(isinstance(x, bool) or not isinstance(x, (int, F)) for x in values):
        raise TypeError("parameters must be exact integers or Fractions")
    p, b, ceiling, alpha = map(F, values)
    if (
        isinstance(windows, bool)
        or not isinstance(windows, int)
        or windows < 1
        or not 0 <= p <= 1
        or not 0 <= b <= ceiling
        or not 0 < alpha < 1
    ):
        raise ValueError("invalid model parameter or number of windows")
    mean, second = p + b, (p + b) ** 2 - p**2
    rho1 = sqrt_fraction(2 * (ceiling + F(1, 4)) / (windows * alpha))
    rho2 = sqrt_fraction(
        2 * (4 * ceiling**3 + 10 * ceiling**2 + 4 * ceiling) / (windows * alpha)
    )
    a = maximum(point(0), sub(point(mean), rho1))
    c = minimum(point(1 + ceiling), add(point(mean), rho1))
    d = maximum(point(0), sub(point(second), rho2))
    e = minimum(point(ceiling**2 + 2 * ceiling), add(point(second), rho2))
    if ceiling == 0:
        lower, upper = a, c
    else:
        lower = maximum(
            point(0),
            sub(a, point(ceiling)),
            sqrt_interval(maximum(point(0), sub(mul(a, a), e))),
            mul(sub(d, point(ceiling**2)), point(1 / (2 * ceiling))),
        )
        upper = minimum(point(1), c, sqrt_interval(sub(mul(c, c), d)))
    assert lower[0] <= p <= upper[1]
    return {"lower": lower, "upper": upper, "width": sub(upper, lower)}


def at_windows(windows):
    return centered_projection(F(3, 10), F(1, 2), 1, windows)


def width_at_most(windows, target):
    lower, upper = at_windows(windows)["width"]
    if upper <= target:
        return True
    if lower > target:
        return False
    raise ArithmeticError("width comparison unresolved at the chosen precision")


def first_centered_width(target):
    """Nested population-centered boxes justify this monotone binary search."""
    if isinstance(target, bool) or not isinstance(target, (int, F)):
        raise TypeError("target must be an exact integer or Fraction")
    if not 0 < target < 1:
        raise ValueError("target must be strictly between zero and one")
    low, high = 1, 1
    while not width_at_most(high, target):
        high *= 2
    while low < high:
        middle = (low + high) // 2
        if width_at_most(middle, target):
            high = middle
        else:
            low = middle + 1
    assert not width_at_most(low - 1, target) and width_at_most(low, target)
    return low


def describe(bounds):
    low, high = bounds
    with localcontext() as context:
        context.prec = 16
        middle = (low + high) / 2
        display = str(Decimal(middle.numerator) / Decimal(middle.denominator))
    return {"display_midpoint": display, "rational_enclosure": list(map(str, bounds))}


def main():
    threshold = first_centered_width(F(1, 10))
    result = {
        "parameters": {"p": "3/10", "b": "1/2", "B": "1", "alpha": "1/20"},
        "method": "Exact Fraction arithmetic and outward integer-isqrt bounds on a 10^-60 lattice; decimals only for display.",
        "population_centered_table": {
            str(10**k): {name: describe(x) for name, x in at_windows(10**k).items()}
            for k in range(4, 9)
        },
        "width_one_tenth": {
            "first_integer_N_for_population_centered_box": threshold,
            "previous_N_width": describe(at_windows(threshold - 1)["width"]),
            "at_N_width": describe(at_windows(threshold)["width"]),
        },
        "zero_background_comparison": {
            "parameters": {"p": "3/10", "b": "0", "B": "0", "N": 4000},
            "width": describe(centered_projection(F(3, 10), 0, 0, 4000)["width"]),
        },
        "scope": "Deterministic population-centered box diagnostic, not expected or best-case data performance, a sample-size lower bound, measurements, or formal software verification. Exactly centered empirical moments need not be attainable at each N.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
