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
| Algebraic cancellation of fixed Poisson background | Lean formal generating series | Probability-space interpretation is not separately formalized |
| Order `D+1` is necessary in general | Valid probability-law construction in Lean | Known family; no construction-originality claim |
| Deterministic `D=1` inverse-error bounds | Separate Lean stability extension | Algebraic model; observation-error bounds must be justified separately |
| Exact rational reproductions | Python examples and tests | Finite calculations are not universal proofs |
| A `D=1` confidence-set projection | Written elimination proof and optional Sage calculation | Conditional IID model; no general-dimensional solver |

The [claim-to-evidence map](docs/claims.md) separates formal proofs, written
arguments, software checks and unresolved questions. Formal kernel checking
concerns the encoded propositions. It does not establish novelty, physical
assumptions or experimental usefulness.

## Inspect and reproduce

- Read the [theorem and proof](docs/theorem.md).
- Follow the [reproduction instructions](docs/reproduction.md) for Python,
  the pinned Lean/mathlib project and the optional Sage calculation.
- Inspect the six core source modules in [lean/](lean/) and the separate
  [D=1 stability extension](lean/extensions/d1/README.md).
- Review the [verification record](evidence/README.md) and its stated trust limits.

The emitted source count and unknown detection efficiency are not separately
identified. Random-rate background, source/background dependence, detector
saturation, support leakage and dependent windows require different analysis.
No detector or laboratory experiment has been validated by this repository.

## What comes next

The immediate proof targets are the probability-space Poisson bridge, general
stability bounds and the finite-sample coverage argument. The `D=1` algebraic
stability bound is now formalized. Broader exact solvers,
better statistical bounds, literature-priority checks and physical calibration
are separate tasks. See the [proof roadmap](docs/roadmap.md).

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
Original code and documentation are provided under the [MIT license](LICENSE.txt).
Third-party material retains its stated license; see [notices](NOTICE.md).
