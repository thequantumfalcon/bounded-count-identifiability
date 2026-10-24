# Synthetic count experiment

This standard-library example samples three prescribed count models and compares
unbiased empirical factorial moments with exact population targets. It supplements
the mathematical checks with a reproducible software experiment; it is synthetic,
not a measurement or a test of a physical detector.

Run with Python 3.11+ and a new output directory:

```sh
python examples/count_model_stress.py --output /path/to/new/count-stress
```

The script refuses to reuse an existing directory. It requires no packages,
network access, accelerator or credentials. The fixed design is 200 repetitions
of 2,000 windows for each of three models: 1,200,000 counts altogether. It uses
bounded blocks, a cooperative 180-second deadline and a count-overflow error
rather than clipping. Hosted runs also need an external job timeout. Raw counts
occupy 2,400,000 bytes; execution records and summaries add a small amount.

## Fixed design and targets

Let $Y=X+Z$, where $X$ is Bernoulli with parameter $p$ and, given the rate $R$,
$Z$ is Poisson with rate $R$. The prescribed ideal model makes the source
independent of the rate and background; windows and model samples are independent.
For the mixture, a fresh rate is chosen in every window.

| Model | $p$ | Rate $R$ | $m_1$ | $m_2$ | $m_3$ |
| --- | --- | --- | --- | --- | --- |
| Fixed baseline | $3/10$ | $1/2$ | $4/5$ | $11/20$ | $7/20$ |
| Matched mixture | $3/10$ | $0$ or $3/5$, equal probabilities | $3/5$ | $9/25$ | $27/100$ |
| Matched Poisson | $0$ | $3/5$ | $3/5$ | $9/25$ | $27/125$ |

Here $m_r=\mathbb E[(Y)_r]$ and $(y)_r=y(y-1)\cdots(y-r+1)$. The last two models
match the first two factorial moments but differ at the third by $27/500=0.054$.
This is a check of a specified pair; it does not establish identification for
arbitrary random background rates.

The design, seed 20261021, sample count, targets and uncertainty allocations were
saved before the first run. SHA-256 derives separate deterministic streams for
each model, repetition and source/rate/background role. Python's pseudorandom
generator and a floating-point Knuth Poisson sampler approximate the intended
probability laws; distinct seeds do not prove stochastic independence.

## Uncertainty calculation

All estimates are averages of $(Y)_r$. The primary statistic is the difference
of the two third factorial-moment averages. No empirical plug-in cumulants are
used. Exact rational calculations supply prescribed-law moments through order
six from

```math
m_r=\mathbb E[R^r]+rp\,\mathbb E[R^{r-1}],\qquad r\geq1,
```

and the identity

```math
(y)_r^2=\sum_{j=0}^{r}\binom rj^2 j!\,(y)_{2r-j}
```

gives each statistic's variance. For $N=400000$ windows per model, a mean's
Chebyshev radius is $\sqrt{\mathrm{Var}((Y)_r)/(N\alpha)}$. The difference
uses the sum of the two model variances divided by $N$, under the prescribed
independent-model benchmark.

The primary contrast receives $\alpha=1/40$. Each of the nine marginal moment
means receives $\alpha=1/360$. A union bound gives simultaneous ideal-IID
benchmark coverage at least $1-(1/40+9/360)=0.95$; this union bound does not need
the ten interval events to be independent. Rational outward square-root
enclosures on a $10^{-12}$ grid make the reported radii conservative.

These benchmark intervals know the generating-law variances. They are not a
data-derived uncertainty procedure for an unknown law. The fixed-rate confidence
ceilings elsewhere in this repository are not applied to the mixture. Pseudorandom
finite-precision execution is not itself a proof of the ideal-IID coverage claim.

## Retained first-run result

The [compact execution record](../evidence/count-stress-check.json) binds these
statistics to a replay of the final public-source bytes, with matching raw-data
hashes. The original design and first-run outcome were retained.

The recorded local Python 3.11 replay saved all 1,200,000 counts in 2.75 seconds
on the development machine. Runtime is descriptive, not a hardware benchmark.

| Model | Empirical $m_1$ | Empirical $m_2$ | Empirical $m_3$ |
| --- | --- | --- | --- |
| Fixed baseline | 0.800005 | 0.551180 | 0.352140 |
| Matched mixture | 0.6016575 | 0.363890 | 0.274815 |
| Matched Poisson | 0.599445 | 0.358670 | 0.214500 |

The observed third-order difference was 0.060315. Its preallocated ideal-IID
benchmark interval was $[0.027614889908,\ 0.093015110092]$, containing 0.054 and
excluding zero. All ten targets were inside their respective intervals in this
run. That is one observed outcome, not an empirical estimate of a 95% coverage
rate. Inclusion and separation are always reported; neither is required for the
script or CI to succeed. A deterministic replay checks implementation consistency
without selecting a new seed or discarding the original outcome.

## Outputs and controls

The output directory contains the executed source snapshot, frozen design,
a record of runtime and hashes, all stream seeds, per-repetition integer sums
and three raw count files. Files ending in `.counts.u16le` contain unsigned 16-bit
little-endian counts in repetition-major, then window-major order, with shape
`[200, 2000]` and no header. The execution record lists each count file's SHA-256
and size; it also hashes the other saved artifacts. Binary readback recomputes all
factorial sums and checks each raw file's hash again.

The hosted `stress` job runs this program as part of required CI, with a
five-minute external timeout. Its `count-stress-ci-receipt` artifact preserves
the complete output for 14 days. Raw binary counts are not committed to Git;
retain the downloaded artifact if a longer-lived data record is needed. The
executed source and frozen protocol make a fresh reproduction possible after
artifact expiration. Inspect the run for the exact commit being reviewed.

Deterministic checks exercise Bernoulli endpoints, Poisson zero-rate and known
uniform sequences, rate-selection boundaries, factorial product identities and
an independently organized generating-series calculation. Deliberately replacing
the Poisson sampler with rounded rates, or replacing the mixture with its mean
rate in the second-moment formula, must be detected. These controls do not depend
on favorable random draws and do not exhaustively verify the sampler.

The experiment does not establish physical calibration, source–background or
window independence in measured data, optimal sample complexity, originality,
outside human review or a formal proof of the executable. It is a small,
reproducible test of specified synthetic models and their numerical handling.
