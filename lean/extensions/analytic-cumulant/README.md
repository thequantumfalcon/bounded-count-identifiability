# Analytic and formal factorial cumulants

[CountAnalyticCumulantBridge.lean](CountAnalyticCumulantBridge.lean) connects
the existing formal factorial cumulants to derivatives of the real logarithm
of the actual factorial generating expectation at zero. It also composes that
identity with the existing source and background identification theorems.

For a real polynomial `P` with constant coefficient one, the normalized jet of
`log(P(t))` equals the formal `PowerSeries.logOf P`. Multiplying coefficient
`n` by `n!` gives the actual `n`th logarithmic derivative. This holds at every
natural order, including order zero, whose value is zero. The corresponding
channel identity uses `P(t) * exp(b*t)` for any real formal parameter `b`.

The probability specializations require a valid bounded law on the known
support `0,...,D`, a nonnegative fixed Poisson rate, the stated marginal laws,
and independence between the bounded and Poisson variables. They cover both
an arbitrary probability space and the canonical independent product space.
For two such models, equality of log-expectation derivatives at orders
`2,...,D+1` identifies the bounded masses; including order one also identifies
the Poisson rate. The models may use different probability spaces and rates.
The boundaries `D=0` and rate zero are included.

The variable `t` is the factorial-PGF coordinate `(1+t)^count`, not the
ordinary exponential-moment parameter. Normalization gives a nonzero local
polynomial germ at zero. The observed expectation identity holds for `t>-1`,
so equality on a neighborhood transfers derivatives. The proof does not move
derivatives under an integral or assert convergence of an infinite Taylor
series. Its [product helper](../taylor-product/README.md) uses explicit
analytic-order regularity, which the polynomial and local logarithm satisfy.

The source manifest lists the 13 checked roots. Reproduce them with the full
research suite in the [formal verification guide](../../README.md). Pinned
imports are reused; the checked roots use only `propext`, `Classical.choice`,
and `Quot.sound`. This establishes population identities under the specified
model. It does not establish sampling independence, numerical estimation,
physical calibration, outside human review, or originality.
