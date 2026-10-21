# Formal verification

This Lean project contains six proof modules for identification of a count law supported on `{0, ..., D}` from factorial cumulants of orders `2, ..., D+1`. It also proves the algebraic cancellation of an unknown fixed Poisson factor and the necessity, in general, of reaching order `D+1`.

## Reproduce from a fresh checkout

Install Lean's Elan toolchain manager, Git, and Python 3.10 or later. From this directory, run:

```text
lake exe cache get
lake build
python verify.py --run external-check
```

The checked-in `lean-toolchain` selects Lean 4.35.0. `lakefile.toml` pins mathlib to commit `56a005855ea17e0b0958f73ec801ae140b0a1679`; `lake-manifest.json` records the eight transitive dependency revisions as well. Preserve the lock file to reproduce these versions. The first command fetches the pinned dependencies and the upstream mathlib compilation cache. This recipe requires network access and therefore is **not** a build of every dependency from source.

The `BoundedCount` Lake library explicitly includes all six modules and passes `--trust=0` to their Lean invocations. The Python command independently recompiles those six project modules into a new local output directory, verifies their source hashes, checks the printed axiom lists, and writes `verification/external-check/result.json`. It resolves Lean through `lake env`; a separate bare `lean` command on the caller's path is unnecessary. Use a new `--run` name for each run, because existing evidence is never overwritten.

## What has been checked here

The committed receipt at `verification/local-existing-cache-formatted/result.json` records a fresh compilation of the staged project sources against previously installed Lean/mathlib dependency artifacts. No compiled artifact from the original project was supplied as an input. The receipt records source hashes, compiler identity, successful exits, output hashes, and printed axiom lists. The only axioms in those lists are Lean's standard `propext`, `Classical.choice`, and `Quot.sound`.

This local run used existing dependency libraries. It does **not** establish that a fresh network checkout, dependency retrieval, or every upstream dependency's source build has succeeded. It is also not an additional independent proof-kernel check. A future fresh-checkout run must be reported separately, with its actual environment and outcome.

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

The source law assumes nonnegative masses, total mass one, and a known finite support bound `D`. Cumulants are defined algebraically as `r!` times the coefficient of a formal logarithmic series. The formal Poisson channel is multiplication by `exp(b*t)`. Its interpretation as addition of an independent Poisson random variable with a fixed nonnegative rate requires the usual probabilistic generating-function argument; no measure-theoretic construction of independent random variables or analytic `Real.log` bridge is included here.

The results concern exact cumulants. They do not prove robustness to estimated cumulants, finite-sample performance, a physical model's validity, or uniqueness of a source before unknown thinning. Additional independent proof checks and scientific or statistical analyses belong in separate evidence records.

The sharpness family is established prior work: see [Afendras and Papadatos, Eq. (3.1) and Lemma 3.1](https://arxiv.org/pdf/1411.1165), PDF page 7, for the generalized matching / quasi-Poisson family and its matched factorial moments. No originality claim is made for that family or the lower-bound implication. Priority of any broader theorem must be assessed separately from successful formal verification.

## Dependencies and licenses

`third_party/provenance.json` records every pinned dependency and the hashes of its copied license text. The upstream dependency code and compiler binaries are not vendored. Mathlib and seven of its eight transitive packages use Apache-2.0; `Cli` uses MIT. Lean uses Apache-2.0, with additional bundled-component notices preserved in `third_party/licenses/Lean-bundled-LICENSES.txt`. These upstream licenses do not replace the license chosen for this project's own work.
