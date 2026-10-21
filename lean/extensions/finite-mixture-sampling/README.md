# Sampling bounds for finite mixtures

This extension derives simultaneous first- and second-factorial-moment error
bounds from the actual finite-mixture law in
[CountFiniteMixedPoisson](../finite-mixture/README.md). It uses the pinned
toolchain and existing conditional sampling theorem.

Each mixture component is a Bernoulli(`p`) source plus an independent Poisson
background of rate `r_i`. The weights are nonnegative and sum to one; the same
`p` in `[0,1]` is used in every component. Every component rate lies in a supplied
`[0,B]`, with `B >= 0`. For an observed count `S`, the two population targets are

$$
m_1=p+\sum_i w_i r_i,\qquad
m_2=\sum_i w_i(r_i^2+2pr_i).
$$

The source proves square integrability and the conservative variance ceilings

$$
W_1=B+\tfrac14+\tfrac{B^2}{4},\qquad
W_2=4B^3+10B^2+4B+\tfrac{(B^2+2B)^2}{4}.
$$

The additional terms bound variance between components. For the second
statistic, the component mean `r_i^2+2pr_i` lies in `[0,B^2+2B]`. Finite total
variance and the bounded-range variance inequality give the displayed ceilings.
These established methods and conservative constants carry no originality or
optimality claim.

For `N > 0` windows with the same specified mixture law, assume unconditional
pairwise independence of their observed counts. The theorem bounds the
probability that either sample moment differs from its population target by
more than `sqrt(2 W_r / (N alpha))` by `alpha`, for `alpha > 0`. The usual
confidence interpretation uses `0 < alpha < 1`. The zero-ceiling case is
included. The two sample statistics need not be independent of each other.

Conditional independence given one random rate shared across all windows does
not supply the required premise. See the
[shared-rate counterexample](../../../docs/probability-extensions.md#a-shared-random-rate-can-defeat-averaging).
The theorem assumes the window laws and independence; it does not establish
them from recorded counts or calibration data.

## Registered roots

The eight separately audited roots in `CountFiniteMixedPoissonSampling` are:

- `finite_sum_memLp`
- `finite_total_variance`
- `count_memLp`
- `factorial_two_memLp`
- `mixture_means`
- `count_variance_ceiling`
- `factorial_variance_ceiling`
- `sample_means_coverage`

The generic finite-total-variance lemma takes actual component integrals as
premises and encodes their nonnegative values. The count-specific results
derive those premises from the component probability laws.

## Reproduction and limits

From the repository root after retrieving the pinned dependencies:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run mixture-sampling-check
python lean/replay.py --proof-run mixture-sampling-check --run mixture-sampling-check
```

Use a fresh run name. The verifier checks the source manifest and compiles each
module with `--trust=0`, then checks a generated axiom query separately. Replay
uses the bundled Lean kernel and reused upstream dependency artifacts.

This result supplies moment error bounds for finite mixtures under the stated
assumptions. It does not identify a source from two moments in the broader
model, justify the fixed-rate parameter projection, formalize arbitrary mixing
laws, verify the Python/Sage implementation, validate an apparatus or provide
independent human review.
