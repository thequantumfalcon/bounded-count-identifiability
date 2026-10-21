"""Bounded deterministic differential fuzzing; finite software checks, not proof."""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from math import factorial
from pathlib import Path

import bounded_counts as library
from bounded_counts import core

MAX_BYTES = 17
MAX_DEGREE = 8
MAX_ORDER = 8
MAX_ITERATIONS = 10_000
DEFAULT_SEED = 20261021


def require(condition, message):
    """Keep checks active with Python -O too."""
    if not condition:
        raise AssertionError(message)


def pgf_coefficients(law, order):
    """Form sum p[x]*(1+t)**x by repeated polynomial multiplication."""
    result = [F(0)] * (order + 1)
    power = [F(1)] + [F(0)] * order
    for mass in law:
        for r in range(order + 1):
            result[r] += mass * power[r]
        power = [power[0]] + [power[r] + power[r - 1] for r in range(1, order + 1)]
    return result


def partitions(total, minimum=1):
    """Integer partitions represented by sorted block sizes (n <= MAX_ORDER)."""
    if total == 0:
        yield ()
    for first in range(minimum, total + 1):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def partition_cumulants(coefficients):
    """Moment/cumulant set-partition identity, grouped by block sizes.

    If a_j is the coefficient of t**j in the factorial PGF, this sums
    n!*(-1)**(k-1)*(k-1)!*product(a_j**m_j/m_j!) over sum(j*m_j)=n.
    It uses neither the package's recurrence nor the tests' polynomial log.
    Python's Fraction and factorial remain shared trusted primitives.
    """
    result = [F(0)]
    for n in range(1, len(coefficients)):
        value = F(0)
        for blocks in partitions(n):
            term = F((-1) ** (len(blocks) - 1) * factorial(len(blocks) - 1))
            for size in set(blocks):
                multiplicity = blocks.count(size)
                term *= coefficients[size] ** multiplicity / factorial(multiplicity)
            value += term
        result.append(value * factorial(n))
    return tuple(result)


def matching_by_derangements(degree, strength):
    """Count permutations by fixed points, then thin those points independently."""
    derangements = [1, 0]
    for n in range(2, degree + 1):
        derangements.append((n - 1) * (derangements[-1] + derangements[-2]))
    result = [F(0)] * (degree + 1)
    for fixed in range(degree + 1):
        mass = F(
            derangements[degree - fixed], factorial(fixed) * factorial(degree - fixed)
        )
        # Repeated multiplication by (1-h)+h*z gives the retained-count law.
        retained = [F(1)]
        for _ in range(fixed):
            following = [F(0)] * (len(retained) + 1)
            for j, probability in enumerate(retained):
                following[j] += (1 - strength) * probability
                following[j + 1] += strength * probability
            retained = following
        for j, probability in enumerate(retained):
            result[j] += mass * probability
    return tuple(result)


def rejects(exception, operation, label):
    try:
        operation()
    except exception:
        return
    raise AssertionError(f"invalid input accepted: {label}")


