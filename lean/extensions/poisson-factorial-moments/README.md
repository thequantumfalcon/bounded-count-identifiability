# Actual Poisson and Bernoulli–Poisson moments

[PoissonFactorialMomentsV1.lean](PoissonFactorialMomentsV1.lean) proves
integrability and the exact descending-factorial moment identity
`E[(N)_k] = r^k` for an actual Poisson measure of nonnegative rate `r`, for
every natural `k`. It also proves membership in every finite `Lp` space.

For a bounded source plus an independent Poisson count with the stated
marginal laws, all natural powers of the observed count are integrable, the
count belongs to every finite `Lp`, and its quadratic factorial statistic
`Y(Y-1)` belongs to `L2`. The exponent is a finite nonnegative real; no
essential boundedness or `L-infinity` claim is made.

For a source taking values in `{0,1}`, the actual positive-order factorial
moment is

```text
E[(X+N)_(k+1)] = r^(k+1) + (k+1) * p * r^k.
```

Here `p` is the mass at one, `k` is natural, and the theorem includes
integrability. A separate root specializes to the existing Bernoulli mass
definition with `0<=p<=1`. The formula covers both source endpoints and zero
rate without division by the rate. Independence is between the source and
background within each observation; these roots do not assert independence
between sampling windows.

The source manifest lists eight checked roots. Reproduce them with the full
research suite in the [formal verification guide](../../README.md). Pinned
dependencies are reused; all roots use only `propext`, `Classical.choice`, and
`Quot.sound`. These are standard distributional identities. They do not
establish physical model validity, software correctness, originality, or
outside human review.
