# Probability, sampling and uncertainty extensions

These extensions connect more of the written argument to actual probability
objects. They share the pinned Lean/mathlib dependencies and preserve the eight
earlier proof sources. Each has a separate source manifest. No originality claim
is made for these standard encodings, variance arguments or elementary bounds.

## Finite laws and expectations

[CountProbabilityBridge.lean](../lean/extensions/probability/CountProbabilityBridge.lean)
constructs a mathlib probability mass function and probability measure on
`Fin(D+1)` from every mass vector satisfying the core bounded-law assumptions.
It includes `D=0`, zero masses and endpoint distributions. For every real-valued
function on the count values, it proves that the Bochner integral is the finite
weighted sum. Consequently,

$$
P(t)=\mathbb E[(1+t)^X],\qquad
[t^k]P(t)=\mathbb E\binom Xk.
$$

The first identity holds for every real `t` because the count is bounded. The
core identification theorem then identifies these actual measures. The
analytic extension below proves that the core formal cumulants agree with
logarithm derivatives of this expectation. The independent Poisson generating
identity is also formalized below.

## Independent Poisson observations

[PoissonMGFV1.lean](../lean/extensions/poisson-mgf/PoissonMGFV1.lean) proves that
the actual mathlib Poisson measure has every real exponential moment, including
rate zero, and derives its standard exponential-moment formula from the
convergent exponential series. Integrability is established explicitly before
identifying the Bochner integral.

[CountPoissonObservation.lean](../lean/extensions/poisson-observation/CountPoissonObservation.lean)
then takes a bounded source `X`, a Poisson count `Y` of fixed nonnegative rate
`r`, their marginal-law statements and genuine independence. For every real
`s`, it proves integrability and

$$
\mathbb E[e^{s(X+Y)}]=P(e^s-1)\exp(r(e^s-1)).
$$

For `t > -1`, substituting `s=log(1+t)` gives

$$
\mathbb E[(1+t)^{X+Y}]=P(t)\exp(rt).
$$

The module also constructs the product of the finite source measure and the
Poisson measure, proves its probability normalization, both projection laws
and independence, and specializes the integrable generating identity to that
space. Degree zero, zero masses and zero rate are included. These eleven roots
close the probability-level generating-function construction. The analytic
connection is supplied by the following extension. Neither result validates
a physical model.
The identities and product construction carry no novelty claim.
Independence here is between the source and background in one observation;
independence across repeated observation windows is a separate assumption.

## Analytic cumulants

[CountAnalyticCumulantBridge.lean](../lean/extensions/analytic-cumulant/CountAnalyticCumulantBridge.lean)
proves, for every normalized real polynomial `P` and every natural order `n`,

$$
n![t^n]\log P(t)=\left.\frac{d^n}{dt^n}\log(P(t))\right|_{t=0},
$$

where the left logarithm is the core formal power series and the right is the
real function. The supporting Taylor-jet modules define coefficients as
`iteratedDeriv n f 0 / n!`, prove locality and differentiation, and prove the
product identity under explicit analytic-order `ContDiffAt` assumptions. In
the pinned mathlib, its bare top order is stronger than the embedded smooth
order; this is not a product theorem stated for arbitrary smooth functions.
The polynomial and local logarithm satisfy the required premises. The polynomial-log
proof matches a local differential identity with the formal-log identity;
it does not assume that every smooth function equals its Taylor series.

The extension handles the exponential channel and connects the cumulants to
the actual bounded-law and bounded-source-plus-Poisson expectations. For the
observed model it uses equality of functions near zero, where `t > -1`, rather
than an unproved exchange of differentiation and integration. All orders,
including zero and one, are covered. Source identification and identification
of the source together with the background are then stated directly in terms
of these analytic expectation derivatives, on possibly different probability
spaces with the required marginal laws and independence.

## Distributional factorial moments

[PoissonFactorialMomentsV1.lean](../lean/extensions/poisson-factorial-moments/PoissonFactorialMomentsV1.lean)
proves integrability and the factorial moments of the actual Poisson measure
by summing its probability masses. For every natural order `k`,
`E[(Y)_k] = b^k`, where `(Y)_k` is the descending factorial. Rate zero is included.

