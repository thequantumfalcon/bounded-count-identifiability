# From encoded counts to conditional confidence

[CountCountsConfidence.lean](CountCountsConfidence.lean) connects a finite
record of natural counts to exact rational factorial means, outward confidence
radii and the original real-parameter feasible region. Its ten registered roots
are bound by [source_manifest.json](source_manifest.json).

For a record $y_1,\ldots,y_N$, the computable definitions are

$$
\widehat m_1=N^{-1}\sum_i y_i,\qquad
\widehat m_2=N^{-1}\sum_i y_i(y_i-1).
$$

Both are rational. The formal second definition uses the natural descending
factorial, with a proved identity to the real quadratic, including $y_i=0$.
`firstMean_cast` and `secondMean_cast` connect these computations to the sample
means used by the existing probability theorem.

`checkRadii` checks $N>0$, $B\geq0$, $\alpha>0$, $R_1,R_2\geq0$, and

$$
2(B+1/4)\leq N\alpha R_1^2,\qquad
2(4B^3+10B^2+4B)\leq N\alpha R_2^2.
$$

Its Boolean equivalences and `checkRadii_encloses` prove that acceptance gives
real radii at least as large as the Chebyshev radii. The resulting rational box
has endpoints $\widehat m_1\pm R_1$ and $\widehat m_2\pm R_2$.
`pairFeasible_of_errors` connects simultaneous moment error bounds to the true
pair's membership in the original constraints.

`rational_pair_coverage` and `rational_projected_coverage` prove failure
probability at most $\alpha$ for that box and its projected source region.
`nonempty_decision_coverage` proves that the existing exact Boolean decision
declares the region empty with probability at most $\alpha$. True source and
background parameters can be irrational. The hypotheses are unchanged:
Bernoulli source, fixed independent Poisson background within each window,
common marginal laws, unconditional pairwise independence of observed windows,
and a valid fixed background ceiling. The sample size, ceiling, error level
and supplied radii are fixed for this probability theorem; the proposer derives
its radii only from those design parameters. No independence between the two moment
estimators is needed.

These are repeated-sampling guarantees under the model, not posterior
probabilities assigned to parameters after seeing a particular record. A
certificate does not verify that a measured record came from the assumed model.

## Check a small record

After retrieving the pinned dependencies, run from the repository root with
fresh output names:

```text
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run counts-proof
python lean/check_certificates.py --suite counts --proof-run counts-proof --run counts-controls
python lean/check_certificates.py --suite counts --proof-run counts-proof --run counts-example --counts=0,1,2,4 --background=1 --alpha=1/20
```

The last record is illustrative, not a physical measurement. The runner checks
the explicit encoded counts, both means, both radius inequalities and all four
box endpoints. A separate import-only axiom audit checks each successful
certificate. Default controls include zero background, zero counts, fractional
inputs, the 64-count input limit and a large count. Deliberately wrong averages,
ordinary instead of factorial moments, undersized or negative radii and an
altered endpoint must fail with a normalized `False` residual; an arbitrary
compiler error or timeout does not count as that rejection.

[The Python proposer](../../../examples/d1_count_certificates.py) uses integer
arithmetic to round square roots upward on a rational grid. It accepts at most
64 explicit counts, each at most 12 digits, and exact integer/fraction scalar
inputs. These limits bound certificate size; they do not limit the universal
Lean theorem. Large-record scalable certification remains future work.
`--digits` selects a grid from zero through twelve decimal places; the
certificate checks the actual inequalities, without trusting the proposer to
round correctly. Existing output files and run directories are preserved.

Parsing and acquisition remain outside formal verification. Review the emitted
numeric record against the intended input. Lean, its runtime and upstream
dependencies remain trusted. This adds checked count-to-box arithmetic and
conditional coverage; it does not verify the full Sage program, certify
algebraic endpoint serialization, establish scientific originality or provide
external mathematical review.