def check_case(data, api=library):
    """Exercise a bounded byte-derived case; no I/O or package mutation."""
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError(f"input must be bytes of length at most {MAX_BYTES}")
    values = data.ljust(MAX_BYTES, b"\x00")
    degree, order = values[0] % (MAX_DEGREE + 1), values[1] % (MAX_ORDER + 1)
    background = F(values[2], 1 + values[3] % 16)
    denominator = 1 + values[5] % 16
    strength = F(values[4] % (denominator + 1), denominator)
    weights = list(values[8 : 9 + degree])
    if not any(weights):
        weights[values[6] % len(weights)] = 1
    law = tuple(F(weight, sum(weights)) for weight in weights)
    coefficients = pgf_coefficients(law, order)
    moments = tuple(value * factorial(r) for r, value in enumerate(coefficients))
    cumulants = partition_cumulants(coefficients)
    observed_coefficients = [
        sum(
            (
                coefficients[j] * background ** (r - j) / factorial(r - j)
                for j in range(r + 1)
            ),
            F(0),
        )
        for r in range(order + 1)
    ]
    observed_moments = tuple(
        value * factorial(r) for r, value in enumerate(observed_coefficients)
    )
    observed_cumulants = partition_cumulants(observed_coefficients)
    require(api.factorial_moments(iter(law), order) == moments, "source moments")
    require(api.factorial_cumulants(law, order) == cumulants, "source cumulants")
    require(
        api.factorial_cumulants_from_moments(moments) == cumulants, "moment transform"
    )
    require(
        api.poisson_added_factorial_moments(law, background, order) == observed_moments,
        "Poisson moments",
    )
    require(
        api.poisson_added_factorial_cumulants(law, background, order)
        == observed_cumulants,
        "Poisson cumulants",
    )
    require(observed_cumulants[2:] == cumulants[2:], "higher cumulant invariance")
    if order:
        require(observed_cumulants[1] == cumulants[1] + background, "mean shift")
    padding = values[6] % 3
    require(
        api.validate_law(law, support_bound=degree + padding)
        == law + (F(0),) * padding,
        "support padding",
    )
    require(
        api.validate_law(law + (F(0),), support_bound=degree) == law, "support trimming"
    )
    require(
        api.factorial_cumulants(law + (F(0),) * padding, order) == cumulants,
        "padding invariance",
    )
    require(
        api.generalized_matching_law(degree, strength)
        == matching_by_derangements(degree, strength),
        "matching distribution",
    )
    epsilon = F(1, 1 + values[7])
    rejects(
        ValueError, lambda: api.validate_law([-epsilon, 1 + epsilon]), "negative mass"
    )
    rejects(ValueError, lambda: api.validate_law([1, epsilon]), "normalization")
    rejects(ValueError, lambda: api.validate_law([0, 1], support_bound=0), "support")
    rejects(
        ValueError, lambda: api.factorial_moments(law, -1 - values[7]), "negative order"
    )
    rejects(
        ValueError,
        lambda: api.poisson_added_factorial_moments(law, -epsilon, order),
        "negative background",
    )
    rejects(
        ValueError,
        lambda: api.generalized_matching_law(degree, 1 + epsilon),
        "strength",
    )
    bad = (True, 0.5, "1", None)[values[7] % 4]
    rejects(TypeError, lambda: api.validate_law([bad]), "inexact probability")
    rejects(TypeError, lambda: api.factorial_moments(law, bad), "inexact order")
    rejects(
        TypeError,
        lambda: api.poisson_added_factorial_moments(law, bad, order),
        "inexact background",
    )


def corpus_cases():
    entries = json.loads(
        Path(__file__).with_name("corpus.json").read_text(encoding="utf-8")
    )
    return [(entry["name"], bytes.fromhex(entry["hex"])) for entry in entries]


def generated_cases(seed, iterations):
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**64:
        raise ValueError("seed must be an unsigned 64-bit integer")
    if (
        isinstance(iterations, bool)
        or not isinstance(iterations, int)
        or not 0 <= iterations <= MAX_ITERATIONS
    ):
        raise ValueError(f"iterations must be in [0, {MAX_ITERATIONS}]")
    for index in range(iterations):
        digest = hashlib.sha256(
            seed.to_bytes(8, "big") + index.to_bytes(8, "big")
        ).digest()
        yield f"generated-{index}", digest[:MAX_BYTES]


def run(seed=DEFAULT_SEED, iterations=1000):
    # Validate arguments even when there are no generated cases.
    generated = list(generated_cases(seed, iterations))
    corpus = corpus_cases()
    for name, data in corpus + generated:
        try:
            check_case(data)
        except Exception as exc:
            raise AssertionError(
                f"{name}; replay with --replay {data.hex()!r}: {exc}"
            ) from exc
    return {
        "status": "PASS",
        "mode": "bounded deterministic differential fuzzing",
        "seed": seed,
        "generated_cases": iterations,
        "corpus_cases": len(corpus),
        "maximum_degree": MAX_DEGREE,
        "maximum_order": MAX_ORDER,
        "maximum_input_bytes": MAX_BYTES,
        "source_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in {
                "target": Path(__file__),
                "corpus": Path(__file__).with_name("corpus.json"),
                "installed_core": Path(core.__file__),
            }.items()
        },
        "limits": "Finite synthetic software checks; no coverage-guided engine, universal proof, physical validation or independent human review.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument(
        "--replay", help="replay one hex-encoded input of at most 17 bytes"
    )
    args = parser.parse_args()
    if args.replay is not None:
        if len(args.replay) > 2 * MAX_BYTES:
            parser.error("replay input exceeds 17 bytes")
        try:
            data = bytes.fromhex(args.replay)
            check_case(data)
        except ValueError as exc:
            parser.error(str(exc))
        result = {"status": "PASS", "replayed_hex": data.hex()}
    else:
        try:
            result = run(args.seed, args.iterations)
        except ValueError as exc:
            parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
