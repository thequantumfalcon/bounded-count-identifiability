# Conditional moment coverage

[CountD1VarianceCoverage.lean](CountD1VarianceCoverage.lean) proves polynomial
variance identities and ceilings, followed by an actual measure-theoretic
Chebyshev and union bound for two estimators. Their expectations and variance
ceilings are explicit premises. Zero variance has a separate almost-sure
equality theorem. The [source manifest](source_manifest.json) lists nine roots.

The [sample-mean extension](../sample-mean/README.md) supplies the estimator
premises for a finite family with stated independence and moment assumptions.
Concrete Bernoulli-plus-Poisson moments and the full confidence projection
remain separate. See the [extension guide](../../../docs/probability-extensions.md)
for exact assumptions and reproduction.
