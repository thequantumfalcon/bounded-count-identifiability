# Counting models, correlations and uncertainty

The [identification theorem](theorem.md) concerns a bounded **count** plus an
independent fixed-rate Poisson count. A bounded random **intensity** followed
by Poisson detection is a different model. The distinction matters when
transferring results between count-distribution and optical inverse problems.
This note gives written derivations and limitations; it adds no Lean theorem,
originality claim or physical validation.

For a nonnegative integer-valued variable $Y$, write

$$
C_Y(t)=\log\mathbb E[(1+t)^Y],\qquad
\kappa_r^{\mathrm F}(Y)=C_Y^{(r)}(0).
$$

For a real variable $J$, write $K_J(u)=\log\mathbb E[e^{uJ}]$ and
$\kappa_r(J)=K_J^{(r)}(0)$ for its ordinary cumulants. The bounded variables
and fixed-rate Poisson channels below have generating functions in a
neighborhood of zero, so these derivatives exist.

## Bounded additive counts and mixed Poisson counts

| Model | Generating function | What the higher factorial cumulants describe |
| --- | --- | --- |
| $Y=X+Z$, $X\in\{0,\ldots,D\}$, $Z\sim\mathrm{Poisson}(b)$ independent of $X$ | $C_Y(t)=C_X(t)+bt$ | $\kappa_r^{\mathrm F}(Y)=\kappa_r^{\mathrm F}(X)$ for $r\ge2$ |
| $N\mid J\sim\mathrm{Poisson}(b+\eta J)$, $0\le J\le L$, fixed $b,\eta\ge0$ | $C_N(t)=bt+K_J(\eta t)$ | $\kappa_r^{\mathrm F}(N)=\eta^r\kappa_r(J)$ for $r\ge2$ |

For the second row, conditioning gives the identity directly:

$$
\mathbb E[(1+t)^N]
=\mathbb E[\exp((b+\eta J)t)]
=e^{bt}\mathbb E[e^{\eta tJ}].
$$