For an independent Bernoulli source of parameter `p` and Poisson background
of rate `b`, it then proves, for every `k >= 1`,

$$
\mathbb E[(X+Y)_k]=b^k+kp\cdot b^{k-1}.
$$

Both endpoint Bernoulli laws are allowed. This identity is derived from the
marginal probability laws and independence, rather than assumed as a moment
premise. For every bounded source plus independent Poisson background, the
extension also establishes every natural-power moment's integrability, every
finite `Lp` membership of the count, and square integrability of its quadratic
factorial statistic. The last conclusion is stronger than square integrability
of the count alone and discharges that specific sampling prerequisite.

## Conditional confidence bounds

[CountD1VarianceCoverage.lean](../lean/extensions/finite-sample/CountD1VarianceCoverage.lean)
proves the polynomial variance identities and ceilings used in the
[written confidence argument](claims.md#d1-confidence-prototype). It also proves
a genuine measure-theoretic Chebyshev and union bound: given square-integrable
estimators with expectations `m₁,m₂`, variance bounds `W₁/N,W₂/N`, and positive
`W₁,W₂,N,α`, the probability that either deviation is at least its radius
`sqrt(2Wᵣ/(Nα))` is at most `α`. Independence between the two estimators is not
required. A separate theorem handles zero variance by almost-sure equality.

[CountFiniteSampleMean.lean](../lean/extensions/sample-mean/CountFiniteSampleMean.lean)
derives the sample-mean premises for a nonempty finite sample: square
integrability, expectation, variance equal to the sum of individual variances
divided by `N²`, and the bound `W/N`. It assumes pairwise independence within
each family of per-window statistics, common expectations and individual
variance bounds, then applies the two-estimator theorem. Joint independence
of the two different moment estimates is unnecessary.

[CountConfidenceZeroAndTransforms.lean](../lean/extensions/confidence-zero/CountConfidenceZeroAndTransforms.lean)
extends coverage to nonnegative variance ceilings, including either or both
ceilings equal to zero. Failure means a deviation strictly exceeds its radius;
the good intervals include their endpoints. It also derives pairwise
independence of the family `Yᵢ(Yᵢ-1)` from pairwise independence of `Yᵢ` by
measurability of the transform. This does not make a count independent of its
own transformed value. The factorial sample-mean theorem explicitly assumes
square integrability of both statistics; square integrability of `Yᵢ` alone
does not establish it for the quadratic transform.

[BernoulliPoissonStatisticsV1.lean](../lean/extensions/bernoulli-poisson-statistics/BernoulliPoissonStatisticsV1.lean)
now supplies those premises from the actual Bernoulli-plus-Poisson probability
model. It proves the first four factorial moments and both variances. Writing
`S=X+Y` for one observation,

$$
\mathrm{Var}(S)=b+p(1-p),\qquad
\mathrm{Var}(S(S-1))=4b^3+(12p+2-4p^2)b^2+4pb.
$$

With `0 <= b <= B`, the existing ceilings `B+1/4` and
`4B^3+10B^2+4B` give simultaneous sample-mean coverage. The specialized theorem
assumes actual marginal laws and within-window independence, then derives the
moments, square integrability and variance bounds. It does not assume those
conclusions. Across windows, pairwise independence of the observed-count
family suffices; joint IID sampling is a stronger sufficient condition. The
parameter endpoints and zero rate are included, with a nonempty finite sample
and positive error level. Small empirical correlations do not establish the
required independence. Executable confidence software remains outside these
formal proofs.

The same module's `projected_region_coverage` theorem bounds the probability
that the true `p` is absent from the exact feasible region by `α`. It uses the
true background rate as a witness whenever both moment intervals contain
their population values. Together with the projection and clipping equalities
below, this connects the actual sampling model to the stated confidence set.

## Exact confidence projection

[CountConfidenceProjection.lean](../lean/extensions/confidence-projection/CountConfidenceProjection.lean)
defines feasibility by the original constraints on `p`, background `b`, mean
`p+b`, and second factorial moment `(p+b)^2-p^2`. It proves the
[closed interval formula](claims.md#d1-confidence-prototype), including
zero background ceiling, reversed bounds, the square-root domain guard and
an empty final interval. Clipping to the model ranges preserves the feasible
set, including when the clipped box is empty. The proof explicitly constructs
the intermediate mean used to eliminate the background.

This is a theorem about real sets. The optional Sage program implements the
same formula using exact algebraic arithmetic, but its execution, input policy,
witness helper and arithmetic library have not been formally verified.
Negative ceilings and reversed raw intervals raise input errors in that program;
the mathematical feasible set is empty. A projection of a specified box only
becomes a confidence procedure when that box has a justified coverage bound.

## Background-rate uncertainty

[CountD1BackgroundUncertainty.lean](../lean/extensions/background-uncertainty/CountD1BackgroundUncertainty.lean)
uses the algebraic model `k(p,v) = -p²+v`. If `p,q ≥ 0`, both `v,w` lie in
`[0,η]`, and the differences in `k` and mean are at most `ε` and `δ`, it proves

$$
|p-q|\leq\sqrt{\varepsilon+\eta},\qquad
|(\mu-p)-(\nu-q)|\leq\delta+\sqrt{\varepsilon+\eta}.
$$

The interval implies `|v-w| ≤ η`. Both compared models must satisfy the bound;
the theorem does not certify an arbitrary noisy estimate or supply `η` from data.

A separate written interpretation takes a nonnegative random rate `Λ` with
finite second moment, a background `Z | Λ ~ Poisson(Λ)`, and a Bernoulli source
`X` independent of the pair `(Λ,Z)`. Conditioning and total variance give

$$
\mathbb E[X+Z]=p+\mathbb E\Lambda,\qquad
\mathrm{Var}(X+Z)-\mathbb E[X+Z]=-p^2+\mathrm{Var}(\Lambda).
$$

Thus a justified bound `Var(Λ) ≤ η` supplies the perturbation allowance. The
arbitrary-mixing interpretation remains a written argument. A separate
[finite-mixture extension](../lean/extensions/finite-mixture/README.md) now
constructs a normalized finite sum of actual Bernoulli–Poisson product measures
with one common source parameter. It derives integrability and every positive
factorial moment, then proves the mean and second-cumulant identities using
the centered weighted rate variance. Zero weights, zero or repeated rates and
both Bernoulli endpoints are allowed.

If every component rate lies in a supplied interval `[L,U]`, the extension also
proves `v ≤ (U-L)²/4`. This is the established bounded-range variance inequality,
not a new inequality or a calibration inferred from observations. Applying the
existing stability theorem to two such actual mixture laws gives the displayed
source and mean-background error bounds. Both models must satisfy their stated
variance allowance. The module defines the second factorial cumulant by
`E[S(S-1)] - E[S]²`; it does not formalize logarithm derivatives of a mixture
generating function or a separate latent-index random variable.

The fixed-rate confidence theorem above cannot automatically be used with
random-rate backgrounds: its variance ceilings and sampling assumptions need
fresh justification for that model.
The second factorial cumulant here means variance minus mean; a finite second
moment alone need not give an analytic moment generating function near zero.
The standard mixed-Poisson factorial-moment identity appears in
[Kuba and Panholzer, Proposition 1(a)](https://arxiv.org/pdf/1403.2712).

For `0 < h ≤ 1`, compare a Bernoulli(`h`) source with rate `Λ` equally likely
to be `0` or `2h`, against source zero with fixed Poisson rate `2h`. Both totals
have mean `2h` and second factorial cumulant zero. Their source gap is
`h = sqrt(η)` at `η=h²`. This attains the pairwise ambiguity bound. It is not a
full-law collision: their third factorial cumulants differ by `2h³`. Nor is it
a constant-one minimax estimator lower bound. For an estimator using only
these two exact population statistics, the two-model argument forces a
worst-case error of at least `h/2`. It does not give that lower bound for
estimators using the full data or additional population statistics.

### Sampling bounds for finite mixtures

The [finite-mixture sampling extension](../lean/extensions/finite-mixture-sampling/README.md)
derives square integrability and conservative single-window variance ceilings
for the actual count and its second factorial statistic. For component rates in
a supplied $[0,B]$, they are

$$
W_1=B+\tfrac14+\tfrac{B^2}{4},\qquad
W_2=4B^3+10B^2+4B+\tfrac{(B^2+2B)^2}{4}.
$$

Finite total variance separates the weighted component variances from the
variance of component means. The mean count ranges over an interval of length
$B$; the component mean of the second statistic lies in $[0,B^2+2B]$.
The bounded-range variance inequality supplies the additional terms above.
These bounds are conservative and are not claimed to be optimal.

For $N>0$ observed windows with this common mixture law and unconditional
pairwise independence of the observed counts, the formal theorem bounds

```math
\Pr\!\left\{
|\widehat m_1-m_1|>\sqrt{\frac{2W_1}{N\alpha}}
\quad\text{or}\quad
|\widehat m_2-m_2|>\sqrt{\frac{2W_2}{N\alpha}}
\right\}\leq\alpha,
```

where $m_1=p+\sum_i w_i r_i$ and $m_2=\sum_i w_i(r_i^2+2pr_i)$.
For a confidence interpretation take $0<\alpha<1$. The zero-background case is
included; no independence between the two estimators is required. This closes
the sampling-bound step for the specified finite mixtures. It does not justify
the fixed-rate parameter projection for this broader model: the two-moment
ambiguity above persists even with exactly known population moments. General
mixing laws, calibration of $B$ and dependent-window bounds remain open.

### A shared random rate can defeat averaging

Marginal mixture laws do not establish independence across windows. Take source
zero, draw one rate $\Lambda\in\lbrace0,1\rbrace$ with equal probabilities for the entire
record, and conditionally draw independent Poisson($\Lambda$) counts $Z_i$.
Each window has the same finite-mixture marginal, but distinct windows have
covariance $\mathrm{Var}(\Lambda)=1/4$. Consequently,

$$
\mathrm{Var}\left(\frac1N\sum_{i=1}^N Z_i\right)
=\frac{1}{2N}+\frac14.
$$

For $B=1$, the finite-mixture single-window ceiling
$W_1=B+1/4+B^2/4=3/2$ is valid. The formal sampling theorem obtains its $1/N$
variance reduction from unconditional pairwise independence. At $N=1000$ and $\alpha=0.05$, the
corresponding simultaneous-Chebyshev mean radius has square $3/50$. On the
event $\Lambda=0$, of probability $1/2$, every observation is zero and its
sample mean differs from the population mean $1/2$ by $1/2$; the squared error
$1/4$ exceeds $3/50$. The nominal 5% failure bound therefore fails in this
model, despite conditional independence given the shared rate.

This is a written probability counterexample with
[exact arithmetic checks](../examples/finite_mixture_flint.py), not a formalized
dependent-process theorem or a laboratory observation. Independently drawing
the rate and counts anew for each window is a different model. Pairwise
independence of the observed windows must be justified where a sampling theorem
requires it; it does not follow from a marginal law or conditional independence.

## Reproduction and trust

After fetching the pinned dependencies as described in the
[formal guide](../lean/README.md), run from the repository root:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-research
```

This suite recompiles all six core modules and twenty-two extensions in dependency
order with `--trust=0`, checks source manifests, exact printed theorem lists,
standard axioms, diagnostics and output bindings. The axiom lists come from a
generated import-only query in a separate Lean process, with exact unique root
coverage; messages from proof compilation cannot supply that audit. Use a new
run name each time. See the [red-team follow-up](red-team-followup.md) for the
older gate's output-forgery defect and the distinction between axiom auditing
and stored-proof replay.
It reuses upstream compiled dependencies; it does not rebuild every trusted
component from source. Configuration is not evidence of a successful hosted
run: inspect the Actions results for the exact commit being reviewed.

Formal checks concern the encoded propositions. Separate semantic review in
the same research campaign is additional scrutiny, not external human review.
The extensions do not establish physical calibration, historical priority,
optimal estimators or practical performance.
