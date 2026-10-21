"""Emit a Lean certificate request for exact rational D=1 feasibility.

This program does not decide the answer. A successful Lean kernel check of the
emitted theorem certifies the stated rational query under the encoded model.
Use --expect accept or reject to propose an answer; an incorrect proposal must
fail proof checking. The full Sage projection program is not verified here.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path
import re
import sys


PARAMETERS = {
    "source": ("B", "a", "c", "d", "e", "p"),
    "pair": ("B", "a", "c", "d", "e", "p", "b"),
    "nonempty": ("B", "a", "c", "d", "e"),
}
CHECKERS = {
    "source": "checkSource",
    "pair": "checkPair",
    "nonempty": "checkNonempty",
}
DEFINITIONS = {
    "source": ("checkSource", "sourceChecks"),
    "pair": ("checkPair",),
    "nonempty": ("checkNonempty", "nonemptyChecks", "positiveChecks", "linearLower"),
}
# Bound emitted terms and accept no decimal, expression, identifier or code.
RATIONAL = re.compile(r"[+-]?(?:0|[1-9][0-9]{0,63})(?:/[1-9][0-9]{0,63})?\Z")


def parse_rational(value: str) -> Fraction:
    if not isinstance(value, str) or not RATIONAL.fullmatch(value):
        raise ValueError("use signed integers or n/d, with at most 64 digits per part")
    return Fraction(value)


def lean_rational(value: Fraction) -> str:
    return f"(({value.numerator}) / {value.denominator} : ℚ)"


def certificate(kind: str, accepted: bool, values: list[str]) -> str:
    """Return only a fixed-template theorem with normalized numeric literals."""
    if kind not in PARAMETERS or type(accepted) is not bool:
        raise ValueError("invalid query kind or expected verdict")
    names = PARAMETERS[kind]
    if len(values) != len(names):
        raise ValueError(f"{kind} requires {len(names)} values: {', '.join(names)}")
    rationals = [parse_rational(value) for value in values]
    terms = [lean_rational(value) for value in rationals]
    arguments = " ".join(f"({name} := {term})" for name, term in zip(names, terms))
    real_terms = [f"({term} : ℝ)" for term in terms]
    if kind == "pair":
        proposition = "CountConfidenceExecutable.PairFeasible " + " ".join(real_terms)
    else:
        proposition = "CountConfidenceProjection.Feasible " + " ".join(real_terms)
        if kind == "nonempty":
            proposition = "∃ p : ℝ, " + proposition + " p"
    if not accepted:
        proposition = f"¬ ({proposition})"
    verdict = "true" if accepted else "false"
    theorem = f"CountConfidenceExecutable.{CHECKERS[kind]}_eq_{verdict}_iff"
    definitions = ", ".join(
        "CountConfidenceExecutable." + name for name in DEFINITIONS[kind]
    )
    normalized = ", ".join(f"{name}={value}" for name, value in zip(names, rationals))
    return (
        "import CountConfidenceExecutable\n\n"
        "-- Proposed answer only: successful kernel checking is required.\n"
        f"-- {kind}: {normalized}; expected {verdict}.\n"
        "set_option maxRecDepth 4096\n"
        "set_option maxHeartbeats 400000\n\n"
        f"theorem certificate :\n    {proposition} := by\n"
        f"  apply ({theorem} {arguments}).mp\n"
        f"  norm_num [{definitions}]\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=tuple(PARAMETERS), required=True)
    parser.add_argument("--expect", choices=("accept", "reject"), required=True)
    parser.add_argument(
        "--values",
        required=True,
        metavar="CSV",
        help="comma-separated exact values in B,a,c,d,e[,p[,b]] order; use --values=...",
    )
    parser.add_argument("--output", type=Path, help="new .lean file; default: stdout")
    args = parser.parse_args()
    try:
        result = certificate(args.kind, args.expect == "accept", args.values.split(","))
        if args.output is None:
            sys.stdout.buffer.write(result.encode("utf-8"))
        else:
            if args.output.suffix != ".lean":
                raise ValueError("output must be a new .lean file")
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(result)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
