# Bernoulli–Poisson confidence regions

[BernoulliPoissonStatisticsV1.lean](BernoulliPoissonStatisticsV1.lean) connects
the actual independent Bernoulli-plus-Poisson model to finite-sample moment
bounds and coverage of the projected Bernoulli parameter region.

For `Z=X+Y`, where `X` has Bernoulli parameter `p` in `[0,1]` and `Y` has a
fixed nonnegative Poisson rate `r`, the checked results give square
integrability of `Z` and `Z(Z-1)`, the first four factorial moments, and

```text
E[Z] = p+r
E[Z(Z-1)] = r^2+2*p*r
Var(Z) = r+p*(1-p)
Var(Z(Z-1)) = 4*r^3+(12*p+2-4*p^2)*r^2+4*p*r.
```

The sampling theorems assume a probability space, a positive number `N` of
windows, the same `p` and `r` in every window, the stated marginal laws,
independence of source and background within each window, and pairwise
independence of observed counts across distinct windows. Independence of the
two sample estimators is not required. These are mathematical model
assumptions, not conclusions drawn from data.

Given a known ceiling `r<=B` and `alpha>0`, define

```text
W1 = B+1/4,  W2 = 4*B^3+10*B^2+4*B
R1 = sqrt(2*W1/(N*alpha)),  R2 = sqrt(2*W2/(N*alpha)).
```

The simultaneous moment failure event has measure at most `alpha`. More
directly, `projected_region_coverage` bounds by `alpha` the event that the true
parameter `p` is absent from the feasible region formed by the two sample
means and these radii. For the usual confidence interpretation take
`0<alpha<1`; the theorem itself only needs `alpha>0`.

The [projection extension](../confidence-projection/README.md) proves that
clipping these moment intervals preserves the region and supplies its exact
closed interval formula, including empty cases. The coverage root is stated
using that extension's `Feasible` predicate. Zero background ceiling, source
endpoints, and a zero second variance ceiling are included. No empty region
is replaced with a point estimate.

The source manifest lists six checked roots. Reproduce them with the research
suite in the [formal verification guide](../../README.md). The proof composes
the actual [factorial moments](../poisson-factorial-moments/README.md), the
existing sample-mean bounds, and deterministic projection. Pinned imports are
reused; checked roots use only `propext`, `Classical.choice`, and `Quot.sound`.
This proves a model-conditional mathematical coverage result. It does not
verify an executable confidence program, infer the observation model from
finite data, establish physical calibration, or imply originality or outside
human review.
