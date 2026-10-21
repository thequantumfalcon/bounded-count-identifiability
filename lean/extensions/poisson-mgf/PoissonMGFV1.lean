import Mathlib.Probability.Distributions.Poisson.Basic
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Tactic.Ring

/-!
The standard Poisson exponential moment, with integrability established from
the convergent exponential series before identifying the probability integral.
The parameter r includes zero and s ranges over all real numbers.
-/

open MeasureTheory ProbabilityTheory
open scoped NNReal Nat

namespace PoissonMGFV1

private theorem poisson_exp_weight (r : ℝ≥0) (s : ℝ) (n : ℕ) :
    (Real.exp (-(r : ℝ)) * (r : ℝ) ^ n / (n !) : ℝ) *
        Real.exp (s * (n : ℝ)) =
      Real.exp (-(r : ℝ)) * (((r : ℝ) * Real.exp s) ^ n / (n !)) := by
  rw [mul_pow, mul_comm s (n : ℝ), Real.exp_nat_mul]
  ring

private theorem poisson_exp_hasSum (r : ℝ≥0) (s : ℝ) :
    HasSum (fun n : ℕ =>
      (Real.exp (-(r : ℝ)) * (r : ℝ) ^ n / (n !) : ℝ) *
        Real.exp (s * (n : ℝ)))
      (Real.exp ((r : ℝ) * (Real.exp s - 1))) := by
  convert (NormedSpace.expSeries_div_hasSum_exp
    ((r : ℝ) * Real.exp s)).mul_left (Real.exp (-(r : ℝ))) using 1
  · ext n
    exact poisson_exp_weight r s n
  · rw [← Real.exp_eq_exp_ℝ, ← Real.exp_add]
    congr 1
    ring

/-- Every real exponential moment is integrable for the actual Poisson measure. -/
theorem poisson_exp_integrable (r : ℝ≥0) (s : ℝ) :
    Integrable (fun n : ℕ => Real.exp (s * (n : ℝ))) (poissonMeasure r) := by
  rw [integrable_poissonMeasure_iff]
  simpa only [Real.norm_eq_abs, Real.abs_exp] using
    (poisson_exp_hasSum r s).summable

/-- The standard Poisson exponential moment for every nonnegative rate. -/
theorem poisson_exp_integral (r : ℝ≥0) (s : ℝ) :
    (∫ n : ℕ, Real.exp (s * (n : ℝ)) ∂poissonMeasure r) =
      Real.exp ((r : ℝ) * (Real.exp s - 1)) := by
  have h := hasSum_integral_poissonMeasure (poisson_exp_integrable r s)
  simp only [smul_eq_mul] at h
  exact h.unique (poisson_exp_hasSum r s)

end PoissonMGFV1

#print axioms PoissonMGFV1.poisson_exp_integrable
#print axioms PoissonMGFV1.poisson_exp_integral
