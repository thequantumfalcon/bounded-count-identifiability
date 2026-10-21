"""Independent finite rational controls for the finite mixed-Poisson formulas.

No repository arithmetic, cumulant, or fixture modules are imported. FLINT
forms exp(r*t)*(1+p*t), mixes it, and takes a formal logarithm through t^8.
Retained coefficients are exact; truncation is not an analytic tail bound.
"""

import hashlib
import json
from math import factorial
from pathlib import Path
import platform
import sys

import flint
from flint import fmpq as Q, fmpq_series as Series


ORDER = 8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def qsum(values):
    return sum(values, Q(0))


def observe(p, weights, rates):
    require(Q(0) <= p <= Q(1), "Bernoulli parameter")
    require(len(weights) == len(rates) and bool(weights), "nonempty matched atoms")
    require(all(w >= 0 for w in weights), "nonnegative weights")
    require(qsum(weights) == 1, "normalized weights")
    require(all(r >= 0 for r in rates), "nonnegative rates")
    t = Series([0, 1], prec=ORDER + 1)
    generating = Series([0], prec=ORDER + 1)
    for w, r in zip(weights, rates):
        generating += w * (r * t).exp() * (1 + p * t)
    require(generating.prec >= ORDER + 1, "sufficient PGF precision")
    require(generating[0] == 1, "PGF normalization")
    logarithm = generating.log()
    require(logarithm.prec >= ORDER + 1, "sufficient logarithm precision")
    moments = [generating[n] * factorial(n) for n in range(ORDER + 1)]
    cumulants = [logarithm[n] * factorial(n) for n in range(ORDER + 1)]
    mean_rate = qsum(w * r for w, r in zip(weights, rates))
    variance = qsum(w * (r - mean_rate) ** 2 for w, r in zip(weights, rates))
    third_rate = qsum(w * (r - mean_rate) ** 3 for w, r in zip(weights, rates))
    return moments, cumulants, mean_rate, variance, third_rate


def fixture(name, p, weights, rates, lower=None, upper=None):
    p = Q(p)
    weights = tuple(Q(w) for w in weights)
    rates = tuple(Q(r) for r in rates)
    lower = min(rates) if lower is None else Q(lower)
    upper = max(rates) if upper is None else Q(upper)
    return name, p, weights, rates, lower, upper


def fixtures():
    yield fixture("zero-law", 0, [1], [0])
    yield fixture("bernoulli-one-zero-background", 1, [1], [0])
    yield fixture("single-positive-rate", Q(2, 5), [1], [Q(7, 3)])
    yield fixture("equal-rates", Q(1, 3), [Q(1, 4), Q(3, 4)], [Q(5, 2)] * 2)
    yield fixture("zero-weight-outlier", Q(1, 2), [1, 0], [0, 11])
    yield fixture(
        "sharp-equal-endpoint-mixture", Q(2, 7), [Q(1, 2)] * 2, [Q(1, 5), Q(13, 5)]
    )
    yield fixture(
        "asymmetric-three-atom",
        Q(3, 5),
        [Q(1, 7), Q(2, 7), Q(4, 7)],
        [0, Q(1, 2), Q(7, 3)],
    )
    yield fixture(
        "zero-weight-pure-background", 0, [0, Q(1, 4), Q(3, 4)], [0, Q(1, 3), Q(5, 4)]
    )
    yield fixture(
        "nonsharp-range-with-negative-lower-bound", 1, [Q(1, 2)] * 2, [0, 2], -1, 3
    )
    rate_grid = (Q(0), Q(1, 4), Q(1), Q(3))
    parameter_grid = (Q(0), Q(1, 3), Q(1, 2), Q(1))
    count = 0
    for p in parameter_grid:
        for a in rate_grid:
            for b in rate_grid:
                for c in rate_grid:
                    for numerator_a in range(4):
                        for numerator_b in range(4 - numerator_a):
                            w = (
                                Q(numerator_a, 3),
                                Q(numerator_b, 3),
                                Q(3 - numerator_a - numerator_b, 3),
                            )
                            yield fixture(f"grid-{count}", p, w, (a, b, c))
                            count += 1
    require(count == 2560, "grid enumeration")


def reject_wrong(label, actual, wrong):
    try:
        require(actual == wrong, label)
    except AssertionError:
        return {
            "name": label,
            "actual": str(actual),
            "deliberately_wrong": str(wrong),
            "rejected": True,
        }
    raise AssertionError("wrong formula was not rejected: " + label)


