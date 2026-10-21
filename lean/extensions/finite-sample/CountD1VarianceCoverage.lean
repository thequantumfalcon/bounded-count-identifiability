import Mathlib.Probability.Moments.Variance
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
Algebraic variance ceilings and a conditional two-estimator Chebyshev bound.
The factorial moments and estimator variance bounds are explicit hypotheses;
their derivation from an IID Bernoulli-plus-Poisson sample is not asserted here.
The positive-ceiling radius corollary excludes zero ceilings. No novelty claim.
-/

noncomputable section
open MeasureTheory ProbabilityTheory

namespace CountD1VarianceCoverage

theorem factorial_square_identity (y : ℝ) :
    (y * (y - 1)) ^ 2 =
      y * (y - 1) * (y - 2) * (y - 3) +
      4 * (y * (y - 1) * (y - 2)) + 2 * (y * (y - 1)) := by
  ring

theorem first_variance_identity (p b : ℝ) :
    (b ^ 2 + 2 * p * b) + (p + b) - (p + b) ^ 2 = b + p * (1 - p) := by
  ring

theorem second_variance_identity (p b : ℝ) :
    (b ^ 4 + 4 * p * b ^ 3) + 4 * (b ^ 3 + 3 * p * b ^ 2) +
      2 * (b ^ 2 + 2 * p * b) - (b ^ 2 + 2 * p * b) ^ 2 =
      4 * b ^ 3 + (12 * p + 2 - 4 * p ^ 2) * b ^ 2 + 4 * p * b := by
  ring

theorem first_variance_ceiling (p b B : ℝ) (hb : b ≤ B) :
    b + p * (1 - p) ≤ B + 1 / 4 := by
  nlinarith [sq_nonneg (p - 1 / 2)]

theorem second_variance_ceiling (p b B : ℝ)
    (_hp : 0 ≤ p) (hp1 : p ≤ 1) (hb : 0 ≤ b) (hbB : b ≤ B) :
    4 * b ^ 3 + (12 * p + 2 - 4 * p ^ 2) * b ^ 2 + 4 * p * b ≤
      4 * B ^ 3 + 10 * B ^ 2 + 4 * B := by
  have hB : 0 ≤ B := hb.trans hbB
  have hcoeff : 12 * p + 2 - 4 * p ^ 2 ≤ 10 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hp1) (show 0 ≤ 2 - p by linarith)]
  have hcoefmul := mul_le_mul_of_nonneg_right hcoeff (sq_nonneg b)
  have hsquare : b ^ 2 ≤ B ^ 2 := pow_le_pow_left₀ hb hbB 2
  have hcube : b ^ 3 ≤ B ^ 3 := pow_le_pow_left₀ hb hbB 3
  have hpb : p * b ≤ b := by nlinarith [mul_nonneg (sub_nonneg.mpr hp1) hb]
  nlinarith

theorem variance_ratio_radius (W N α v : ℝ)
    (hW : 0 < W) (hN : 0 < N) (hα : 0 < α) (hv : v ≤ W / N) :
    v / (Real.sqrt (2 * W / (N * α))) ^ 2 ≤ α / 2 := by
  have hden : 0 < 2 * W / (N * α) := by positivity
  rw [Real.sq_sqrt hden.le]
  apply (div_le_iff₀ hden).2
  have heq : α / 2 * (2 * W / (N * α)) = W / N := by
    field_simp
  rwa [heq]

section Probability
variable {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]

/-- The zero-ceiling case is deterministic almost surely, including at radius zero. -/
theorem zero_variance_deterministic
    (T : Ω → ℝ) (hT : MemLp T 2 μ) (m : ℝ)
    (hm : (∫ ω, T ω ∂μ) = m) (hv : variance T μ ≤ 0) :
    ∀ᵐ ω ∂μ, T ω = m := by
  have hz : variance T μ = 0 := le_antisymm hv (variance_nonneg T μ)
  simpa only [hm] using ae_eq_integral_of_variance_eq_zero hT hz

