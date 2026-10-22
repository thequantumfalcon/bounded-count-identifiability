# Bounded count identifiability

For a probability law supported on the integers `0, ..., D`, factorial cumulants
of orders `2, ..., D+1` determine the law, even when its mean is not supplied.
Independent Poisson background with an unknown **fixed** rate leaves these
higher cumulants unchanged. The observed mean then identifies the background.

This research artifact contains a written proof, Lean formalizations, exact
rational examples and a prototype `D=1` moment-box calculation. The general
order bound is sharp. The example establishing sharpness is an **existing
generalized matching distribution**, credited in the [references](docs/references.md).
Priority of the general sufficient-order theorem remains unresolved.

**Research provenance:** substantial AI assistance was used under human direction.
The maintainer did not independently derive or manually verify every step.
See the [full process disclosure and limitations](PROVENANCE.md).

## Start with an exact example

With Python 3.11 or newer, from this repository's root:

```sh
python -m pip install .
python -m bounded_counts --degree 3 --strength 1/2
```

The example compares different bounded source laws with different Poisson
backgrounds. Their observed factorial cumulants agree through order `D` and
separate at order `D+1`. The Python library uses exact rational arithmetic and
has no runtime dependencies. These computations illustrate the universal proof;
they do not replace it.

## What is established

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Bounded-law identification from orders `2, ..., D+1` | Written argument and Lean | Known exact support; population cumulants |
| Cancellation of fixed Poisson background and its probability generating identity | Lean formal series, actual probability construction and analytic derivative connection | Fixed nonnegative rate and source–background independence |
| Order `D+1` is necessary in general | Valid probability-law construction in Lean | Known family; no construction-originality claim |
| Deterministic `D=1` inverse-error bounds | Separate Lean stability extension | Algebraic model; observation-error bounds must be justified separately |
| Connection of those bounds to Bernoulli laws, including `p=0` and `p=1` | Lean finite-law and analytic extensions | Population cumulants; errors still need justification from data |
| Finite masses define actual probability measures and generating-function expectations | Lean probability and analytic extensions | Known finite support; all-order logarithm derivatives agree with formal cumulants |
| Conditional two-moment confidence bounds | Lean derives actual moments, integrability, variances and sample coverage | Bernoulli source, fixed independent Poisson background, known ceiling and pairwise-independent observed windows |
| `D=1` stability under bounded second-cumulant perturbations | Lean algebraic bound and actual finite-mixture probability construction | Finite mixtures of fixed-rate components; a supplied rate range bounds rate variance. Calibration and general mixing laws remain open |
| Moment error bounds for finite random-rate mixtures | Actual variance ceilings and simultaneous sampling bound in Lean | Common finite-mixture laws, supplied rate ceiling and unconditional pairwise independence across observed windows; no mixed-rate parameter projection or physical validation |
| Exact rational reproductions | Python examples and tests | Finite calculations are not universal proofs |
| A `D=1` confidence-set projection | Lean interval elimination, clipping and empty-set proofs; optional Sage calculation | The executable Sage program is not formally verified; no general-dimensional solver |
| Exact rational confidence decisions | Computable Lean tests proved equivalent to real point/pair feasibility and global nonemptiness; kernel-checked query certificates | Rational inputs; frontend and full Sage program remain outside formal verification |
| Encoded counts to rational confidence boxes | Lean aggregation identities, outward-radius checks and conditional pair/projected/empty-decision coverage; concrete record certificates | Sampling assumptions remain explicit; acquisition, parsing and full Sage execution are not verified |
| A second-system endpoint reconstruction | Isabelle/HOL proves the mean-one, ceiling-one family and exact root-isolation descriptors | A selected algebraic family; not the full Sage program or outside human review |

The [claim-to-evidence map](docs/claims.md) separates formal proofs, written
arguments, software checks and unresolved questions. Formal kernel checking
concerns the encoded propositions. It does not establish novelty, physical
assumptions or experimental usefulness.

## Inspect and reproduce

- Read the [theorem and proof](docs/theorem.md).
- Follow the [reproduction instructions](docs/reproduction.md) for Python,
  the pinned Lean/mathlib project and the optional Sage calculation.
- Inspect the six core source modules in [lean/](lean/) and the separate
  [D=1 stability](lean/extensions/d1/README.md) and
  [finite-law connection](lean/extensions/d1-law/README.md) extensions.
- Inspect the [probability, sampling and uncertainty extensions](docs/probability-extensions.md)
  and their explicit remaining assumptions.
- Review the [verification record](evidence/README.md) and its stated trust limits.
- Run the [synthetic count experiment](docs/stress-test.md), including its
  frozen design, saved-data checks and explicit ideal-model limitations.
- Check a rational box with the [verified decision functions and query certificates](lean/extensions/confidence-executable/README.md).
- Check a small count record with the [count-to-box certificates and coverage connection](lean/extensions/counts-confidence/README.md).
- Reproduce the [Isabelle endpoint reconstruction](isabelle/README.md), including
  its definition/oracle audit and deliberately invalid controls.
- Read the [red-team follow-up](docs/red-team-followup.md) for the verifier defects,
  their repairs and the limits of the numerical confidence prototype.
- Read the [originality review](docs/originality-review.md) and
  [focused reviewer request](docs/reviewer-request.md).

The emitted source count and unknown detection efficiency are not separately
identified. Random-rate background, source/background dependence, detector
saturation, support leakage and dependent windows require different analysis.
No detector or laboratory experiment has been validated by this repository.

The supplied red-team review exposed a real weakness in the earlier axiom-audit
tooling. The [follow-up](docs/red-team-followup.md) distinguishes that defect
from the mathematical statements and explains the separate audit and proof
replay checks. Historical green runs remain historical; use the Actions results
and receipts for the exact commit you inspect.

## What comes next

The formal extensions now cover the analytic cumulant connection, actual
distributional factorial moments and exact confidence-set projection. Further
work includes verification of acquisition/parsing and algebraic endpoint output, extension
beyond finite background-rate mixtures, broader exact solvers and sharper
statistical bounds. Outside mathematical review, literature-priority checks
and physical calibration still require their own evidence. See the
[proof roadmap](docs/roadmap.md).

Corrections, counterexamples, reproducibility reports and independent
mathematical review are welcome. This project does not claim external human
review, peer review, practical optimality or complete verification of every claim.

## Maintenance and reuse

Maintained by [The Quantum Falcon](https://github.com/thequantumfalcon).
Use [Discussions](https://github.com/thequantumfalcon/bounded-count-identifiability/discussions)
for questions and the issue forms for mathematical or software defects.
See [contribution guidance](.github/CONTRIBUTING.md),
[security reporting](.github/SECURITY.md) and [CITATION.cff](CITATION.cff).

The Python API is experimental (`0.1.0.dev0`); compatibility is not yet promised.
The [maintenance policy](docs/decisions/0002-maintenance-controls.md) explains
required checks, dependency updates and unresolved Scorecard recommendations.
Green CI is not a perfect security score or evidence of independent review.
Original code and documentation are provided under the [MIT license](LICENSE.txt).
Third-party material retains its stated license; see [notices](NOTICE.md).