def main():
    flint.ctx.cap = ORDER + 1
    source_hash = sha(__file__)
    boundary_outputs = []
    fixture_count = 0
    cached = []
    sharp = 0
    for name, p, weights, rates, lower, upper in fixtures():
        moments, cumulants, mean_rate, variance, third_rate = observe(p, weights, rates)
        require(all(lower <= r <= upper for r in rates), "range premise: " + name)
        require(lower <= mean_rate <= upper, "mean in rate range: " + name)
        for n in range(1, ORDER + 1):
            formula = qsum(
                w * (r**n + n * p * r ** (n - 1)) for w, r in zip(weights, rates)
            )
            require(moments[n] == formula, f"factorial moment order {n}: {name}")
        require(moments[1] == p + mean_rate, "observed mean: " + name)
        require(
            cumulants[2] == moments[2] - moments[1] ** 2, "second from log: " + name
        )
        require(cumulants[2] == -(p**2) + variance, "second correction: " + name)
        require(cumulants[3] == 2 * p**3 + third_rate, "third correction: " + name)
        bound = (upper - lower) ** 2 / 4
        intermediate = (upper - mean_rate) * (mean_rate - lower)
        require(
            Q(0) <= variance <= intermediate <= bound, "range variance bound: " + name
        )
        count_variance = moments[2] + moments[1] - moments[1] ** 2
        factorial_two_variance = (
            moments[4] + 4 * moments[3] + 2 * moments[2] - moments[2] ** 2
        )
        conditional_second = tuple(r**2 + 2 * p * r for r in rates)
        between_second = qsum(
            w * (g - moments[2]) ** 2 for w, g in zip(weights, conditional_second)
        )
        within_second = qsum(
            w * (4 * r**3 + (12 * p + 2 - 4 * p**2) * r**2 + 4 * p * r)
            for w, r in zip(weights, rates)
        )
        require(
            count_variance == mean_rate + p * (1 - p) + variance,
            "count total variance: " + name,
        )
        require(
            factorial_two_variance == within_second + between_second,
            "factorial-two total variance: " + name,
        )
        first_ceiling = upper + Q(1, 4) + upper**2 / 4
        second_ceiling = (
            4 * upper**3 + 10 * upper**2 + 4 * upper + (upper**2 + 2 * upper) ** 2 / 4
        )
        require(Q(0) <= count_variance <= first_ceiling, "first ceiling: " + name)
        require(
            Q(0) <= factorial_two_variance <= second_ceiling,
            "second ceiling: " + name,
        )
        sharp += variance == bound and upper > lower
        fixture_count += 1
        if not name.startswith("grid-"):
            boundary_outputs.append(
                {
                    "name": name,
                    "p": str(p),
                    "weights": list(map(str, weights)),
                    "rates": list(map(str, rates)),
                    "lower": str(lower),
                    "upper": str(upper),
                    "observed_mean": str(moments[1]),
                    "second_factorial_cumulant": str(cumulants[2]),
                    "third_factorial_cumulant": str(cumulants[3]),
                    "rate_mean": str(mean_rate),
                    "rate_variance": str(variance),
                    "variance_bound": str(bound),
                    "count_variance": str(count_variance),
                    "factorial_two_variance": str(factorial_two_variance),
                    "count_variance_ceiling": str(first_ceiling),
                    "factorial_two_variance_ceiling": str(second_ceiling),
                }
            )
        cached.append((p, moments[1], cumulants[2], mean_rate, variance))
    require(sharp > 0, "nontrivial sharpness example")

    # Check stability without a numerical square root: both sides are nonnegative.
    # For the background inequality, square max(0, |rate gap|-delta).
    for left, right in zip(cached, cached[1:]):
        p, mu, second, rate, var = left
        q, nu, other_second, other_rate, other_var = right
        epsilon, delta, eta = (
            abs(second - other_second),
            abs(mu - nu),
            max(var, other_var),
        )
        require((p - q) ** 2 <= epsilon + eta, "squared source stability")
        residual = max(Q(0), abs(rate - other_rate) - delta)
        require(residual**2 <= epsilon + eta, "squared background stability")

    ambiguities = []
    for h in (Q(0), Q(1, 10), Q(1, 3), Q(1, 2), Q(1)):
        mixed = observe(h, (Q(1, 2), Q(1, 2)), (Q(0), 2 * h))
        fixed = observe(Q(0), (Q(1),), (2 * h,))
        require(mixed[0][1:3] == fixed[0][1:3], "two observed factorial moments match")
        require(
            mixed[1][1:3] == fixed[1][1:3], "two observed factorial cumulants match"
        )
        require(mixed[1][2] == 0, "zero common second cumulant")
        gap = mixed[1][3] - fixed[1][3]
        require(gap == 2 * h**3, "third-order ambiguity gap")
        require(mixed[3] == h**2, "source-stability equality example")
        if h:
            require(gap > 0, "strict third-order separation")
        ambiguities.append(
            {
                "h": str(h),
                "mean": str(mixed[0][1]),
                "second_moment": str(mixed[0][2]),
                "second_cumulant": str(mixed[1][2]),
                "third_cumulant_gap": str(gap),
                "variance_allowance": str(mixed[3]),
            }
        )

    sample = observe(Q(1, 2), (Q(1, 2), Q(1, 2)), (Q(0), Q(2)))
    control_h = Q(1, 2)
    control_mixed = observe(control_h, (Q(1, 2), Q(1, 2)), (Q(0), 2 * control_h))
    control_fixed = observe(Q(0), (Q(1),), (2 * control_h,))
    control_third_gap = control_mixed[1][3] - control_fixed[1][3]
    controls = [
        reject_wrong("omit mixing variance", sample[1][2], -(Q(1, 2) ** 2)),
        reject_wrong(
            "wrong Bernoulli second-cumulant sign",
            sample[1][2],
            Q(1, 2) ** 2 + sample[3],
        ),
        reject_wrong(
            "wrong third-order ambiguity gap", control_third_gap, control_h**3
        ),
    ]
    require(sample[3] > Q(2) ** 2 / 8, "reject invalid universal range-squared/8 bound")
    controls.append(
        {
            "name": "range-squared/8 asserted as universal upper bound",
            "actual_variance": str(sample[3]),
            "deliberately_wrong_bound": "1/2",
            "rejected": True,
        }
    )

    # A bounded random rate can violate both fixed-rate variance ceilings.
    mixed_boundary = observe(Q(1), (Q(1, 2), Q(1, 2)), (Q(0), Q(8)))[0]
    for label, actual, wrong in (
        (
            "fixed-rate first variance ceiling applied to a mixture",
            mixed_boundary[2] + mixed_boundary[1] - mixed_boundary[1] ** 2,
            Q(8) + Q(1, 4),
        ),
        (
            "fixed-rate second variance ceiling applied to a mixture",
            mixed_boundary[4]
            + 4 * mixed_boundary[3]
            + 2 * mixed_boundary[2]
            - mixed_boundary[2] ** 2,
            Q(4 * 8**3 + 10 * 8**2 + 4 * 8),
        ),
    ):
        require(actual > wrong, label)
        controls.append(
            {
                "name": label,
                "actual_variance": str(actual),
                "deliberately_wrong_bound": str(wrong),
                "rejected": True,
            }
        )

    # Conditional independence given one shared rate does not yield the
    # unconditional pairwise independence needed by the sampling theorem.
    # With p=0 and shared rate 0 or 1 equally, rate=0 forces every count to 0.
    n, alpha, ceiling = 1000, Q(1, 20), Q(3, 2)
    radius_squared = 2 * ceiling / (n * alpha)
    zero_rate_error_squared = Q(1, 2) ** 2
    actual_mean_variance = Q(1, 2) / n + Q(1, 4)
    require(actual_mean_variance > ceiling / n, "reject shared-rate variance/N")
    require(zero_rate_error_squared > radius_squared, "shared-zero-rate failure")
    require(Q(1, 2) > alpha, "shared-rate failure probability exceeds alpha")
    shared_rate_control = {
        "windows": n,
        "alpha": str(alpha),
        "single_window_ceiling": str(ceiling),
        "actual_sample_mean_variance": str(actual_mean_variance),
        "incorrect_variance_ceiling": str(ceiling / n),
        "radius_squared": str(radius_squared),
        "error_squared_on_zero_rate_event": str(zero_rate_error_squared),
        "failure_probability_lower_bound": "1/2",
        "scope": "Exact arithmetic for the documented shared-latent-rate counterexample; its probability interpretation is a written argument, not a proof-assistant check.",
    }

    require(source_hash == sha(__file__), "source unchanged")
    no_production_imports = not any(
        name == "bounded_counts" or name.startswith("bounded_counts.")
        for name in sys.modules
    )
    require(no_production_imports, "no production arithmetic import")
    record = {
        "schema_version": 1,
        "status": "PASS",
        "python": platform.python_version(),
        "python_flint": flint.__version__,
        "flint": flint.__FLINT_VERSION__,
        "arithmetic": "FLINT exact rational truncated power series exp and log",
        "maximum_order": ORDER,
        "series_precision": ORDER + 1,
        "source_sha256": source_hash,
        "source_unchanged": True,
        "no_production_arithmetic_imports": no_production_imports,
        "fixture_count": fixture_count,
        "moment_formula_comparisons": fixture_count * ORDER,
        "adjacent_pair_stability_checks": len(cached) - 1,
        "total_variance_identity_checks": 2 * fixture_count,
        "sampling_variance_ceiling_checks": 2 * fixture_count,
        "nonconstant_sharp_variance_examples": int(sharp),
        "deliberately_wrong_formulas": controls,
        "two_moment_ambiguity": ambiguities,
        "boundary_fixtures": boundary_outputs,
        "shared_rate_dependence_control": shared_rate_control,
        "limits": {
            "maximum_mixture_atoms": 3,
            "maximum_rate": 11,
            "maximum_order": ORDER,
            "fixed_grid_cases": 2560,
            "named_boundary_cases": 9,
        },
        "scope": "Finite exact controls through order eight, with an arithmetic implementation distinct from the repository's Fraction routines. Not a universal proof, proof-assistant execution, independent human review, physical calibration or validation. FLINT, Python and the explicit coefficient-to-moment interpretation remain trusted.",
    }
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