/-- A genuine probability bound. It requires no independence between the estimators. -/
theorem simultaneous_chebyshev
    (T₁ T₂ : Ω → ℝ) (hT₁ : MemLp T₁ 2 μ) (hT₂ : MemLp T₂ 2 μ)
    (m₁ m₂ r₁ r₂ α : ℝ)
    (hm₁ : (∫ ω, T₁ ω ∂μ) = m₁) (hm₂ : (∫ ω, T₂ ω ∂μ) = m₂)
    (hr₁ : 0 < r₁) (hr₂ : 0 < r₂) (hα : 0 ≤ α)
    (hv₁ : variance T₁ μ / r₁ ^ 2 ≤ α / 2)
    (hv₂ : variance T₂ μ / r₂ ^ 2 ≤ α / 2) :
    μ {ω | r₁ ≤ |T₁ ω - m₁| ∨ r₂ ≤ |T₂ ω - m₂|} ≤ ENNReal.ofReal α := by
  have h₁ := meas_ge_le_variance_div_sq hT₁ hr₁
  have h₂ := meas_ge_le_variance_div_sq hT₂ hr₂
  rw [hm₁] at h₁
  rw [hm₂] at h₂
  calc
    μ {ω | r₁ ≤ |T₁ ω - m₁| ∨ r₂ ≤ |T₂ ω - m₂|} ≤
        μ {ω | r₁ ≤ |T₁ ω - m₁|} + μ {ω | r₂ ≤ |T₂ ω - m₂|} :=
      measure_union_le _ _
    _ ≤ ENNReal.ofReal (α / 2) + ENNReal.ofReal (α / 2) :=
      add_le_add (h₁.trans (ENNReal.ofReal_le_ofReal hv₁))
        (h₂.trans (ENNReal.ofReal_le_ofReal hv₂))
    _ = ENNReal.ofReal α := by
      rw [← ENNReal.ofReal_add (by positivity) (by positivity)]
      congr 1
      ring

/-- The stated positive-ceiling radii have simultaneous failure probability at most α.
The sample-average variance bounds and unbiasedness are hypotheses, not conclusions. -/
theorem conditional_moment_coverage
    (T₁ T₂ : Ω → ℝ) (hT₁ : MemLp T₁ 2 μ) (hT₂ : MemLp T₂ 2 μ)
    (m₁ m₂ W₁ W₂ N α : ℝ)
    (hm₁ : (∫ ω, T₁ ω ∂μ) = m₁) (hm₂ : (∫ ω, T₂ ω ∂μ) = m₂)
    (hW₁ : 0 < W₁) (hW₂ : 0 < W₂) (hN : 0 < N) (hα : 0 < α)
    (hv₁ : variance T₁ μ ≤ W₁ / N) (hv₂ : variance T₂ μ ≤ W₂ / N) :
    μ {ω | Real.sqrt (2 * W₁ / (N * α)) ≤ |T₁ ω - m₁| ∨
        Real.sqrt (2 * W₂ / (N * α)) ≤ |T₂ ω - m₂|} ≤ ENNReal.ofReal α := by
  apply simultaneous_chebyshev μ T₁ T₂ hT₁ hT₂ m₁ m₂ _ _ α hm₁ hm₂
  · positivity
  · positivity
  · exact hα.le
  · exact variance_ratio_radius W₁ N α _ hW₁ hN hα hv₁
  · exact variance_ratio_radius W₂ N α _ hW₂ hN hα hv₂

end Probability
end CountD1VarianceCoverage

#print axioms CountD1VarianceCoverage.factorial_square_identity
#print axioms CountD1VarianceCoverage.first_variance_identity
#print axioms CountD1VarianceCoverage.second_variance_identity
#print axioms CountD1VarianceCoverage.first_variance_ceiling
#print axioms CountD1VarianceCoverage.second_variance_ceiling
#print axioms CountD1VarianceCoverage.variance_ratio_radius
#print axioms CountD1VarianceCoverage.zero_variance_deterministic
#print axioms CountD1VarianceCoverage.simultaneous_chebyshev
#print axioms CountD1VarianceCoverage.conditional_moment_coverage
