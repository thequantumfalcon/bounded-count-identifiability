# Formal verification

This Lean project contains six proof modules for identification of a count law supported on `{0, ..., D}` from factorial cumulants of orders `2, ..., D+1`. It also proves the algebraic cancellation of an unknown fixed Poisson factor and the necessity, in general, of reaching order `D+1`.

The separate [D=1 extension](extensions/d1/README.md) proves deterministic
inverse-error bounds. It shares the pinned toolchain and dependencies, but has
its own manifest, verifier and receipts. The commands below reproduce the six
core modules; follow the extension guide for its additional check.

The [finite-law connection](extensions/d1-law/README.md) connects these bounds
to Bernoulli masses and the core formal cumulants. Its verifier freshly
recompiles the six core modules, the stability module and the new connection,
then checks the imported artifacts and the six new theorem roots. It has a
separate manifest and leaves historical core receipts unchanged.

The [research extensions](../docs/probability-extensions.md) add actual finite
probability measures, independent Poisson generating identities, conditional confidence bounds,
sample-mean variance formulas, transformed-observation independence, coverage
with zero ceilings and a bounded second-cumulant perturbation theorem. They
also prove the all-order analytic cumulant connection, actual distributional
moments and variances, and coverage of the exact D=1 projected region.
From the repository root, `python lean/extensions/d1-law/verify_law_bridge.py
--suite research --run external-research` checks all twenty-three project modules
freshly. Each new extension has its own manifest; the historical receipts still
refer only to their original sources and checks.

## Reproduce from a fresh checkout

Install Lean's Elan toolchain manager, Git, and Python 3.10 or later. From this directory, run:

```text
lake exe cache get
lake build
python verify.py --run external-check
```

The checked-in `lean-toolchain` selects Lean 4.35.0. `lakefile.toml` pins mathlib to commit `56a005855ea17e0b0958f73ec801ae140b0a1679`; `lake-manifest.json` records the eight transitive dependency revisions as well. Preserve the lock file to reproduce these versions. The first command fetches the pinned dependencies and the upstream mathlib compilation cache. This recipe requires network access and therefore is **not** a build of every dependency from source.

The `BoundedCount` Lake library explicitly includes all six modules and passes
`--trust=0` to their Lean invocations. The Python command recompiles those six
project modules into fresh output and verifies their source hashes. A generated
import-only query in a separate Lean process audits the pinned theorem roots;
messages emitted during proof compilation cannot supply that audit. Exact
unique root coverage and an allowed-axiom subset are required. The receipt is
`verification/external-check/result.json`. The verifier resolves Lean through
`lake env`; a separate bare `lean` command on the caller's path is unnecessary.
Use a new `--run` name for each run, because existing evidence is never overwritten.

