# Synthetic emitter-counting comparisons with Poisson background

This is a **synthetic calculation**, not a measurement, detector validation or
originality claim. It compares numerical two-point lower bounds and specified
estimators for identical emitters with an unknown fixed Poisson background.

## Model and question

In each window, $n$ identical emitters independently give at most one detected
photon each with probability $p$, and an independent Poisson background with
fixed mean $b$ adds counts:

$$
Y=\operatorname{Binomial}(n,p)+\operatorname{Poisson}(b).
$$

Here $n$ is a positive integer, $0<p\le1$ and $b\ge0$. The restriction $p>0$
matters for emitter counting: if $p=0$, every $n$ gives the same zero source law.

This is the identical-parameter case of the Poisson-binomial subclass discussed
in the [internal prior-art comparison](originality-review.md). For a known
common support bound $D$, the [theorem](theorem.md) identifies the source law
from exact population factorial cumulants $2,\ldots,D+1$. Applying that general
theorem to $n$ versus $n+1$ emitters requires a bound that includes both models.
Identification does not specify how many windows are needed to estimate those
cumulants.

For this binomial subclass, the generating function gives a simpler population
inverse directly:

$$
\kappa_2(Y)=-np^2,\qquad \kappa_3(Y)=2np^3,
$$

$$
p=-\frac{\kappa_3(Y)}{2\kappa_2(Y)},\qquad
n=-\frac{4\kappa_2(Y)^3}{\kappa_3(Y)^2},\qquad
b=\mathbb EY-np.
$$

