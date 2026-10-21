# Accounting for an uncertain background ceiling

This is a written conditional argument and a future calibration specification.
It is not a new Lean theorem, a calibration measurement, or a claim that any
instrument satisfies the counting model. No new statistical method is claimed.

## Combining calibration and sampling error

Fix the true independent Poisson background mean $b\ge0$, the study sample size
$N>0$ and failure allocation $\alpha>0$. Retain the common-law and unconditional
pairwise-independence assumptions of the [sampling theorem](probability-extensions.md).
For the fixed-rate procedure, define

```math
W_1(B)=B+\tfrac14,\qquad W_2(B)=4B^3+10B^2+4B,
\qquad \rho_r(B)=\sqrt{2W_r(B)/(N\alpha)}.
```

These functions are nondecreasing for nonnegative $B$. Suppose a measurable
random proposed ceiling $\widehat B$ has a separately justified guarantee
$\Pr(\widehat B<b)\le\delta$. The sampling theorem applied to the deterministic
valid ceiling $B=b$ gives probability at most $\alpha$ to the event $A$ that
either empirical moment error exceeds its radius $\rho_r(b)$.

Outside $A\cup\lbrace\widehat B<b\rbrace$, the radii at $\widehat B$ are at least
those at $b$, and $0\le b\le\widehat B$. Both true moments therefore lie in the
empirical box and the true pair $(p,b)$ satisfies its model constraints. Clipping
preserves feasibility. Thus the exact projected region $C(\widehat B)$ satisfies

```math
\lbrace p\notin C(\widehat B)\rbrace
\subseteq A\cup\lbrace\widehat B<b\rbrace,
\qquad \Pr\bigl(p\notin C(\widehat B)\bigr)\le\alpha+\delta.
```

This inclusion does not assume independence between calibration and study data.
It does require the original unconditional study-window assumptions and fixed
$N$ and $\alpha$. Adaptive exclusions, stopping or significance allocation need
their own argument. Negative proposed ceilings belong to the calibration-failure
event and cannot be treated as a successful inference. For example, allocations
$\alpha=0.04$ and $\delta=0.01$ give a total failure allowance of $0.05$.

## A possible fixed-rate source-off calibration

Assume $M\ge1$ preselected equal-duration source-off windows are independent
Poisson counts with the same fixed mean $b$ as the study background. Their sum
$K$ has law $\operatorname{Poisson}(Mb)$. For $0<\delta<1$, the standard one-sided
upper limit uses the root

```math
e^{-u_K}\sum_{j=0}^{K}\frac{u_K^j}{j!}=\delta,
\qquad \widehat B=u_K/M.
```

The Poisson CDF is decreasing in its mean; its inversion gives
$\Pr(\widehat B<b)\le\delta$. Equivalently, $u_K$ is half the chi-square
$(1-\delta)$ quantile with $2(K+1)$ degrees of freedom. At zero observed counts,
$u_0=-\log\delta$: an all-zero record does not justify setting $B=0$.
The [EPA MARLAP manual, section 19.5.3.2, printed page 19-40](https://www.epa.gov/sites/default/files/2015-05/documents/402-b-04-001c-19-final.pdf)
gives the Poisson/chi-square confidence construction. The one-sided allocation
and its composition with this project's region are the application described here.

No numerical implementation of this calibration limit is certified here.
Exposure conversion, upward numerical enclosure and any allowance transferring
background conditions from calibration to study must be justified separately.
A matching mean or variance does not establish the assumed Poisson law.

## A mixture's largest component cannot be inferred this way

Consider any deterministic rule returning a finite bound $c$ on an all-zero
calibration record of length $M$. Choose a two-component rate mixture with
probability $1-\varepsilon$ at zero and $\varepsilon$ at $H>c$, redrawn
independently each window. Its component maximum is $H$. With probability at
least $(1-\varepsilon)^M$, every selected rate is zero, all observations are zero,
and the reported bound is wrong. Taking $\varepsilon>0$ sufficiently small makes
that probability exceed any proposed $\delta<1$.

Consequently, a rule finite on an all-zero record cannot uniformly upper-bound
the largest rate over unrestricted finite mixtures at the claimed level.
Physical rate limits, restrictions on rare components or a different target
are necessary. The fixed-rate calibration construction does not supply the
component ceiling assumed by the finite-mixture theorem.

## Photon counts and detector clicks

Established optical reconstruction work already combines single-photon source
models with Poisson and thermal backgrounds. [Knoll et al. (2023)](https://advanced.onlinelibrary.wiley.com/doi/10.1002/qute.202300062),
equations (7)–(15), model both the photon distribution and a four-branch detector
tree before reconstructing source modes. This is related methodology, not a test
of this repository's theorem or confidence procedure. The inspected
[public deposit](https://zenodo.org/records/7495159) contains expected and
reconstructed mean photon numbers for 15 configurations, without the raw
time-ordered count windows needed for our sampling diagnostics.

The observation model matters even with ideal threshold detection. If
$Z\sim\operatorname{Poisson}(b)$ becomes the binary click
$C=\mathbf 1_{Z\geq1}$, then $C\sim\operatorname{Bernoulli}(q)$ with
$q=1-\exp(-b)$, and its second factorial cumulant is $-q^2$. The identical click
law arises from a Bernoulli$(q)$ source with zero background. In particular,
a pure Poisson input with $b=\log 2$ and a Bernoulli$(1/2)$ input give identical
click records. Even all click moments cannot distinguish these two inputs.

This elementary counterexample concerns thresholded observations; the theorem
assumes additive counts. A binary click record, capped detector output or
inverted response estimate needs a separate response and uncertainty argument.
The distinction is established detector physics, not a new discovery or a
physical measurement by this project.

## Evidence a future study must preserve

Preserve raw time-ordered counts, exposures and source-off/study labels;
instrument settings and response calibration; overflow and dead-time flags;
exclusions; the independently justified source bound; preselected sample and
error allocations; and the numerical enclosure and background-transfer argument.
Hash the data and analysis scripts. Structural checks of these records cannot
establish support, stationarity, independence or detector response by themselves.