The shared [audit policy](proof_audit.py) supplies the complete registry of 140
roots across the research suite, the allowed axioms and defensive source checks.
Valid roots need not use all three allowed axioms. The separate
[stored-proof replay](replay.py) consumes a completed research run; see
[the reproduction commands](../docs/reproduction.md#formal-proof). It uses the
pinned Lean kernel and trusts the imported upstream dependency artifacts.
This adds a check of saved proof terms, not an independent kernel or sandbox.

## What has been checked here

The [dated verification index](../evidence/verification-index-2026-10-21.json)
links a later completed hosted milestone with all 21 modules and 124 theorem
roots, plus a separate point-in-time settings readback. It does not substitute
for the Actions result and receipt of the exact commit under review.

The following two committed receipts describe the original six-module verifier.
The [red-team follow-up](../docs/red-team-followup.md) records its confirmed
output-forgery and root-coverage weaknesses. Its successful historical runs
are retained as records of those executions, not upgraded to evidence of the
repaired audit or later proof replay.

The committed receipt at `verification/local-existing-cache-formatted/result.json` records a fresh compilation of the staged project sources against previously installed Lean/mathlib dependency artifacts. No compiled artifact from the original project was supplied as an input. The receipt records source hashes, compiler identity, successful exits, output hashes, and printed axiom lists. The only axioms in those lists are Lean's standard `propext`, `Classical.choice`, and `Quot.sound`.

This local run used existing dependency libraries. By itself it does **not** establish a fresh network checkout or dependency retrieval, and it is not an additional independent proof-kernel check.

A separate [GitHub CI run](https://github.com/thequantumfalcon/bounded-count-identifiability/actions/runs/39552914288) passed on 21 October 2026 for commit `d72022752b4a7bf6349b5a14256cc6e06770e03e`, using a fresh Ubuntu 24.04 runner. It retrieved the pinned dependencies and upstream mathlib cache, built all six modules, and passed the portable verifier. Its [preserved Linux receipt](verification/github-initial-d720227/result.json) and adjacent logs bind the same proof sources, lock and verifier. This closes the fresh-checkout reproduction gap for that commit. It still does not rebuild every upstream dependency from source or provide external human review.

The TOML configuration was separately accepted by the installed Lake parser. Dependency pins and license files were checked against the local dependency source snapshots. `source_manifest.json` binds the six proof sources to their finalized bytes; `.gitattributes` preserves those bytes across platforms. Build products under `.verification/` and `.lake/` are intentionally excluded from publication.

## Statements and boundaries

| Module | Role |
| --- | --- |
| `CountSeriesCore` | Formal logarithmic series, exponential tilt, and identification of normalized nonnegative polynomials of degree at most `D`. |
| `CountLawEncoding` | Encodes a finite probability law as its factorial probability generating polynomial and proves injectivity. |
| `CountIdentification` | Equality of factorial cumulants `2, ..., D+1` identifies the complete bounded count law. |
| `CountPoissonChannel` | Multiplication by the formal series `exp(b*t)` leaves cumulants of orders at least two unchanged. |
| `CountObservedIdentification` | Identifies the bounded source through that factor; the first cumulant additionally identifies the background parameter. |
| `CountSharpness` | Constructs valid laws for every `D >= 1` and `0 < h < 1` with the same lower cumulants, proving the order cutoff is necessary. |

The main theorem roots are:

```text
BoundedCountLaw.higher_factorial_cumulants_identify
BoundedCountLaw.observed_higher_cumulants_identify_source
BoundedCountLaw.observed_cumulants_identify_source_and_background
CountSharpness.sharpLaw_isBoundedLaw
CountSharpness.cutoff_is_sharp
CountSharpness.lower_observed_cumulants_match
```

The source law assumes nonnegative masses, total mass one, and a known finite support bound `D`. Cumulants are defined algebraically as `r!` times the coefficient of a formal logarithmic series. The formal Poisson channel is multiplication by `exp(b*t)`. The separate [probability extensions](../docs/probability-extensions.md#independent-poisson-observations) construct the independent, fixed nonnegative-rate Poisson model and prove its generating-function identity. The [analytic extension](extensions/analytic-cumulant/README.md) proves equality with `Real.log` derivatives of the actual generating expectation at every order.

The core results concern exact cumulants. The separate D=1 extension bounds
parameter error given specified observation errors in an algebraic model.
The finite-law connection lifts that bound to the core Bernoulli cumulants,
including the endpoint laws, and to the formal observation channel.
The research extensions supply conditional sampling bounds, a canonical
finite probability-space encoding and independent Poisson generating identities.
The newer modules derive actual distributional moments and variances, prove
the confidence projection including empty cases, and connect the actual sample
model to projected-region coverage. Executable Python/Sage correctness remains
separate. No extension establishes a physical model's validity or uniqueness
of a source before unknown thinning.

The sharpness family is established prior work: see [Afendras and Papadatos, Eq. (3.1) and Lemma 3.1](https://arxiv.org/pdf/1411.1165), PDF page 7, for the generalized matching / quasi-Poisson family and its matched factorial moments. No originality claim is made for that family or the lower-bound implication. Priority of any broader theorem must be assessed separately from successful formal verification.

## Dependencies and licenses

`third_party/provenance.json` records every pinned dependency and the hashes of its copied license text. The upstream dependency code and compiler binaries are not vendored. Mathlib and seven of its eight transitive packages use Apache-2.0; `Cli` uses MIT. Lean uses Apache-2.0, with additional bundled-component notices preserved in `third_party/licenses/Lean-bundled-LICENSES.txt`. These upstream licenses do not replace the license chosen for this project's own work.
