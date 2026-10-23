"""Generate exact browser fixtures from the installed Python package.

Run with the development environment after installing the package. The output
contains synthetic population calculations, not observations or a proof of
the JavaScript implementation. No machine paths or timestamps are retained.
"""

import argparse
import json
import sys
from fractions import Fraction as F
from importlib.metadata import version
from pathlib import Path
from random import Random

import bounded_counts
from bounded_counts import generalized_matching_law, poisson_added_factorial_cumulants

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "demo" / "tests" / "fixtures.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare regenerated fixtures with the saved file without writing",
    )
    args = parser.parse_args()
    package_path = Path(bounded_counts.__file__).resolve()
    if package_path.is_relative_to(ROOT / "src"):
        raise RuntimeError(
            "Install the package; fixtures must not import repository src/."
        )

    fixtures = []

    def append(name, law, order, background, **details):
        fixtures.append(
            {
                "name": name,
                "law": list(map(str, law)),
                "order": order,
                "background": str(background),
                "cumulants": list(
                    map(str, poisson_added_factorial_cumulants(law, background, order))
                ),
                **details,
            }
        )

    for degree in range(1, 9):
        for tenth in range(11):
            strength = F(tenth, 10)
            law = generalized_matching_law(degree, strength)
            for background in (F(0), F(1, 2), F(3)):
                append(
                    f"matching-D{degree}-h{strength}-b{background}",
                    law,
                    degree + 1,
                    background,
                    family="matching",
                    degree=degree,
                    strength=str(strength),
                )

    random = Random(20261022)
    for index in range(48):
        degree = index % 9
        masses = [random.randrange(20) for _ in range(degree + 1)]
        if not any(masses):
            masses[0] = 1
        law = tuple(F(value, sum(masses)) for value in masses)
        append(
            f"rational-law-{index}",
            law,
            min(10, degree + 2),
            F(random.randrange(301), 100),
            family="arbitrary",
        )

    for p in (F(0), F(1, 10), F(3, 10), F(1, 2), F(1)):
        for b in (F(0), F(1, 2), F(3)):
            append(
                f"bernoulli-p{p}-b{b}",
                (1 - p, p),
                4,
                b,
                family="bernoulli",
                probability=str(p),
            )

    result = {
        "schema": 1,
        "generator": "tools/generate_demo_fixtures.py",
        "oracle": "installed bounded_counts package",
        "package_version": version("bounded-count-identifiability"),
        "scope": "Exact synthetic population cases; finite software comparisons, not a universal proof or measured data.",
        "cases": fixtures,
    }
    expected = json.dumps(result, indent=2) + "\n"
    if args.check:
        if (
            not DESTINATION.is_file()
            or DESTINATION.read_text(encoding="utf-8") != expected
        ):
            print(
                "Demo fixtures differ from the installed package; regenerate and review them.",
                file=sys.stderr,
            )
            return 1
        print(f"Verified {len(fixtures)} exact cases against the installed package")
        return 0
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(expected, encoding="utf-8")
    print(f"Wrote {len(fixtures)} exact cases to demo/tests/fixtures.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
