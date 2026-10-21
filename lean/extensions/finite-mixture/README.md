# Finite mixed-Poisson background

`CountFiniteMixedPoisson.lean` constructs an actual probability measure as a
finite weighted sum of Bernoulli-plus-Poisson product measures. The weights
are nonnegative and sum to one; rates are nonnegative; every component has
the same Bernoulli parameter `p` in `[0,1]`. Zero weights, repeated or zero
rates, and both Bernoulli endpoints are allowed.

The eight checked roots establish probability normalization, integrability
and all positive-order factorial moments, the nonnegativity and second-moment
formula of the centered rate variance, the observed mean and second factorial
cumulant, a bounded-range variance inequality, and pairwise stability.

Writing `m = sum_i w_i r_i` and `v = sum_i w_i (r_i-m)^2`, the actual mixture
law satisfies

```text
E[S] = p + m
E[(S)_(k+1)] = sum_i w_i (r_i^(k+1) + (k+1) p r_i^k)
E[S(S-1)] - E[S]^2 = -p^2 + v
```

If every rate lies in `[L,U]`, the module proves `v <= (U-L)^2/4`. This is
a conditional way to supply an allowance from a justified rate range. It
does not estimate or validate that range.

For two such models whose rate variances both lie in `[0,eta]`, population
mean difference at most `delta` and second factorial cumulant difference at
most `epsilon` imply

```text
|p-q| <= sqrt(epsilon+eta)
|m-n| <= delta+sqrt(epsilon+eta)
```

The moments follow from actual component probability laws and finite-measure
integration. They are not assumed as premises. The centered rate variance is
an explicit finite sum; the module does not construct a separate latent-rate
random variable or prove a conditional-expectation theorem for arbitrary
mixing measures.

Run the complete research verifier from the repository root after retrieving
the pinned dependencies:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-finite-mixture
```

Use a fresh run name. The shared registry supplies these eight roots to an
import-only query in a separate Lean process; proof-compilation output is not
the axiom audit. The source manifest binds the Lean source's exact bytes.

These are established mixed-Poisson moment and bounded-range variance
arguments, with no originality claim. The standard mixed-Poisson identity is
discussed by [Kuba and Panholzer, Proposition 1(a)](https://arxiv.org/abs/1403.2712).

The extension does not validate an instrument, rate calibration, independence
across windows, or executable inference. The fixed-rate confidence theorem
must not be applied to these mixtures without additional variance and sampling
arguments. Arbitrary mixing distributions and external review remain outside
this formal result.
