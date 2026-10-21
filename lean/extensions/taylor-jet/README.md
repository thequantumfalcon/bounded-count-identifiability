# Normalized derivative jets

[CountTaylorJetFoundation.lean](CountTaylorJetFoundation.lean) defines a formal
real power series whose coefficient at order `n` is `iteratedDeriv n f 0 / n!`.
Its three checked roots give that coefficient, compatibility with formal
differentiation, and invariance under equality on a neighborhood of zero.

The definition uses mathlib's totalized derivatives for arbitrary real
functions. It does not assert differentiability, analyticity, convergence, or
that a function equals the sum of its formal jet. The derivative compatibility
identity uses the iterated-derivative convention and factorial normalization.

The [product extension](../taylor-product/README.md) supplies a multiplication
result under explicit regularity assumptions. The
[analytic cumulant extension](../analytic-cumulant/README.md) connects these
jets to the project's existing cumulant definitions.

The source manifest lists the exact three roots. Run the complete research
suite using the [formal verification guide](../../README.md). Pinned dependency
caches are reused; the checked project roots use only `propext`,
`Classical.choice`, and `Quot.sound`. This is not outside human review or a
claim of mathematical originality.