Thus orders 2 and 3 identify $n,p$ under the stated binomial assumptions,
without a known bound on $n$; the mean additionally identifies $b$. This is
an algebraic consequence of the binomial model and Poisson cancellation, with
no originality claim. It does not demonstrate a need for order $D+1$ in this
subclass. The [short note](theorem.md#conditional-emitter-counting-application)
separates this specialization from the theorem for arbitrary bounded laws.

Fix a signal law $P=\operatorname{Binomial}(n,p)+\operatorname{Poisson}(b)$
and an alternative
$Q=\operatorname{Binomial}(n',p')+\operatorname{Poisson}(b')$, with valid
probabilities and nonnegative background means. Write
$A=\sum_{j\ge0}\sqrt{P(j)Q(j)}$ for their Bhattacharyya coefficient and
$\delta=-\log A$. For $N$ independent signal windows and $K$ independent
source-off windows, all mutually independent, the joint coefficient is
$A^N\exp[-K(\sqrt b-\sqrt{b'})^2/2]$. The total-variation bound implies
that any test whose two error probabilities sum to at most 10% must satisfy

$$
2N\delta+K(\sqrt b-\sqrt{b'})^2\ge\ln(1/0.19).
$$

Indeed, the error sum is at least $1-\mathrm{TV}$, and
$\mathrm{TV}\le\sqrt{1-A^{2N}\exp[-K(\sqrt b-\sqrt{b'})^2]}$.
For a design with $K=rN$ an integer, this gives the fixed-pair lower bound

$$
N\ge\frac{\ln(1/0.19)}{2\left[\delta+r\,\tfrac{(\sqrt b-\sqrt{b'})^2}{2}\right]}.
$$

The displayed quotient assumes a positive finite denominator, as in the
reported cells. It is a necessary condition, not a sufficient testing rule.

The case $r=0$ supplies no source-off observations. Known background restricts
alternatives to $b'=b$. The tables report signal-window lower bounds; the
source-off design uses $N+K$ windows in total. A rounded allocation should use
its actual integer $K$ in the preceding inequality.

Searching over $(p',b')$ can find a stronger fixed-pair obstruction, but does
not prove that the selected alternative is globally least favorable. Even a
globally optimized lower bound would not establish an achievable sample size.

## Numerical lower-bound comparisons

Run [emitter_background_cost.py](../examples/emitter_background_cost.py) with
`numpy` and `scipy` ([pins](../examples/requirements-emitters.txt)). Here
$n'=n+1$, for $n=2,\ldots,5$. Rounded ratios compare the computed lower bounds
with their known-background counterparts, not the actual data requirements of
any procedure:

| $p$ | $b$ | Known-$b$ lower bound | $r=0$ | $r=0.01$ | $r=0.03$ | $r=0.1$ |
| --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 0.1 | 1.65e5-3.2e5 | 149-296x | 1.33-1.65x | 1.11-1.21x | 1.03-1.06x |
| 0.1 | 0.1 | 2.01e4-5.16e4 | 42.4-104x | 1.48-2.21x | 1.16-1.41x | 1.05-1.12x |
| 0.3 | 0.1 | 811-2.7e3 | 3.86-7.64x | 1.75-2.35x | 1.3-1.68x | 1.1-1.25x |
| 0.05 | 1 | 4.65e6-5.7e6 | 1.07e3-1.34e3x | 1.19-1.23x | 1.06-1.08x | 1.02x |
| 0.1 | 1 | 3.75e5-4.09e5 | 282-382x | 1.68-1.74x | 1.22-1.24x | 1.06-1.07x |
| 0.3 | 1 | 7.19e3-9.94e3 | 34.6-55.9x | 3.76-4.74x | 1.94-2.3x | 1.28-1.38x |

The [full synthetic results](../evidence/emitter-study/background-cost.json)
retain the individual parameter cells, candidate alternatives and numerical
tail diagnostics.

In this grid the unknown-background lower bounds are much larger than the
known-background lower bounds. Adding source-off observations reduces the
displayed obstruction. A ratio close to one does not show that the corresponding
estimation problems have equal difficulty, or that this allocation is optimal.

The numerical search combines a grid with local refinement. For a probability
prefix $j<J$, write
$H_J=\tfrac12\sum_{j<J}(\sqrt{P(j)}-\sqrt{Q(j)})^2$. If the omitted tail
masses are bounded above by $\tau_P,\tau_Q$, then

$$
A\ge1-H_J-\frac{\tau_P+\tau_Q}{2}.
$$

When positive, this lower bound on $A$ gives an upper bound on $\delta$ and
hence a weaker necessary-count bound. The code includes Chernoff tail
allowances and compares candidate evaluations with higher-precision decimal
arithmetic. Floating-point and decimal calculations are not certified interval
arithmetic: the tables are numerical approximations to the fixed-pair bounds,
not machine-certified inequalities or proofs of global optimality.
In the recorded first-grid execution, 73 of 168 two-parameter local refinements
reached their iteration limit. This is a diagnostic of that execution, not a
reproduction target: termination statuses, iteration counts and evaluation
counts can vary across platforms even with pinned library versions. The
retained candidates still have valid model parameters and finite evaluations;
their termination statuses are included in the result file.

## Applied to published emitter-counting parameters

[Li et al. (2022), *Optics Express* 30, 12495–12509](https://doi.org/10.1364/OE.454412)
estimate $M,p$ using photon-number-resolving detection and a binomial likelihood.
Their published Section 6 also studies independent additive Poisson noise,
$Y\sim\operatorname{Binomial}(M,p)+\operatorname{Poisson}(rMp)$, comparing a
likelihood analysis with known relative background $r$ against one that ignores
the noise. Thus Poisson-contaminated emitter counting is already part of that
paper; knowing $r$ is a different design from our source-off calibration.

A follow-up,
published as [Li et al. (2023), *AVS Quantum Science* 5, 041401](https://doi.org/10.1116/5.0162501)
([preprint](https://arxiv.org/abs/2306.05614v2)), uses a convolution of binomial
laws for several species. Its Section II omits background from model (2) and
leaves a Poisson or mixed Poisson–Gaussian extension for future work. That
statement concerns the multi-species model, rather than an absence of earlier
Poisson-noise analysis. The calculation below uses the identical-species model
with a synthetic fixed Poisson background.

[emitter_published_parameters.py](../examples/emitter_published_parameters.py)
takes $(M,p)=(40,0.2)$ and $(100,0.1)$ from Fig. 7(a,b) of the published
2022 paper, and $(8,0.1)$ from the single-species example in Section V.A,
Fig. 3 of the published 2023 follow-up.
It adds an independent Poisson background $b$ per pulse and compares three
specified estimators of $M$ in 200 Monte Carlo repetitions with seed 2026:

- **Binomial baseline:** a finite-search integer binomial likelihood fit,
  applied as if there were no background. This is a local implementation of the
  background-free model, not a reproduction of the papers' software.
- **Cancellation:** factorial cumulants 2 and 3, which the background does not
  change ($\kappa_2=-Mp^2$, $\kappa_3=2Mp^3$).
- **Calibration:** a moment estimate using $b$ estimated from additional
  source-off pulses numbering 10% of the signal pulses.

The full simulation grid uses $b\in\{0,0.1,0.5,1\}$ and
$N\in\{10^4,10^5,10^6\}$ signal pulses. The binomial baseline is evaluated
only for $N\le10^5$; the two moment procedures cover the full grid. The table
below displays the $b=0.1,1$ rows at $N=10^5$.

The two moment procedures return continuous $M$ estimates, without rounding
them to integer emitter counts. Both require $M\ge1$ and $0<p\le1$, in
addition to the signs needed by their formulas. Cancellation estimates $M,p$
from cumulants 2 and 3 alone. The value $\widehat b=\overline Y-\widehat M\widehat p$
is retained as a separate diagnostic; a negative value does not discard the
emitter estimate. Such an estimate is not a jointly admissible fit of all three
model parameters. Calibration uses the source-off mean and retains its
nonnegative-background requirement. These checks do not establish statistical
accuracy.
The likelihood baseline searches a finite integer range and records a search
cap hit as a failure. Undefined, inadmissible and capped results are counted,
not replaced by point estimates. For the moment procedures, the output field
`raw_finite_summary` retains finite values of the ratios actually computed.
For cancellation, it already conditions on $\widehat\kappa_2<0$ and
$\widehat\kappa_3>0$, before the
count/probability guards. It is not a summary of every algebraically finite
ratio across all attempts.

For $b>0$ the observed count law has unbounded support, whereas every finite
binomial law has bounded support. A binomial fit with nonzero likelihood must
have $M\ge\max Y$ in the sample. This baseline is consequently a finite-sample
comparison, not a consistent background-misspecified estimator with a claimed
finite population limit.

Estimating unknown binomial $n$ and $p$ has a substantial statistical literature.
[Johnson–Kemp–Kotz (2005), section 3.8](references.md#classical-count-distribution-reference)
is a standard reference for binomial estimation; the access notes distinguish
the inspected contents from the chapter text.
[Olkin, Petkau and Zidek (1981)](https://doi.org/10.1080/01621459.1981.10477697)
study instability of moment and likelihood estimates at small $p$.
[Schmidt-Hieber, Schneider and colleagues (2021)](https://doi.org/10.1214/21-AOS2096)
give Bayesian concentration results under explicit assumptions, following the
[Schneider, Staudt and Munk numerical study (2019)](https://doi.org/10.1007/978-3-030-30611-3_4).
Their core model is independent binomial observations. This synthetic
comparison uses a capped likelihood baseline and different moment estimators;
it does not benchmark those proposed estimators or transfer their guarantees
to Poisson-contaminated counts. See the [reference and access notes](references.md#estimation).

At $10^5$ signal pulses, the cancellation column shows the median estimate of
$M$ and the interquartile range [25th, 75th percentile]. The other columns show
the mean (relative RMSE). Every cell gives failed attempts out of 200. All
summaries condition on a returned estimate under the stated domain checks;
quartiles use linear interpolation (`numpy.quantile`, `method="linear"`).
These ranges describe the central half of the successful synthetic estimates,
not confidence intervals or uncertainty bounds for the median.

| $(M,p)$ | $b$ | Binomial baseline: mean (relative RMSE) | Cancellation: median [Q25, Q75] | 10% source-off: mean (relative RMSE) |
| --- | --- | --- | --- | --- |
| (40, 0.2) | 0.1 | 41 (3.18%); 0/200 | 38.5 [31, 51.9]; 0/200 | 40 (1.76%); 0/200 |
| (40, 0.2) | 1 | 50.7 (27%); 0/200 | 38.4 [29.1, 56]; 0/200 | 40.1 (1.94%); 0/200 |
| (100, 0.1) | 0.1 | 102 (4.86%); 0/200 | 86.5 [34.8, 261]; 28/200 | 100 (4.22%); 0/200 |
| (100, 0.1) | 1 | 121 (21.4%); 0/200 | 55 [27, 223]; 44/200 | 99.8 (4.24%); 0/200 |
| (8, 0.1) | 0.1 | 10.2 (28.5%); 0/200 | 7.82 [5.55, 12.4]; 0/200 | 8.04 (4.35%); 0/200 |
| (8, 0.1) | 1 | 40.9 (414%); 0/200 | 6.34 [2.69, 22.1]; 55/200 | 8.08 (10%); 0/200 |

The cancellation mean is unstable: rare estimates with
$\widehat\kappa_3$ close to zero dominate the mean and RMSE through
$\widehat M=-4\widehat\kappa_2^3/\widehat\kappa_3^2$. These diagnostics can
change by orders of magnitude between random seeds and are not reliable
summaries of typical performance. The median and interquartile range still
have Monte Carlo uncertainty and exclude failures. The saved JSON retains
means and RMSEs as tail diagnostics; no estimates are trimmed or winsorized.

Earlier versions of this table also discarded cancellation estimates when
$\widehat b<0$. That extra filter was inappropriate for the stated two-cumulant
procedure and hid large errors. The corrected table retains those estimates:
the six rows respectively include 89, 57, 80, 52, 66 and 28 negative inferred
backgrounds among successful cancellation estimates. For example, at
$(M,p,b)=(100,0.1,0.1)$ all 172 estimates passing the cumulant-sign checks also
pass the count/probability checks, including 80 previously excluded by the
background filter. Their median is 86.5 with interquartile range [34.8, 261],
while the unstable mean is $9.92\times10^3$ and relative RMSE
$7.43\times10^4\%$. The other 28 attempts fail the cumulant-sign checks.

At $(8,0.1,0.5)$ and $10^5$ pulses, 185 successful estimates have median 8.14
and interquartile range [3.96, 19.7]. Twelve attempts fail the sign checks and
three give $M<1$. The tail is not captured by this central range: the unstable
mean is $2.02\times10^4$ and relative RMSE is $2.87\times10^6\%$, the largest
in this particular run. Before the count/probability guards, the 188 estimates
passing the sign checks have median 8.01 and interquartile range [3.82, 19.6].
Failure counts, raw mean/RMSE diagnostics and inferred-background diagnostics
remain in the saved results; conditional summaries still omit failed estimates.

For comparison, matching a background-free binomial's population mean and
variance to $Mp+b$ and $Mp(1-p)+b$ gives a continuous moment estimate

$$
\frac{M_{\mathrm{mom}}}{M}=\left(1+\frac{b}{Mp}\right)^2.
$$

A background equal to 1% of the mean signal raises this population moment
estimate by 2.01%. This calculation explains a possible direction and scale of
misspecification error. It is not an identity for the integer likelihood fit,
a finite-sample bias formula, or a proof about either published estimator.

The next table applies the same two-point calculation to alternatives $M+1$
and, where integer, $1.1M$. These are pairwise testing questions with error sum
at most 10%; they are not guarantees of estimating $M$ to 10% relative error.
Columns give rounded numerical lower bounds on signal pulses:

| $(M,p)$ | $b$ | Alternative | Known $b$ | 10% source-off | Unknown $b$ |
| --- | --- | --- | --- | --- | --- |
| (40, 0.2) | 0.1 | 41 | 3.59e5 | 3.6e5 | 1.58e8 (441x) |
| (40, 0.2) | 0.1 | 44 | 2.63e4 | 2.64e4 | 4.68e4 (1.78x) |
| (40, 0.2) | 1 | 41 | 4.71e5 | 4.77e5 | 2.44e8 (518x) |
| (40, 0.2) | 1 | 44 | 3.44e4 | 3.48e4 | 1.69e7 (492x) |
| (100, 0.1) | 0.1 | 101 | 1.11e7 | 1.11e7 | 2.94e10 (2.65e3x) |
| (100, 0.1) | 0.1 | 110 | 1.33e5 | 1.33e5 | 2.08e5 (1.56x) |
| (100, 0.1) | 1 | 101 | 1.35e7 | 1.35e7 | 3.93e10 (2.93e3x) |
| (100, 0.1) | 1 | 110 | 1.61e5 | 1.61e5 | 4.47e8 (2.78e3x) |
| (8, 0.1) | 0.1 | 9 | 1.04e5 | 1.06e5 | 1.83e7 (177x) |
| (8, 0.1) | 1 | 9 | 4.9e5 | 5.17e5 | 2.28e8 (466x) |

In this recorded execution, 10 of 20 two-parameter local refinements reached
their iteration limit. This total can vary across platforms; the saved
candidates and termination statuses remain available for inspection and are
not reproduction thresholds.

Large lower bounds exhibit difficult pairs under the assumed observation model.
Small lower bounds do not prove that a good estimator exists or exclude other
difficult alternatives. These comparisons therefore cannot assign the observed
estimator errors entirely to an information limit or entirely to an estimator.

The Monte Carlo study compares these three procedures on the stated grid; it
does not prove that source-off calibration removes bias or that cumulant-based
inference is generally impractical. Neither the simulated data nor the
two-point comparisons reanalyse the papers' data or validate detector behavior.

The [published-parameter results](../evidence/emitter-study/published-parameters.json)
retain the testing candidates, Monte Carlo summaries and estimator failures.

## Reproduction

Use a Python 3.13 virtual environment for these optional NumPy/SciPy examples;
the pinned numerical dependencies require Python 3.12 or newer. This is
separate from the dependency-free core library's Python 3.11.4 minimum.
From the repository root, install the hash-locked optional dependencies and
write fresh result files:

```sh
python -m pip install --require-hashes --only-binary=:all: -r examples/requirements-emitters.txt
python -c "from pathlib import Path; Path('build/emitter-study').mkdir(parents=True, exist_ok=True)"
python examples/emitter_background_cost.py --json build/emitter-study/background-cost.json
python examples/emitter_published_parameters.py --part all --json build/emitter-study/published-parameters.json
```

The output paths must be new. The published-parameter program also accepts
`--part bounds` or `--part mc` to run either calculation separately. Result
metadata records the design, numerical-library versions and calculation-source
hashes. Schema version 4 adds conditional and raw medians/quartiles, records
the platform and interpreter, and labels optimizer counts as execution-specific
diagnostics. Both studies were rerun with the original seed and design; no
random seed was selected to improve the reported summaries. Numerical
agreement is a reproduction check, not independent review.

## Limits

- The two-point arguments give necessary inequalities for specified pairs,
  not achievable rates, an optimal estimator or an optimal calibration design.
  Numerical optimization and floating-point probability calculations are not
  formally verified.
- Finite Monte Carlo summaries have simulation uncertainty; the cancellation
  mean and RMSE are particularly unstable because of rare extreme ratios.
  Conditional summaries exclude failed estimates and do not measure the
  unconditional risk of a procedure that can fail. They do not prove
  unbiasedness, coverage or practical superiority beyond the reported cells.
- Emitters are identical, background is fixed and independent, and windows are
  independent. Unequal brightness, blinking, bleaching, dead time and
  threshold detection need separate analysis; see the
  [calibration note](calibration.md) for the click-detector counterexample.
- Signal and source-off windows must share the same fixed background law and
  be mutually independent. Source-off windows are additional observations;
  their acquisition time and experimental feasibility are not assessed here.

Emitter counting from photon coincidences is established experimental work.
[Weston et al. (2002)](https://doi.org/10.1021/ac025730z) measured independent
emitter numbers using time-resolved coincidence analysis.
[Ta, Wolfrum and Herten (2010)](https://doi.org/10.1134/S1054660X09170204)
developed a four-detector photon-antibunching model, and
[Kurz et al. (2013)](https://doi.org/10.1002/smll.201300619) tested counting by
photon statistics (CoPS) on DNA origami with controlled labeling and equal dye
brightness. [Grußmayer and Herten (2017)](https://doi.org/10.1039/C7CP00363C)
studied how brightness, photostability and acquisition settings affect CoPS.
Its detector-specific multiple-photon probabilities include optical geometry
and a low-probability background component; they should not be equated with
the ideal additive count model used here.

[Li et al. (2022)](https://doi.org/10.1364/OE.454412) already analyze additive
Poisson noise, whereas their [2023 follow-up](https://doi.org/10.1116/5.0162501)
leaves background outside its multi-species model. The present synthetic
comparisons do not reproduce the Weston or CoPS experiments or benchmark their
estimators.
Their physical demonstrations support their studied setups, not detector
validation for this repository. See the [reference and access notes](references.md)
for the inspected sources.

See [research process and limitations](../PROVENANCE.md) for the full
disclaimer and development-process disclosure.
