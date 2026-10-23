# Bounded source with independent Poisson background

[CountPoissonObservation.lean](CountPoissonObservation.lean) proves integrability
and generating-function identities for an actual bounded-law random variable
`X`, an actual Poisson random variable `Y` of nonnegative rate `r`, and their
independence. The [source manifest](source_manifest.json) lists nine roots.

For every real `s`, the observed exponential moment is

`E[exp(s*(X+Y))] = P(exp(s)-1) * exp(r*(exp(s)-1))`,

where `P` is the bounded source's factorial generating polynomial. Substitution
`s = log(1+t)` proves, for `t > -1`,

`E[(1+t)^(X+Y)] = P(t) * exp(r*t)`.

The conditional theorems use stated marginal laws and genuine independence.
The module also constructs the canonical product measure, proves that it is a
probability measure, establishes both projection laws and their independence,
and specializes the generating identity to that concrete space. Degree zero
and rate zero are included. It uses the [Poisson exponential-moment proof](../poisson-mgf/README.md).

These results establish the probability-level generating identity. They do not
identify analytic logarithm derivatives with the existing formal cumulants,
derive the single-window factorial-moment formulas or transformed square
integrability, construct a finite IID sample, or prove confidence projection
correctness. They do not validate a physical observation model or establish
independence from empirical correlations. No novelty claim is made for these
standard probability constructions.

From the repository root, use an unused run name:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-observation
```

The pinned verifier checks explicit roots, standard axioms and exact source
bindings with `--trust=0`, reusing compiled dependencies. See the
[extension guide](../../../docs/probability-extensions.md) for reproduction
limits. Earlier hosted verification records do not verify these new bytes.
