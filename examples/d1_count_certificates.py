"""Propose a Lean certificate for a small explicit record of natural counts.

Exact Python arithmetic proposes averages, outward radii and box endpoints.
Only successful Lean checking certifies the encoded record and inequalities.
Acquisition, parsing, window independence and the observation law are not proved.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from math import isqrt
from pathlib import Path
import re
import sys


MAX_COUNTS = 64
COUNT = re.compile(r"(?:0|[1-9][0-9]{0,11})\Z")
RATIONAL = re.compile(r"[+-]?(?:0|[1-9][0-9]{0,63})(?:/[1-9][0-9]{0,63})?\Z")
FIELDS = ("B", "alpha", "R1", "R2", "m1", "m2", "a", "c", "d", "e")


def rational(value: str) -> Fraction:
    if not isinstance(value, str) or not RATIONAL.fullmatch(value):
        raise ValueError("use an integer or n/d with at most 64 digits per part")
    return Fraction(value)


def parse_counts(values: list[str]) -> tuple[int, ...]:
    if not isinstance(values, list) or not 1 <= len(values) <= MAX_COUNTS:
        raise ValueError(f"provide 1 through {MAX_COUNTS} explicit counts")
    if any(not isinstance(x, str) or not COUNT.fullmatch(x) for x in values):
        raise ValueError("counts must be unsigned integers of at most 12 digits")
    return tuple(int(x) for x in values)


def sqrt_upper(value: Fraction, digits: int) -> Fraction:
    """Smallest grid point k/10**digits whose square is at least value."""
    if type(value) is not Fraction or value < 0:
        raise ValueError("square-root input must be a nonnegative Fraction")
    if type(digits) is not int or not 0 <= digits <= 12:
        raise ValueError("digits must be an integer from 0 through 12")
    scale = 10**digits
    numerator = value.numerator * scale**2
    k = isqrt(numerator // value.denominator)
    if k * k * value.denominator < numerator:
        k += 1
    return Fraction(k, scale)


def prepare(
    counts: list[str], background: str, alpha: str, digits: int = 6
) -> tuple[tuple[int, ...], dict[str, Fraction]]:
    observed = parse_counts(counts)
    B, error = rational(background), rational(alpha)
    if B < 0 or not 0 < error < 1:
        raise ValueError("require background ceiling >= 0 and 0 < alpha < 1")
    N = len(observed)
    m1 = Fraction(sum(observed), N)
    m2 = Fraction(sum(y * (y - 1) for y in observed), N)
    R1 = sqrt_upper(2 * (B + Fraction(1, 4)) / (N * error), digits)
    R2 = sqrt_upper(2 * (4 * B**3 + 10 * B**2 + 4 * B) / (N * error), digits)
    return observed, dict(
        zip(FIELDS, (B, error, R1, R2, m1, m2, m1 - R1, m1 + R1, m2 - R2, m2 + R2))
    )


def render(counts: tuple[int, ...], values: dict[str, Fraction]) -> str:
    """Render proposed numeric answers, which the Lean checker must validate.

    Accepting incorrect answers here is intentional: the runner tests their rejection.
    Only fixed syntax and bounded natural/rational numeric literals are emitted.
    """
    if not isinstance(counts, tuple) or any(type(x) is not int for x in counts):
        raise ValueError("encoded counts must be a tuple of integers")
    parse_counts([str(x) for x in counts])
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        raise ValueError("unexpected proposed fields")
    if any(type(x) is not Fraction for x in values.values()):
        raise ValueError("proposed values must be exact Fractions")
    # A bounded input can produce larger intermediate fractions. Bound generated
    # literals as well, including callers supplying their own proposed answers.
    if any(
        max(len(str(abs(x.numerator))), len(str(x.denominator))) > 512
        for x in values.values()
    ):
        raise ValueError("proposed rational exceeds the 512-digit output bound")
    terms = {
        name: f"(({x.numerator}) / {x.denominator} : ℚ)" for name, x in values.items()
    }
    return (
        "import CountCountsConfidence\n\n"
        "-- Proposed arithmetic only; successful kernel checking is required.\n"
        "-- Coverage additionally requires the laws and independence in the universal theorem.\n"
        "set_option maxRecDepth 8192\n"
        "set_option maxHeartbeats 800000\n\n"
        f"def observations : Fin {len(counts)} → ℕ := ![{', '.join(map(str, counts))}]\n\n"
        "open CountCountsConfidence\n\n"
        "theorem certificate :\n"
        f"    firstMean observations = {terms['m1']} ∧\n"
        f"    secondMean observations = {terms['m2']} ∧\n"
        f"    checkRadii {len(counts)} {terms['B']} {terms['alpha']} {terms['R1']} {terms['R2']} = true ∧\n"
        f"    firstMean observations - {terms['R1']} = {terms['a']} ∧\n"
        f"    firstMean observations + {terms['R1']} = {terms['c']} ∧\n"
        f"    secondMean observations - {terms['R2']} = {terms['d']} ∧\n"
        f"    secondMean observations + {terms['R2']} = {terms['e']} := by\n"
        "  norm_num [observations, firstMean, secondMean, checkRadii, radiusChecks,\n"
        "    Fin.sum_univ_succ, Nat.descFactorial]\n"
    )


def certificate(counts: list[str], background: str, alpha: str, digits: int = 6) -> str:
    return render(*prepare(counts, background, alpha, digits))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--counts", required=True, help="comma-separated natural counts"
    )
    parser.add_argument(
        "--background", required=True, help="fixed exact background ceiling"
    )
    parser.add_argument("--alpha", required=True, help="preselected exact error level")
    parser.add_argument("--digits", type=int, default=6)
    parser.add_argument("--output", type=Path, help="new .lean file; default: stdout")
    args = parser.parse_args()
    try:
        text = certificate(
            args.counts.split(","), args.background, args.alpha, args.digits
        )
        if args.output is None:
            sys.stdout.buffer.write(text.encode("utf-8"))
        else:
            if args.output.suffix != ".lean":
                raise ValueError("output must be a new .lean file")
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
