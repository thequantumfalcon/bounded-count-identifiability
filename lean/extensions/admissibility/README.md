# Conditional admissibility and recovery

[CountAdmissibility.lean](CountAdmissibility.lean) imports the
[largest-root module](../largest-root/README.md). Its mass function takes the
degree-$D$ truncation of a series $S$, substitutes $t=z-1$, and extracts its
coefficients as candidate probabilities.

The sufficiency theorem assumes $S(0)=1$, $[t^{D+1}]S=0$, and nonnegative
candidate masses through $D$. It proves that those masses form a bounded law
and that their factorial cumulants agree with those of $S$ through $D+1$.
This is a genuine existence result under the stated series assumptions.

The recovery theorem starts with an existing bounded law $p$. It assumes the
same normalization and vanishing coefficient for $S$, agreement of higher
log coefficients with the law, and that the first log coefficient of $S$ is
at least the law's mean. The largest-root bound then forces equal means and
the reconstructed masses equal $p$ on its support.

That last inequality is an explicit hypothesis (`hρ`), not an automatically
verified property of arbitrary supplied cumulants. The module does not construct
the cumulant-only exponential series or package the complete largest-root
admissibility equivalence for an arbitrary cumulant vector. The
[written criterion](../../../docs/reconstruction.md#exact-admissibility)
includes those remaining connections. It also does not supply an executable
root-isolation or sign-decision procedure.

For a written control of why the inequality matters, take $D=1$ and the law
$\mathrm{Bernoulli}(1/2)$. The series $S=\exp(-t/2-t^2/8)$ has the same
second factorial cumulant and zero coefficient at $t^2$, but its first
log coefficient is $-1/2$. Truncation reconstructs masses $(3/2,-1/2)$.
Thus matching the higher cumulant and vanishing top coefficient alone cannot
justify recovery of the law. This example is not an additional Lean theorem.

The [source manifest](source_manifest.json) binds this module and these roots:

- `CountAdmissibility.logOf_coeff_congr`
- `CountAdmissibility.natDegree_shifted_le`
- `CountAdmissibility.factorialPGF_mass`
- `CountAdmissibility.admissible_of_nonneg_masses`
- `CountAdmissibility.mass_eq_of_admissible`

Use the [shared research verification and replay commands](../largest-root/README.md#reproduce).
They compile fresh project artifacts and audit these roots in a separate Lean
invocation. No new axiom, observation-model assumption or originality claim
is supplied by successful verification.
