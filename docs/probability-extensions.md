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
core identification theorem then identifies these actual measures. Its
cumulants still use the core formal-log definition. The equivalence with
analytic logarithm derivatives and the independent Poisson observation channel
are separate formalization obligations.

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

These results do not yet derive the actual Bernoulli-plus-Poisson factorial
moments from a probability construction. The variance identities alone are
polynomial equalities. A complete confidence procedure must still connect
those distributional moments, handle zero and positive ceilings together, and
verify the projection formula and implementation. The written IID model is a
sufficient sampling assumption; small empirical correlations do not establish
the required independence.

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
\operatorname{Var}(X+Z)-\mathbb E[X+Z]=-p^2+\operatorname{Var}\Lambda.
$$

Thus a justified bound `Var(Λ) ≤ η` supplies the perturbation allowance. This
probability-mixture calculation is not formalized by the algebraic module.
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

## Reproduction and trust

After fetching the pinned dependencies as described in the
[formal guide](../lean/README.md), run from the repository root:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-research
```

This suite recompiles all six core modules and the six extensions in dependency
order with `--trust=0`, checks source manifests, exact printed theorem lists,
standard axioms, diagnostics and output bindings. Use a new run name each time.
It reuses upstream compiled dependencies; it does not rebuild every trusted
component from source. Configuration is not evidence of a successful hosted
run: inspect the Actions results for the exact commit being reviewed.

Formal checks concern the encoded propositions. Separate semantic review in
the same research campaign is additional scrutiny, not external human review.
The extensions do not establish physical calibration, historical priority,
optimal estimators or practical performance.
