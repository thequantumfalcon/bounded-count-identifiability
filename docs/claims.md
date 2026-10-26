# Claims and evidence

The central result is the [bounded-count identification theorem](theorem.md). This table separates its mathematical scope from numerical checks and possible applications.

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Orders $2,\ldots,D+1$ identify any law on a known $0,\ldots,D$. | Universal proof in [theorem.md](theorem.md); [CountIdentification.lean](../lean/CountIdentification.lean). | Exact population cumulants and the stated support bound. |
| Independent fixed Poisson background preserves the identifying orders; adding the mean identifies its rate. | Generating-function proof, core Lean modules and [analytic connection](probability-extensions.md#analytic-cumulants). | Actual marginal laws, source–background independence and fixed nonnegative rates are explicit. Analytic expectation derivatives agree with formal cumulants at every order. |
| The general maximum order $D+1$ cannot be lowered. | Valid-law construction and matching cumulants in [CountSharpness.lean](../lean/CountSharpness.lean). | Uses an established generalized matching distribution; the comparison law is a point mass. |
| The source mean is the largest real root of an explicit cumulant polynomial; coefficient inversion reconstructs its law and gives an exact admissibility criterion. | Written proof in [reconstruction.md](reconstruction.md); [largest-root](../lean/extensions/largest-root/README.md) and [conditional admissibility](../lean/extensions/admissibility/README.md) extensions; [finite exact identity controls](../examples/largest_root_identity.py). | Lean proves the location and largest-root properties relative to a supplied series and conditional mass reconstruction. The construction from arbitrary cumulant inputs and the complete stated admissibility equivalence remain written; see [formal coverage](reconstruction.md#formal-coverage). The example is not a general root-isolation solver. |
| At zero, derivatives through order $D+1$ of the normalized shifted location polynomial equal the corresponding binomial moments; its first derivative is the mass at the supplied support ceiling. | [Root-structure extension](../lean/extensions/root-structure/README.md), with the normalization explained in [reconstruction.md](reconstruction.md#formal-coverage). | The formal polynomial is normalized by $1/(D+1)!$. Exact support-dependent root multiplicity and implicit-function sensitivity remain written consequences. |
| The inverse on admissible bounded laws has sharp uniform Hölder exponent $1/(D+1)$ for mean and total variation. | Written majorant proof and attributed sharpness family in [reconstruction.md](reconstruction.md#the-exponent-is-sharp). | Two admissible laws with the same fixed bound $D$; conservative dimension-dependent constants. No sampling-error guarantee or formalization of this general-$D$ result. |
| Exact arithmetic reproduces population cumulants and the known-family collision. | [Population calculation code](../src/bounded_counts/) and [examples](../examples/). | Finite exact cases supplement the universal proof. The software is not formally verified. |
| For nonnegative parameters in the algebraic $D=1$ model, second-cumulant error at most $\varepsilon$ gives parameter error at most $\sqrt{\varepsilon}$; mean error at most $\delta$ additionally gives background error at most $\delta+\sqrt{\varepsilon}$. | [CountD1Stability.lean](../lean/extensions/d1/CountD1Stability.lean), separately compiled with explicit axiom checks. | Defines $\kappa_2(p)=-p^2$ and $b(\mu,p)=\mu-p$ algebraically. The probability bridge and data-error guarantees are separate. |
| The $D=1$ bounds apply to the cumulants of Bernoulli masses and their independent-Poisson observation channel. | [CountD1LawBridge.lean](../lean/extensions/d1-law/CountD1LawBridge.lean), including endpoint laws, and the probability/analytic extensions. | $p,q\in[0,1]$; actual background rates are nonnegative. Observation-error guarantees must be supplied separately. |
| A Bernoulli source admits an exact algebraic projection of a two-moment confidence region. | [CountConfidenceProjection.lean](../lean/extensions/confidence-projection/CountConfidenceProjection.lean), including clipping and empty cases. | Known background ceiling; deterministic projection of a specified box. The Sage implementation is not formally verified. No general-$D$ solver is claimed. |
| The mean-one, ceiling-one endpoint family and the retained illustrative algebraic descriptors admit an Isabelle/HOL reconstruction. | [Two proof theories and a 31-root audit](../isabelle/README.md); [local verification record with source hashes](../evidence/isabelle-endpoints-check.json). | Standard HOL and its toolchain remain trusted. The moment equations are assumptions; this does not verify arbitrary Sage output, probability laws or physical calibration. |
| Rational-input feasibility and global emptiness are decidable by the supplied exact programs. | [Executable decision extension](../lean/extensions/confidence-executable/README.md): Boolean-to-real equivalences, plus kernel-checked concrete query certificates. | Global existence quantifies over real parameters, including irrational witnesses. Python parsing and full Sage execution remain separate. |
| Encoded natural-count records produce rational confidence boxes with conditional pair and projected coverage. | [Count-to-box extension](../lean/extensions/counts-confidence/README.md): exact aggregation, real-cast identities, outward-radius checks, coverage and false-empty probability at most $\alpha$. | Fixed preselected design and the original Bernoulli–Poisson laws/independence/ceiling assumptions. The small-record proposer is checked per emitted certificate; acquisition, parsing, arbitrary algebraic endpoint output and the runtime are not formally verified. |
| Every encoded bounded mass vector defines an actual probability measure; its factorial generating polynomial equals the corresponding expectation. | [Probability extension](probability-extensions.md#finite-laws-and-expectations), seven Lean roots, with the subsequent analytic connection. | Canonical finite probability space; formal cumulants agree with logarithm derivatives of the expectation. |
| Two finite sample means have simultaneous Chebyshev coverage, including zero variance ceilings. | [Sampling extensions](probability-extensions.md#conditional-confidence-bounds), with actual moments, transform square integrability and variances derived in the Bernoulli-plus-Poisson model. | Common marginal laws, source–background independence within each window, a known background ceiling and pairwise independence across observed windows. These conditions are not inferred from data. |
| A bounded additive second-cumulant perturbation gives the $D=1$ allowance $\sqrt{\varepsilon+\eta}$. | [Uncertainty extension](probability-extensions.md#background-rate-uncertainty), plus an actual finite-mixture construction, moment identities and a conditional range-to-variance bound in Lean. | Both models satisfy the variance allowance. General mixing laws and empirical rate-range calibration remain outside the formalization. |
| Finite mixtures with bounded component rates admit simultaneous sample-moment error bounds. | [Finite-mixture sampling extension](../lean/extensions/finite-mixture-sampling/README.md): actual square integrability, total variance, conservative ceilings and Chebyshev coverage. | Common specified mixture law and unconditional pairwise independence of observed windows; the rate ceiling is supplied. No source identification or mixed-rate parameter projection follows from this moment coverage. |
| A frozen synthetic experiment records empirical factorial moments for three prescribed count models. | [Experiment and saved-data controls](stress-test.md), with a local execution record identifying the source hashes and a separate CI artifact. | Known-law uncertainty benchmarks; no empirical coverage-rate validation, optimality or physical measurement. Statistical outcomes do not gate CI success. |
| Finite-moment compatibility and zero covariance do not certify the observation model. | Explicit counterexamples below and the [calibration obligations](roadmap.md). | Constructed probability models are not measurements or an assessment of a particular instrument. |
| The sharpness family and Poisson-cancellation method are established. | [Primary references and access notes](references.md). | Priority of the general sufficient-order theorem remains unresolved. |

The [formal verification guide](../lean/README.md) documents the six core modules and twenty-two extension modules, pinned dependencies, compiler results and reproduction limits. Historical receipts cover their recorded source versions only. Additional development checks accepted selected dependency-closed exports using several checker binaries. The selected results use `propext`, `Classical.choice` and `Quot.sound`; no `sorryAx` was found in those exports. Several checkers share ancestry and dependencies. These checks help detect errors but do not amount to external human peer review. Implementations also share mathematical specifications and parts of their development process; see [research provenance](../PROVENANCE.md).

## D=1 deterministic stability

For any $p,q\geq0$,

$$
|p-q|^2\leq|p^2-q^2|,
\qquad |p-q|\leq\sqrt{|p^2-q^2|}.
$$

The first inequality follows from $|p-q|\leq p+q$ and
$|p^2-q^2|=|p-q|(p+q)$. Taking square roots and then applying the triangle
inequality proves the parameter and background bounds in the table. The
[separate extension guide](../lean/extensions/d1/README.md) specifies all five
checked theorem roots and reproduction commands. This elementary result carries
no originality claim. It does not establish confidence levels, admissibility of
an arbitrary estimate, or stability for general $D$.

The [finite-law extension](../lean/extensions/d1-law/README.md) now proves that
the mass vector $(1-p,p)$ is a bounded law for every $p\in[0,1]$, including both
endpoints. It connects the formula $-p^2$ to the core formal-log cumulant
definition. For the formal observed channel it proves
$\kappa_1=p+b$, $\kappa_2=-p^2$, and the joint inverse bound using those same
definitions. This closes the finite-mass-vector connection. It does not
construct independent random variables or turn estimated errors into
finite-sample confidence guarantees.

## D=1 confidence prototype

For $X\sim\mathrm{Bernoulli}(p)$ and independent $Z\sim\mathrm{Poisson}(b)$, set $Y=X+Z$. With $0\leq p\leq1$ and $0\leq b\leq B$,

$$
m_1=p+b,
\qquad m_2=\mathbb E[Y(Y-1)]=(p+b)^2-p^2.
$$

The two empirical factorial moments are unbiased. For a preselected $N\geq1$ IID windows, a valid fixed $B\geq0$, and preselected $0<\alpha<1$, use

$$
W_1=B+\tfrac14,\qquad W_2=4B^3+10B^2+4B,
\qquad \rho_r=\sqrt{\frac{2W_r}{N\alpha}}.
$$

Indeed,

$$
\mathrm{Var}(Y)=b+p(1-p)\leq W_1,
$$

$$
\mathrm{Var}(Y(Y-1))=4b^3+(12p+2-4p^2)b^2+4pb\leq W_2.
$$

The second variance identity follows from $m_r=b^r+rp b^{r-1}$ for $r\geq1$ and $\mathbb E[(Y(Y-1))^2]=m_4+4m_3+2m_2$. Its bound uses $12p+2-4p^2\leq10$ on $[0,1]$ and $b\leq B$. Chebyshev's inequality and a union bound give simultaneous coverage at least $1-\alpha$ for the moment intervals $[\widehat m_r-\rho_r,\widehat m_r+\rho_r]$. A zero variance ceiling makes that moment deterministic. The proof does not require the two estimators to be independent; it does require the window assumptions.

Clip these intervals to the model ranges, obtaining $[a,c]\subseteq[0,1+B]$ and $[d,e]\subseteq[0,B^2+2B]$. If either is empty, the feasible region is empty. For $B>0$, also reject $c^2<d$; otherwise the exact projection onto $p$ is $[L,U]$ when $L\leq U$, where

$$
L=\max\left(0,a-B,\sqrt{\max(0,a^2-e)},\frac{d-B^2}{2B}\right),
\qquad U=\min\left(1,c,\sqrt{c^2-d}\right).
$$

This follows by eliminating the mean $m=p+b$ from

$$
\max(a,p,\sqrt{d+p^2})\leq m\leq\min(c,p+B,\sqrt{e+p^2}).
$$

For $B=0$, the projection is $[a,c]$ if the clipped intervals are nonempty and $d=0$; otherwise it is empty. Empty results must not be silently replaced by a point estimate. Algebraic endpoint decisions require exact arithmetic; displayed decimals alone are not certificates. The [projection extension](../lean/extensions/confidence-projection/README.md) formalizes this set equality, the positive-ceiling formula, clipping and all rejection cases. The Sage program treats reversed raw bounds and negative ceilings as input errors; the corresponding mathematical constraints are infeasible. Formalizing the formula does not verify the program's parsing, execution or arithmetic library. Synthetic behavior does not prove coverage or practical superiority.

Unbiased factorial-cumulant estimators also have established literature; [Müller (2004), Appendix B, equations (37) and (39)](https://groups.spa.umn.edu/2-photon/publications/JM04BJ.pdf) gives the second-order estimator and its exact finite-sample variance. The prototype above fits factorial moments, rather than treating a plug-in cumulant estimate as unbiased.

### Population-centered scale diagnostic

The conservative confidence formula can produce wide intervals even at large
sample sizes. For the fixed illustrative parameters $p=0.3$, $b=0.5$, $B=1$ and
$\alpha=0.05$, center the moment box at the population values
$m_1=0.8$, $m_2=0.55$ and use the stated radii. This deterministic calculation
gives the following projected widths; decimals are rounded for display.

| Windows $N$ | Projected interval for $p$ | Width |
| --- | --- | --- |
| 10,000 | [0, 0.690265] | 0.690265 |
| 100,000 | [0, 0.459489] | 0.459489 |
| 1,000,000 | [0.227823, 0.358045] | 0.130222 |
| 10,000,000 | [0.279181, 0.319481] | 0.040300 |
| 100,000,000 | [0.293574, 0.306293] | 0.012718 |

[Reproduce the table](../examples/d1_confidence_scale.py) with
`python examples/d1_confidence_scale.py`. It uses standard-library rational
arithmetic and outward square-root enclosures, and emits exact rational bounds
alongside display decimals. For these nested population-centered boxes, width
first falls to at most $0.1$ at $N=1,662,466$; the script bounds widths at both
that integer and the preceding one.

These are not expected or best-case sample widths, a universal sample-size
minimum, or a lower bound for other procedures. Exactly population-centered
empirical moments need not be attainable at every integer $N$; actual sample
intervals vary with the observations. For example, with $p=0.3$, $b=B=0$ and
the same error level, the population-centered width is exactly $0.1$ at
$N=4,000$. The table motivates sharper statistical analysis without claiming
that this conservative method is practically efficient.

The separate [Sage projection example](../examples/d1_projection_sage.py) is
executed by the required `sage` CI job with a digest-pinned SageMath 10.8 image.
It checks seven boundary fixtures, 3,375 exact membership comparisons and
1,038 original-constraint witnesses, and uploads a `sage-ci-receipt` artifact.
Those finite execution controls supplement the projection theorem; they do
not formally verify Sage or the executable program.

## Two assumption controls

The [calibration note](calibration.md) gives a written union-bound argument for
combining uncertainty in a fixed-rate ceiling with sampling error. It also
shows why no rule finite on an all-zero record can uniformly bound the largest
rate in unrestricted finite mixtures. These are conditional written arguments,
not additional Lean theorems or measurements.

A count $Y$ equal to $0$ or $2$ with probability $1/2$ each has mean $1$ and factorial cumulants $(\kappa_2,\kappa_3)=(0,-1)$. A Poisson count of mean $1$ has $(0,0)$. Thus the mean and second factorial cumulant can fit the $D=1$ observation model even when the true distribution is outside it.

Even a Poisson background marginal and zero covariance are insufficient. Let $Z\sim\mathrm{Poisson}(1)$ and specify $\Pr(X=1\mid Z)$ as $5/8,1/4,3/4,1/2$ for $Z=0,1,2,\geq3$, respectively. Then $X\sim\mathrm{Bernoulli}(1/2)$ and $\mathrm{Cov}(X,Z)=0$, but the conditional probabilities show dependence. Direct summation gives

$$
\mathbb E[(1+t)^{X+Z}]=(1+t/2)e^t+\frac{t^3}{8e}.
$$

The extra term changes the third factorial cumulant by $3/(4e)$ while preserving the first two. The independent-addition formula therefore fails despite the correct marginals and zero covariance.

## Claims not made

The [counting-model comparison](counting-models.md) distinguishes this additive
bounded-source model from a Poisson mixture driven by a random intensity. Their
cumulant identities concern different latent quantities. Agreement of a few
moments is weaker than agreement of a full count law, and background-invariant
population quantities can still be difficult to estimate from noisy data.

The project establishes no laboratory validation, new particle interpretation, efficient acquisition protocol, optimal estimator or unconditional finite-data guarantee. It does not identify an emitted source separately from an unknown detection efficiency. A compatible finite list of moments cannot certify the entire noise model. Zero covariance cannot certify independence, and observing no source-support violation cannot prove its probability is exactly zero.

The known-family attribution corrects an earlier omission during development. The distribution was recognized as existing prior art before release. The literature search was targeted and incomplete; failure to locate an exact statement of the sufficient-order theorem is not evidence of originality.