Poisson translation, thinning and this mixed-Poisson cumulant relation are
established machinery; see Jørgensen and Kokonendji,
[sections 2.2–2.5, especially equations (2.9) and (2.19)](https://arxiv.org/pdf/1409.7482).
The fixed background contributes only to the first factorial cumulant.
A random rate or dependence requires a different calculation.

The first row permits the repository's identification result from orders
$2,\ldots,D+1$, with the mean additionally identifying $b$. The second row
does **not** inherit that cutoff from an intensity bound $L$: a Poisson count
has unbounded support whenever its rate is positive. Recovering an arbitrary
intensity distribution is a separate moment or mixture problem. Even the sign
at order two distinguishes important cases:

$$
\kappa_2^{\mathrm F}(N)=\eta^2\operatorname{Var}(J)\ge0,
\qquad
\kappa_2^{\mathrm F}(X)=-p^2
\quad\text{if }X\sim\mathrm{Bernoulli}(p).
$$

These statements concern the specified count channels. Threshold clicks need
a response model: a Poisson input becomes a Bernoulli click variable and can
therefore have a negative second factorial cumulant. The
[calibration note](calibration.md#photon-counts-and-detector-clicks) gives an
exact example.

## What an equal count distribution implies

For a specified number observable with $0<\mathbb E[N]<\infty$, define its
normalized factorial correlations, when finite, by

$$
g_N^{(r)}=\frac{\mathbb E[(N)_r]}{\mathbb E[N]^r},
\qquad (N)_r=N(N-1)\cdots(N-r+1).
$$

Equal full distributions $P(N=n)$ give equal $g_N^{(r)}$ at every available
order. In particular, $g_N^{(2)}$ cannot distinguish two identical count laws.
For an ideal single-mode number measurement this is the usual equal-time
number correlation. For counts integrated over a finite window, the statistic
is window-integrated and need not equal an instantaneous optical correlation.
Correlations between different times use joint distributions, which a
single-window marginal does not determine.

Spatial homometry means equality of a specified spatial autocorrelation; it
does not automatically mean equality of a photon-count distribution after
phase fluctuations and detection. The separate
[homometric photon-count model](https://github.com/thequantumfalcon/homometric-photon-counts#construction-and-result)
illustrates this distinction: at its specified setting, two intensity laws
have equal first three moments and unequal fourth moments. With the same
positive phase variance and gain $\eta$, and common background $b\ge0$, their
count means and second factorial moments agree, hence so does $g_N^{(2)}$.
If their fourth intensity-moment difference
is $\Delta m_4$, then

$$
\Delta\kappa_4^{\mathrm F}(N)=\eta^4\Delta m_4.
$$

Indeed, the ordinary fourth cumulant is the fourth moment minus an expression
in the first three moments. This is a conditional use of the transform above,
not a statement that every homometric pair is separated at order four or that
count statistics determine a complete quantum state.

## Unknown detection efficiency or intensity scale

Suppose an emitted count $X$ is independently thinned with efficiency
$0\le\varepsilon\le1$, so $X_{\mathrm{det}}\mid X\sim
\mathrm{Binomial}(X,\varepsilon)$. Then

$$
C_{X_{\mathrm{det}}}(t)=C_X(\varepsilon t),\qquad
\kappa_r^{\mathrm F}(X_{\mathrm{det}})
=\varepsilon^r\kappa_r^{\mathrm F}(X).
$$

This follows from
$\mathbb E[(1+t)^{X_{\mathrm{det}}}\mid X]=(1+\varepsilon t)^X$;
the standard thinning law is also derived in
[Jørgensen and Kokonendji, equations (2.4)–(2.6)](https://arxiv.org/pdf/1409.7482).

For a Bernoulli emitted source, only $\varepsilon p$ is determined by the
detected source law. For example, $(p,\varepsilon)=(1/2,1/2)$ and $(1/4,1)$
both give $\mathrm{Bernoulli}(1/4)$ detected counts. Adding the same independent
Poisson background preserves that equality. The bounded-count theorem can
identify the **detected** source law under its assumptions; it cannot separate
these two emitted-source and efficiency pairs.

Likewise, in the mixed-Poisson model, replacing $J$ by $cJ$ and $\eta$ by
$\eta/c$, for $c>0$, leaves the whole count law unchanged whenever both choices
are allowed. A calibrated scale or additional model restriction is needed to
identify them separately. Here $\eta$ is an intensity-to-count gain; it is not
necessarily a probability bounded by one.

## Population cancellation does not remove sampling uncertainty

An exact population identity does not give an exact finite-record estimate.
For a concrete control, let $Y_1,\ldots,Y_n$ be IID
$\mathrm{Poisson}(b)$, with $n\ge2$. Define

$$
\bar Y=\frac1n\sum_iY_i,\qquad
s^2=\frac1{n-1}\sum_i(Y_i-\bar Y)^2,\qquad
\widehat\kappa_2^{\mathrm F}=s^2-\bar Y.
$$

This estimator is unbiased for the zero population factorial cumulant, but

$$
\operatorname{Var}(\widehat\kappa_2^{\mathrm F})
=\frac{2b^2}{n-1}.
$$

To verify the identity, the Poisson central moments are
$\mu_2=\mu_3=b$ and $\mu_4=b+3b^2$. Expanding the IID sample moments gives

$$
\operatorname{Var}(s^2)
=\frac{\mu_4}{n}-\frac{n-3}{n(n-1)}\mu_2^2
=\frac bn+\frac{2b^2}{n-1},\qquad
\operatorname{Cov}(s^2,\bar Y)=\frac{\mu_3}{n}=\frac bn,
$$

and $\operatorname{Var}(\bar Y)=b/n$. Combining the three terms proves the
stated variance. General unbiased factorial-cumulant estimation and its
sampling variance are treated in
[Müller (2004), Appendix B](https://pmc.ncbi.nlm.nih.gov/articles/PMC1304299/).
The calculation here is a mathematical control, not a measurement or a lower
bound for every possible estimator.

Thus increasing background can increase estimation error even when it leaves
the target population cumulant unchanged. Confidence regions need an explicit
sampling argument and its assumptions. The repository's
[conditional bounds](probability-extensions.md#conditional-confidence-bounds)
require specified window laws, independence conditions and rate ceilings.
Neither finite moment compatibility nor a successful numerical fit certifies
those assumptions; calibration and model checks remain separate obligations.
