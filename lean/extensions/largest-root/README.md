# Largest-root location on the bounded-count core

[CountLargestRoot.lean](CountLargestRoot.lean) proves that the source mean is
the largest real root of a coefficient function built from its factorial
generating series. It uses the existing `CountSeriesCore` and
`BoundedCountLaw` definitions. The source is bound by its
[manifest](source_manifest.json); verification uses the shared audit policy.

For a normalized series $Q$, write $\mu=[t]\log Q$. The defined function is

$$
\operatorname{topCoeff}(D,Q,m)=[t^{D+1}]Q(t)e^{(m-\mu)t}.
$$

The location identity expresses this as a finite polynomial in $m-\mu$.
If every coefficient of $Q$ is nonnegative, $Q(0)=1$, and
$[t^{D+1}]Q=0$, it vanishes at $\mu$ and is positive at every $m>\mu$.
Consequently every real root is at most $\mu$. For a bounded law, the module
proves that $\mu=\sum_{n=0}^{D}np_n$ using the core factorial-PGF definition.
Another theorem connects the top coefficient of any normalized series with
matching higher log coefficients to this function at its own first coefficient.

## Formal scope

This is a universal theorem about the encoded series and laws, not a test on
selected distributions. It does not itself define the cumulant-only Bell
polynomial used in the [written reconstruction](../../../docs/reconstruction.md).
The universal connection from an arbitrary cumulant vector to that explicit
construction remains a written argument. A finite agreement check cannot
replace that formal connection.

Two related modules use this result:

- [Root structure](../root-structure/README.md) proves coefficient and derivative
  identities, including the top-mass derivative.
- [Admissibility](../admissibility/README.md) proves sufficiency of nonnegative
  reconstructed masses and conditional recovery of an existing law.

The exact support-dependent multiplicity theorem, complete arbitrary-vector
admissibility equivalence, general Hölder bound, root-isolation implementation
and statistical estimation guarantees are not formalized by these modules.
No originality or physical-validation claim follows from the proof checks.

## Reproduce

Retrieve the pinned toolchain and dependency cache using the
[formal verification guide](../../README.md). From the repository root run:

```text
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run reconstruction-check
python lean/replay.py --proof-run reconstruction-check --run reconstruction-check
```

The first command recompiles the six core modules and all research extensions
into fresh outputs. Each module's theorem roots are audited by a separate
generated import-only Lean query. The second replays stored project declarations
with Lean's bundled kernel. It is a separate invocation of the same kernel,
not an independent implementation. Use a new run name for each execution.
The published [additional checker record](../../../evidence/reconstruction-kernel-checks.json)
describes a separate source-bound development check and its limitations.

Only `propext`, `Classical.choice` and `Quot.sound` are permitted by the audit.
Upstream dependency caches are reused; the commands do not rebuild every
dependency from source. Standard assumptions and trusted components remain
explicit in the formal verification guide.

## Checked roots

- `CountLargestRoot.top_coeff_of_matching_cumulants`
- `CountLargestRoot.top_coeff_location`
- `CountLargestRoot.top_coeff_at_mean`
- `CountLargestRoot.top_coeff_pos_above_mean`
- `CountLargestRoot.mean_is_largest_root`
- `CountLargestRoot.law_mean_is_largest_root`
