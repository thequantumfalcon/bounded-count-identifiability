# Finite sample means

[CountFiniteSampleMean.lean](CountFiniteSampleMean.lean) derives expectation
and variance bounds for actual finite sample means, then applies the
[conditional coverage theorem](../finite-sample/README.md).
The [source manifest](source_manifest.json) lists five checked roots.

Assumptions include a positive natural sample size, square integrability,
pairwise independence within each family, common per-observation means, and
per-observation variance bounds. No independence between the two estimator
families is required. This module uses positive ceilings. The subsequent
[confidence extension](../confidence-zero/README.md) handles zero ceilings
and proves independence within a measurably transformed family. Distribution-specific
moments and square integrability of the quadratic transform remain separate.
See the [extension guide](../../../docs/probability-extensions.md) for reproduction.
