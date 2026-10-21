# Product of normalized derivative jets

[CountTaylorJetProduct.lean](CountTaylorJetProduct.lean) proves `jet0_mul`: the
normalized derivative jet of a product equals the product of the two formal
jets, under separate `ContDiffAt ℝ ⊤` assumptions at zero for both factors.

In the pinned mathlib version, this bare `⊤` belongs to `WithTop ℕ∞` and means
analytic order `ω`. It is stronger than the embedded smooth order `∞`.
The theorem therefore does not claim that bare differentiability, or merely
an unstated smoothness assumption, suffices. Its coefficient proof uses the
finite-order Leibniz rule and the binomial/factorial identity.

The conclusion is a formal power-series identity. No theorem summing that
series to the original function is asserted here. The
[foundation](../taylor-jet/README.md) defines the normalization, and the
[analytic cumulant extension](../analytic-cumulant/README.md) establishes the
required regularity for its polynomial and local-log functions.

The source manifest lists the single checked root. Reproduce it as part of the
research suite in the [formal verification guide](../../README.md). Existing
pinned dependency caches are reused. The root uses only `propext`,
`Classical.choice`, and `Quot.sound`; no outside human review or originality
claim is made.
