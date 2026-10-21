"""Coverage-guided input generation for the bounded exact differential oracle."""

# Load harness-only standard-library modules before instrumenting our package.
import argparse  # noqa: F401
from fractions import Fraction  # noqa: F401
import hashlib  # noqa: F401
import json  # noqa: F401
from math import factorial  # noqa: F401
from pathlib import Path  # noqa: F401
import sys
from types import SimpleNamespace

import atheris

# Both the package and the existing differential harness are imported here.
# No package code may be imported earlier: Atheris instruments on first import.
with atheris.instrument_imports():
    import exact_counts


FAULT_FLAG = "--fault-control"
FAULT_MARKER = "BCI_DELIBERATE_FAULT_DETECTED"
FAULT_CONTROL = FAULT_FLAG in sys.argv
API = exact_counts.library
if FAULT_CONTROL:
    sys.argv.remove(FAULT_FLAG)
    API = SimpleNamespace(
        **{key: getattr(API, key) for key in exact_counts.library.__all__}
    )

    def faulty_moments(*args, **kwargs):
        values = exact_counts.library.factorial_moments(*args, **kwargs)
        return (values[0] + 1,) + values[1:]

    # Change only the injected API, never the installed package or oracle.
    API.factorial_moments = faulty_moments


@atheris.instrument_func
def test_one_input(data):
    if len(data) > exact_counts.MAX_BYTES:
        return
    try:
        exact_counts.check_case(data, API)
    except AssertionError as exc:
        if FAULT_CONTROL and str(exc) == "source moments":
            raise RuntimeError(FAULT_MARKER) from exc
        raise


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
