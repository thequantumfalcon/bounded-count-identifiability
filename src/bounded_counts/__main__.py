"""Reproduce an exact lower-order ambiguity with two specified source models."""

import argparse
import json
from collections.abc import Sequence
from fractions import Fraction

from .core import generalized_matching_law, poisson_added_factorial_cumulants


def _strength(text: str) -> Fraction:
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError(
            "strength must be an exact rational such as 1/2"
        ) from exc
    if not 0 < value < 1:
        raise argparse.ArgumentTypeError("this demonstration requires 0 < strength < 1")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--degree", type=int, default=3, help="known support bound D >= 1 (default: 3)"
    )
    parser.add_argument(
        "--strength",
        type=_strength,
        default=Fraction(1, 2),
        help="exact rational h in (0,1), default: 1/2",
    )
    parser.add_argument(
        "--json", action="store_true", help="write exact fractions as JSON strings"
    )
    args = parser.parse_args(argv)
    if args.degree < 1:
        parser.error("degree must be at least 1 to demonstrate two distinct sources")

    degree, h = args.degree, args.strength
    source_a = generalized_matching_law(degree, h)
    source_b = (Fraction(1),) + (Fraction(0),) * degree
    ka = poisson_added_factorial_cumulants(source_a, 0, degree + 1)
    kb = poisson_added_factorial_cumulants(source_b, h, degree + 1)
    result = {
        "degree": degree,
        "strength": str(h),
        "model": "Y=X+Z with independent Z~Poisson(b), fixed b per window",
        "orders": list(range(1, degree + 2)),
        "source_a": {
            "probabilities": list(map(str, source_a)),
            "background": "0",
            "observed_factorial_cumulants": list(map(str, ka[1:])),
        },
        "source_b": {
            "probabilities": list(map(str, source_b)),
            "background": str(h),
            "observed_factorial_cumulants": list(map(str, kb[1:])),
        },
        "equal_through_degree": ka[1 : degree + 1] == kb[1 : degree + 1],
        "different_at_degree_plus_one": ka[degree + 1] != kb[degree + 1],
        "family_reference": "https://arxiv.org/abs/1411.1165, Eq. (3.1) and Lemma 3.1; credits Niermann (1999)",
        "scope": "Exact population-model calculation using an established family; no measured data or physical validation.",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Exact count example: D={degree}, h={h}")
        print("A: generalized matching source, independent Poisson background b=0")
        print(f"   probabilities: {', '.join(map(str, source_a))}")
        print(f"B: zero-count source, independent Poisson background b={h}")
        print("order | observed factorial cumulant A | observed factorial cumulant B")
        for r in result["orders"]:
            print(f"{r} | {ka[r]} | {kb[r]}")
        print(
            f"The observed cumulants agree through order {degree} and differ at order {degree + 1}."
        )
        print(
            "Known family: Afendras-Papadatos, arXiv:1411.1165, crediting Niermann (1999)."
        )
        print(result["scope"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
