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
python tools/tasks.py fuzz
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

The [bounded fuzz runner](../fuzz/README.md) adds seeded differential checks
against an integer-partition cumulant calculation, plus exact transformation
identities. `python tools/tasks.py fuzz` fixes the seed and runs 1,000 generated
cases after the saved corpus. Installed wheel and rebuilt-source checks also run
a smaller 100-case sample. These finite checks can expose software defects;
they are not universal proofs.

The required Linux fuzz job also runs Atheris coverage-guided generation using
the same exact oracles, then checks an injected API fault and genuine replay.
To reproduce that extra check on Linux x86_64 with CPython 3.12, 3.13 or 3.14:

```sh
python -m pip install --require-hashes --only-binary=:all: --no-deps -r fuzz/requirements.txt
python fuzz/run_atheris.py --output build/atheris-local --seconds 60
```

Choose a fresh output directory. The receipt preserves source hashes, engine
statistics, corpus inputs and process logs. Read the [fuzz guide](../fuzz/README.md)
for resource bounds, replay commands and interpretation. Coverage-guided input
generation still shares the existing oracle and is a finite software check.

CI exercises Python on Linux and Windows, compiles Lean on Linux, and includes
separate exact Sage projection and FLINT finite-mixture jobs. Inspect
the actual commit's Actions results: configuration alone is not a successful
run. No package has been published to PyPI.

## Separate finite-mixture calculation

The [FLINT reproduction](../examples/finite_mixture_flint.py) constructs
truncated generating series and their formal logarithms using exact FLINT
rationals. It does not import the package's cumulant implementation. Run it in
a separate environment supported by the hash-pinned wheel file:

```sh
python -m pip install --require-hashes --only-binary=:all: --no-deps -r examples/requirements-flint.txt
python examples/finite_mixture_flint.py
```

Its finite fixtures check moments, the mean and second-cumulant identities,
the rate-range variance bound, endpoint equality and the two-statistic ambiguity
example. It also checks total-variance identities and bounded-rate variance
ceilings for the first two factorial statistics. Controls reject using the
fixed-rate ceilings for mixtures and check the arithmetic of the documented
shared-rate dependence counterexample. Deliberately incorrect formulas must fail the checks. The output records
versions, source hash and execution counts; CI preserves it as `flint-ci-receipt`.
This adds arithmetic and implementation diversity within the same research
campaign. It neither verifies the executable generally nor supplies independent
human review, physical calibration or an originality result. These formulas
are rational, so exact arithmetic suffices without approximate ball enclosures.

## Formal proof

Follow [lean/README.md](../lean/README.md) to build all six modules with pinned
dependencies. Its verifier recompiles into fresh output, checks source hashes,
and runs a generated import-only axiom query in a separate Lean process against
an exact theorem-root registry. Compilation messages are not accepted as axiom
audit evidence. Each run has a unique name. Upstream compiled
mathlib caches are used; this is not a source rebuild of every trusted component.

The [D=1 stability extension](../lean/extensions/d1/README.md) uses the same pinned
dependencies but a separate source manifest and verifier. From the repository
root after the Lean build, run:

```sh
python lean/extensions/d1/verify_stability.py --run external-check
```

This compiles the extension freshly with `--trust=0`, separately audits all five
requested theorem roots and saves a receipt under `build/stability/external-check/`.
Use a new run name each time. `python tools/tasks.py formal` checks both the core
and the extension; the extension does not become part of the frozen core receipt.

The [finite-law connection](../lean/extensions/d1-law/README.md) adds a separate
check from the repository root:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --run external-check
```

It freshly compiles the six core modules, the unchanged stability source and
the Bernoulli connection in dependency order. It validates the core receipt
and imported artifact hashes and separately audits all six new theorem roots.
`python tools/tasks.py formal` includes this check as well. See its extension
guide for output locations and the offline existing-cache mode.

The [probability, sampling and uncertainty suite](probability-extensions.md)
uses the same verifier with `--suite research`:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-research
```

It freshly checks the six core modules and all nineteen extensions. Their source
manifests and theorem-root lists are checked separately. A valid axiom list may
use any subset of `propext`, `Classical.choice` and `Quot.sound`, including no
axioms; additional axioms, missing roots and duplicate roots are rejected.
The dependency cache
is reused, and the offline mode requires those compiled library modules.

After that research run succeeds, replay its stored project proof declarations:

```sh
python lean/replay.py --proof-run external-research --run external-research
```

The [exact rational query guide](../lean/extensions/confidence-executable/README.md)
adds kernel-checked point, pair and global-emptiness certificates:

```sh
python lean/check_certificates.py --proof-run external-research --run external-research
```

This checks the stated rational queries against the source-bound compiled
research objects, with separate axiom audits and deliberately incorrect-answer
controls. It does not verify the entire Sage or Python runtime.

The [count-to-box guide](../lean/extensions/counts-confidence/README.md) adds
explicit-record aggregation, outward radii and endpoint certificates:

```sh
python lean/check_certificates.py --suite counts --proof-run external-research --run external-research
```

This suite checks six valid synthetic records and five isolated incorrect
calculations. Its universal coverage theorem retains the original observation
laws and independence assumptions; a record certificate cannot test those
assumptions. The proposer is limited to 64 explicit counts per certificate.

The replay reuses the project artifacts recorded by the named research run and
the pinned Lean kernel. Imported upstream dependency artifacts remain trusted;
this is neither an independent implementation nor a from-source rebuild of
every dependency. It complements the axiom audit and does not replace it.
Hosted CI uses the corresponding `ci-check` run. A failed or missing receipt is
not a successful replay. The [shared audit policy](../lean/proof_audit.py) pins
the requested root registry and the defensive source-admission checks.

The committed local receipt used existing dependency artifacts and says so.
The separate initial hosted run also passed after fresh dependency retrieval;
its Linux receipt is preserved in the verification record.
Git attributes preserve its referenced proof bytes. See
[the verification record](../evidence/README.md) for extra development checker
runs and their reproducibility limits.

Earlier committed receipts used the former output-based audit. The
[red-team follow-up](red-team-followup.md) explains its confirmed defect and why
those records cannot establish that the repaired gate passed.

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

The hosted `sage` job runs the projection checks in the official SageMath 10.8
Linux image pinned by digest, with a read-only repository mount and networking
disabled during execution. Its `sage-ci-receipt` artifact records the output,
source hash and image metadata. Check the job for the exact commit rather than
inferring success from the workflow file. Local Sage evidence is retained
separately in the [verification record](../evidence/README.md).

The separate standard-library scale example uses exact rational outward bounds:

```sh
python examples/d1_confidence_scale.py
```

It is a diagnostic centered at population moments, not a simulated or measured
experiment. See the [parameter-specific interpretation](claims.md#population-centered-scale-diagnostic).

## Synthetic sampling experiment

The standard-library [count experiment](stress-test.md) samples three specified
laws, retains all 1.2 million generated counts and compares their empirical
factorial moments with exact targets:

```sh
python -I -B examples/count_model_stress.py --output build/count-stress-local
```

Use a new output directory for each run. The seed and design are fixed before
sampling. The script rejects implementation-control or data-integrity failures;
coverage and separation outcomes are reported without gating success. Its
prescribed-law Chebyshev intervals are ideal-IID benchmarks, not inference for
an unknown measured law or proof of pseudorandom independence.

The hosted `stress` job is part of the required aggregate CI check. Its
`count-stress-ci-receipt` artifact retains source, protocol, raw data, controls
and summaries for 14 days. Check the exact commit and download that artifact
within the retention period; raw binary counts are not committed to Git.
