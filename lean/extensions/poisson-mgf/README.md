# Poisson exponential moments

[PoissonMGFV1.lean](PoissonMGFV1.lean) proves integrability and the exponential
moment identity for mathlib's actual Poisson measure:

`E[exp(sY)] = exp(r*(exp(s)-1))`.

The nonnegative rate `r` includes zero, and `s` ranges over all real numbers.
The proof establishes convergence of the weighted exponential series before
identifying the Bochner integral. The [source manifest](source_manifest.json)
lists two theorem roots. This standard formula carries no novelty claim.

The [observation extension](../poisson-observation/README.md) combines this
result with a bounded source and independent Poisson count. The correspondence
between analytic logarithm derivatives and the project's formal cumulants,
explicit factorial-moment formulas, and finite-sample projection correctness
remain separate obligations.

From the repository root, run the pinned research verifier with an unused name:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-poisson
```

The verifier recompiles project modules with `--trust=0` and checks explicit
roots, standard axioms and source bindings while reusing pinned dependencies.
See the [extension guide](../../../docs/probability-extensions.md) for the scope
and reproduction limits. Earlier hosted verification records do not verify these new bytes.
