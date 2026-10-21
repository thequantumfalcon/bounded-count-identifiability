# D=1 stability with a second-cumulant perturbation

[CountD1BackgroundUncertainty.lean](CountD1BackgroundUncertainty.lean) proves
the parameter bound `sqrt(ε+η)` when each additive perturbation lies in `[0,η]`
and the second-cumulant difference is at most `ε`. A mean difference at most
`δ` gives background-mean difference at most `δ+sqrt(ε+η)`.
The [source manifest](source_manifest.json) lists five checked roots.

The theorem is algebraic. Its mixed-Poisson interpretation and example are
explained separately in the [extension guide](../../../docs/probability-extensions.md),
alongside the reproduction command. Calibration, analytic cumulant derivatives,
and the probability-mixture construction are not proved by this module.
