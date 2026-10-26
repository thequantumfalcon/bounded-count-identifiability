# Finite-jet stability for bounded laws

This extension proves quantitative bounds for two actual probability mass
functions supported on `0, ..., D`. It connects their factorial generating
polynomials, formal-log cumulants, means, binomial moments and total variation.
It uses the core definitions and the same pinned Lean/Mathlib dependencies.

For $0\leq d\leq D$, suppose both laws have $d$th binomial moment at least
$\eta>0$, and factorial-cumulant errors in orders $2,\ldots,D+1$ are at most
$\varepsilon\geq0$. Put

$$
N=D+1,\quad M=2^D,\quad m=N-d,\quad K=2(N+1)M+1,\quad L=K^N,
$$

$$
C=(N+1)M(M+1)^N,\quad H=NC(L+1)^N,\quad
J=M(L+1)^N,\quad S=1+NM,\quad T=NJS^N/2.
$$

The exported law theorems conclude

$$
|\mu_p-\mu_q|^m\leq m!H\varepsilon/\eta,
\qquad |\mu_p-\mu_q|\leq(m!H\varepsilon/\eta)^{1/m},
$$

$$
\operatorname{TV}(p,q)\leq
T\big((m!H\varepsilon/\eta)^{1/m}+N\varepsilon\big).
$$

Here the binomial moment is $\sum_{j=0}^D p_j\binom jd$, and total variation
is $\frac12\sum_{j=0}^D|p_j-q_j|$. Both moment lower bounds are needed because
the proof may exchange the laws to orient their mean difference. The choice
$d=0$, $\eta=1$ covers every normalized law under the support bound. The
formal theorem also permits $D=0$, where both laws are the point mass at zero.

The constants are conservative and can make the bounds numerically vacuous.
For $0\leq\varepsilon\leq1$, the TV bound implies a pure-power bound using
$\varepsilon\leq\varepsilon^{1/m}$ and the usual real-power identities. That
simplification is a written corollary, not an additional exported Lean root.
The [sharper majorant bounds](../../../docs/reconstruction.md#a-uniform-inverse-bound)
and support-stratum sharpness path are separate written arguments. No optimal
constant, empirical confidence level, observation-model calibration, novelty
or physical measurement is established here.

## Proof structure

The normalized logarithmic derivative gives a finite coefficient recurrence.
An induction bounds coefficient perturbations without evaluating either
logarithmic series at a positive argument. After the mean shift is removed,
one nonnegative coefficient of the shifted series bounds the mean difference.
An explicit triangular inversion of binomial moments then bounds the masses
and their total variation. The proof contains the law-level connections;
its final statements do not merely assume an unexplained recurrence.

## Reproduce

From the repository root, with the [pinned dependencies](../../README.md):

```text
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run quantitative-check
python lean/replay.py --proof-run quantitative-check --run quantitative-check
```

Use a fresh run name. The shared verifier checks the source manifest,
recompiles the six core modules and registered extensions in dependency order,
and uses separate generated import queries for exact root and axiom coverage.
Replay checks saved proof terms with the same Lean kernel; it is not a second
kernel implementation. Existing dependency artifacts remain trusted.
The [recorded kernel checks](../../../evidence/quantitative-jets-check.json)
bind this proof source, its declared roots and the separate checker controls.
Historical receipts describe their recorded sources only. A candidate must
complete these checks before its verification status is reported as passed.

## Audited roots

- `CountQuantitativeJets.ode_coefficient_stability`
- `CountQuantitativeJets.log_derivative_coefficient_bound`
- `CountQuantitativeJets.normalized_log_recurrence`
- `CountQuantitativeJets.normalized_log_bound`
- `CountQuantitativeJets.shifted_coefficient_bound`
- `CountQuantitativeJets.shifted_recurrence`
- `CountQuantitativeJets.support_power_bound`
- `CountQuantitativeJets.law_coefficient_bounds`
- `CountQuantitativeJets.ordered_law_mean_power_bound`
- `CountQuantitativeJets.law_mean_power_bound`
- `CountQuantitativeJets.law_mean_holder_bound`
- `CountQuantitativeJets.binomial_inverse_stability`
- `CountQuantitativeJets.law_moment_difference_bound`
- `CountQuantitativeJets.law_tv_mean_bound`
- `CountQuantitativeJets.law_tv_holder_bound`

The [source manifest](source_manifest.json) binds the exact source bytes and
all fifteen roots. Source alterations, omitted roots, extra axioms and stale
or shadowing artifacts are rejection conditions in the shared checks.
