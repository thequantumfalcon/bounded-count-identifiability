# Reproduction

Successful computations do not establish physical assumptions or originality.

## Exact Python example

Use Python 3.11 or newer. From the root, create a virtual environment:

```sh
python -m venv .venv
```

Activate with `.venv/Scripts/Activate.ps1` in PowerShell or
`source .venv/bin/activate` in a POSIX shell. Then run:

```sh
python -m pip install .
python -m bounded_counts --degree 3 --strength 1/2
python -m bounded_counts --degree 3 --strength 1/2 --json
```

The package has no runtime dependencies. This example has source masses
`(29/48, 5/16, 1/16, 1/48)` and factorial cumulants `(1/2, 0, 0, -1/16)`.
The comparison source is a point mass at zero. Shifting the backgrounds by
`1/2` makes the observed cumulants agree through order three and differ at
order four. Fractions are exact.

## Development and packaged artifacts

The development lock fixes versions and accepted download hashes. In the
activated environment, run the following with Python 3.11.4 or newer (the
artifact checker requires its safe tar extraction API):

```sh
python tools/tasks.py setup
python tools/tasks.py lint
python tools/tasks.py test
python tools/tasks.py build
python tools/tasks.py artifacts
```

Tests import the installed package. The artifact task installs the wheel in
a fresh isolated environment, runs tests and the CLI, safely extracts the
source distribution, rebuilds its wheel, and repeats those checks. Keep `dist/`
for this build only; ambiguous multiple artifacts cause rejection.
`python tools/tasks.py release` combines the local checks and publishes nothing.

The 95% statement-and-branch coverage gate applies to the Python package, not
the proofs, examples or developer utilities. Coverage is not mathematical
correctness. Tests include a separate formal-logarithm computation, finite-law
transformations and the known sharpness family.

CI exercises Python on Linux and Windows and compiles Lean on Linux. Inspect
the actual commit's Actions results: configuration alone is not a successful
run. No package has been published to PyPI.

## Formal proof

Follow [lean/README.md](../lean/README.md) to build all six modules with pinned
dependencies. Its verifier recompiles into fresh output, checks source hashes
and printed axiom lists, and records a uniquely named run. Upstream compiled
mathlib caches are used; this is not a source rebuild of every trusted component.

The committed local receipt used existing dependency artifacts and says so.
The separate initial hosted run also passed after fresh dependency retrieval;
its Linux receipt is preserved in the verification record.
Git attributes preserve its referenced proof bytes. See
[the verification record](../evidence/README.md) for extra development checker
runs and their reproducibility limits.

## Optional exact Sage projection

With SageMath installed, run from the root:

```sh
sage -python examples/d1_projection_sage.py --self-test
```

Checked with SageMath 10.8, this script projects a supplied moment box for the
Bernoulli-plus-Poisson model using exact algebraic arithmetic. Tests cover
boundaries, exact rational membership comparisons and feasible witnesses.
Output is JSON; `--help` describes inputs. It does not construct empirical
confidence intervals or collect data. The separate conditional coverage
argument is in [claims.md](claims.md).
