import CountD1VarianceCoverage

/-!
Finite sample means: square integrability, unbiasedness, variance scaling, and
two-moment coverage. Pairwise independence within each family is sufficient;
independence between the two families is neither assumed nor used. Distributional
Bernoulli-plus-Poisson moment formulas remain a separate obligation.
-/

noncomputable section
open MeasureTheory ProbabilityTheory
open scoped BigOperators

namespace CountFiniteSampleMean
variable {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
variable {N : ℕ}

def sampleMean (X : Fin N → Ω → ℝ) (ω : Ω) : ℝ :=
  (N : ℝ)⁻¹ * ∑ i, X i ω

omit [IsProbabilityMeasure μ] in
theorem sampleMean_memLp (X : Fin N → Ω → ℝ) (hX : ∀ i, MemLp (X i) 2 μ) :
    MemLp (sampleMean X) 2 μ := by
  exact (memLp_finsetSum Finset.univ (fun i _ ↦ hX i)).const_mul _

theorem sampleMean_unbiased (X : Fin N → Ω → ℝ) (hX : ∀ i, MemLp (X i) 2 μ)
    (hN : 0 < N) (m : ℝ) (hm : ∀ i, (∫ ω, X i ω ∂μ) = m) :
    (∫ ω, sampleMean X ω ∂μ) = m := by
  have hn : (N : ℝ) ≠ 0 := by positivity
  unfold sampleMean
  rw [integral_const_mul, integral_finsetSum Finset.univ (fun i _ ↦ (hX i).integrable (by norm_num))]
  simp only [hm, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  field_simp

omit [IsProbabilityMeasure μ] in
theorem sampleMean_variance (X : Fin N → Ω → ℝ) (hX : ∀ i, MemLp (X i) 2 μ)
    (hI : Pairwise fun i j ↦ IndepFun (X i) (X j) μ) :
    variance (sampleMean X) μ = (N : ℝ)⁻¹ ^ 2 * ∑ i, variance (X i) μ := by
  unfold sampleMean
  rw [variance_const_mul]
  have hs := IndepFun.variance_sum (s := Finset.univ) (fun i _ ↦ hX i)
    (fun i _ j _ hij ↦ hI hij)
  congr 1
  have heq : (fun ω ↦ ∑ i, X i ω) = ∑ i, X i := by
    funext ω
    simp only [Finset.sum_apply]
  rw [heq]
  exact hs

omit [IsProbabilityMeasure μ] in
theorem sampleMean_variance_ceiling (X : Fin N → Ω → ℝ)
    (hX : ∀ i, MemLp (X i) 2 μ) (hN : 0 < N)
    (hI : Pairwise fun i j ↦ IndepFun (X i) (X j) μ)
    (W : ℝ) (hv : ∀ i, variance (X i) μ ≤ W) :
    variance (sampleMean X) μ ≤ W / N := by
  have hn : (N : ℝ) ≠ 0 := by positivity
  rw [sampleMean_variance μ X hX hI]
  have hs : (∑ i, variance (X i) μ) ≤ (N : ℝ) * W := by
    calc
      _ ≤ ∑ _i : Fin N, W := Finset.sum_le_sum (fun i _ ↦ hv i)
      _ = _ := by simp
  calc
    _ ≤ (N : ℝ)⁻¹ ^ 2 * ((N : ℝ) * W) :=
      mul_le_mul_of_nonneg_left hs (sq_nonneg _)
    _ = W / N := by field_simp

/-- A conditional finite-sample coverage theorem for actual finite sample means. -/
theorem two_sample_means_coverage
    (X₁ X₂ : Fin N → Ω → ℝ) (hX₁ : ∀ i, MemLp (X₁ i) 2 μ)
    (hX₂ : ∀ i, MemLp (X₂ i) 2 μ) (hN : 0 < N)
    (hI₁ : Pairwise fun i j ↦ IndepFun (X₁ i) (X₁ j) μ)
    (hI₂ : Pairwise fun i j ↦ IndepFun (X₂ i) (X₂ j) μ)
    (m₁ m₂ W₁ W₂ α : ℝ)
    (hm₁ : ∀ i, (∫ ω, X₁ i ω ∂μ) = m₁)
    (hm₂ : ∀ i, (∫ ω, X₂ i ω ∂μ) = m₂)
    (hW₁ : 0 < W₁) (hW₂ : 0 < W₂) (hα : 0 < α)
    (hv₁ : ∀ i, variance (X₁ i) μ ≤ W₁)
    (hv₂ : ∀ i, variance (X₂ i) μ ≤ W₂) :
    μ {ω | Real.sqrt (2 * W₁ / ((N : ℝ) * α)) ≤ |sampleMean X₁ ω - m₁| ∨
      Real.sqrt (2 * W₂ / ((N : ℝ) * α)) ≤ |sampleMean X₂ ω - m₂|} ≤ ENNReal.ofReal α := by
  apply CountD1VarianceCoverage.conditional_moment_coverage μ
    (sampleMean X₁) (sampleMean X₂) (sampleMean_memLp μ X₁ hX₁)
    (sampleMean_memLp μ X₂ hX₂) m₁ m₂ W₁ W₂ (N : ℝ) α
    (sampleMean_unbiased μ X₁ hX₁ hN m₁ hm₁)
    (sampleMean_unbiased μ X₂ hX₂ hN m₂ hm₂) hW₁ hW₂
  · positivity
  · exact hα
  · exact sampleMean_variance_ceiling μ X₁ hX₁ hN hI₁ W₁ hv₁
  · exact sampleMean_variance_ceiling μ X₂ hX₂ hN hI₂ W₂ hv₂

end CountFiniteSampleMean

#print axioms CountFiniteSampleMean.sampleMean_memLp
#print axioms CountFiniteSampleMean.sampleMean_unbiased
#print axioms CountFiniteSampleMean.sampleMean_variance
#print axioms CountFiniteSampleMean.sampleMean_variance_ceiling
#print axioms CountFiniteSampleMean.two_sample_means_coverage
