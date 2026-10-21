# Finite sample means

[CountFiniteSampleMean.lean](CountFiniteSampleMean.lean) derives expectation
and variance bounds for actual finite sample means, then applies the
[conditional coverage theorem](../finite-sample/README.md).
The [source manifest](source_manifest.json) lists five checked roots.

Assumptions include a positive natural sample size, square integrability,
pairwise independence within each family, common per-observation means, and
per-observation variance bounds. No independence between the two estimator
families is required. The combined coverage theorem uses positive ceilings;
the zero-ceiling case remains separate. The distribution-specific moment
derivation and independence of transformed observations remain open.
See the [extension guide](../../../docs/probability-extensions.md) for reproduction.
