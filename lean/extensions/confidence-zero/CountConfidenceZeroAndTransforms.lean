import CountFiniteSampleMean

/-!
Measurable transforms preserve pairwise independence. Nonnegative variance
ceilings give simultaneous coverage for actual finite sample means, including
zero ceilings, with strict bad events and closed good intervals.

The factorial-statistic specialization assumes square integrability of both
Y and Y * (Y - 1) explicitly. Square integrability of Y alone does not establish
square integrability of this quadratic transform. Distribution-specific moments
and the projection of moment confidence intervals remain separate obligations.
-/

noncomputable section
open MeasureTheory ProbabilityTheory

namespace CountConfidenceZeroAndTransforms

section Transforms
variable {Ω ι β γ : Type*} [MeasurableSpace Ω] [MeasurableSpace β]
  [MeasurableSpace γ] (μ : Measure Ω)

/-- Each coordinate may use a different measurable transform. -/
theorem pairwise_indepFun_measurable_transform
    (X : ι → Ω → β) (f : ι → β → γ) (hf : ∀ i, Measurable (f i))
    (hI : Pairwise fun i j ↦ IndepFun (X i) (X j) μ) :
    Pairwise fun i j ↦ IndepFun (fun ω ↦ f i (X i ω)) (fun ω ↦ f j (X j ω)) μ := by
  intro i j hij
  exact (hI hij).comp (hf i) (hf j)

/-- Independence of the first moment statistics also supplies independence
within the family of second factorial moment statistics. -/
theorem pairwise_indepFun_factorial
    (Y : ι → Ω → ℝ) (hI : Pairwise fun i j ↦ IndepFun (Y i) (Y j) μ) :
    Pairwise fun i j ↦ IndepFun (fun ω ↦ Y i ω * (Y i ω - 1))
      (fun ω ↦ Y j ω * (Y j ω - 1)) μ := by
  exact pairwise_indepFun_measurable_transform μ Y (fun _ y ↦ y * (y - 1))
    (fun _ ↦ measurable_id.mul (measurable_id.sub measurable_const)) hI

end Transforms

section Coverage
variable {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]

/-- Strict failure at radius zero has probability zero when the variance
ceiling is zero. Positive ceilings use the existing Chebyshev radius lemma. -/
theorem nonnegative_ceiling_tail
    (T : Ω → ℝ) (hT : MemLp T 2 μ) (m W N α : ℝ)
    (hm : (∫ ω, T ω ∂μ) = m)
    (hW : 0 ≤ W) (hN : 0 < N) (hα : 0 < α)
    (hv : variance T μ ≤ W / N) :
    μ {ω | Real.sqrt (2 * W / (N * α)) < |T ω - m|} ≤ ENNReal.ofReal (α / 2) := by
  rcases eq_or_lt_of_le hW with hz | hpos
  · have hW0 : W = 0 := hz.symm
    subst W
    have hv0 : variance T μ ≤ 0 := by simpa using hv
    have heq := CountD1VarianceCoverage.zero_variance_deterministic μ T hT m hm hv0
    have hzero : μ {ω | Real.sqrt (2 * (0 : ℝ) / (N * α)) < |T ω - m|} = 0 := by
      apply measure_eq_zero_iff_ae_notMem.mpr
      filter_upwards [heq] with ω hω
      simp [hω]
    rw [hzero]
    exact zero_le
  · have hr : 0 < Real.sqrt (2 * W / (N * α)) := by positivity
    have htail := meas_ge_le_variance_div_sq hT hr
    rw [hm] at htail
    calc
      μ {ω | Real.sqrt (2 * W / (N * α)) < |T ω - m|} ≤
          μ {ω | Real.sqrt (2 * W / (N * α)) ≤ |T ω - m|} := by
        apply measure_mono
        intro ω hω
        change Real.sqrt (2 * W / (N * α)) < |T ω - m| at hω
        change Real.sqrt (2 * W / (N * α)) ≤ |T ω - m|
        exact hω.le
      _ ≤ ENNReal.ofReal (variance T μ / (Real.sqrt (2 * W / (N * α))) ^ 2) := htail
      _ ≤ ENNReal.ofReal (α / 2) := ENNReal.ofReal_le_ofReal
        (CountD1VarianceCoverage.variance_ratio_radius W N α _ hpos hN hα hv)

/-- Failure probability for two closed confidence intervals is at most α,
including either or both zero ceilings. No cross-estimator independence. -/
theorem simultaneous_nonnegative_ceiling_coverage
    (T₁ T₂ : Ω → ℝ) (hT₁ : MemLp T₁ 2 μ) (hT₂ : MemLp T₂ 2 μ)
    (m₁ m₂ W₁ W₂ N α : ℝ)
    (hm₁ : (∫ ω, T₁ ω ∂μ) = m₁) (hm₂ : (∫ ω, T₂ ω ∂μ) = m₂)
    (hW₁ : 0 ≤ W₁) (hW₂ : 0 ≤ W₂) (hN : 0 < N) (hα : 0 < α)
    (hv₁ : variance T₁ μ ≤ W₁ / N) (hv₂ : variance T₂ μ ≤ W₂ / N) :
    μ {ω | Real.sqrt (2 * W₁ / (N * α)) < |T₁ ω - m₁| ∨
      Real.sqrt (2 * W₂ / (N * α)) < |T₂ ω - m₂|} ≤ ENNReal.ofReal α := by
  calc
    _ ≤ μ {ω | Real.sqrt (2 * W₁ / (N * α)) < |T₁ ω - m₁|} +
        μ {ω | Real.sqrt (2 * W₂ / (N * α)) < |T₂ ω - m₂|} := measure_union_le _ _
    _ ≤ ENNReal.ofReal (α / 2) + ENNReal.ofReal (α / 2) := add_le_add
      (nonnegative_ceiling_tail μ T₁ hT₁ m₁ W₁ N α hm₁ hW₁ hN hα hv₁)
      (nonnegative_ceiling_tail μ T₂ hT₂ m₂ W₂ N α hm₂ hW₂ hN hα hv₂)
    _ = ENNReal.ofReal α := by
      rw [← ENNReal.ofReal_add (by positivity) (by positivity)]
      congr 1
      ring

open CountFiniteSampleMean

/-- The estimators here are finite sample means; their L2, expectation and
variance bounds are derived from the per-window premises. -/
theorem two_sample_means_coverage_nonnegative {N : ℕ}
    (X₁ X₂ : Fin N → Ω → ℝ) (hX₁ : ∀ i, MemLp (X₁ i) 2 μ)
    (hX₂ : ∀ i, MemLp (X₂ i) 2 μ) (hN : 0 < N)
    (hI₁ : Pairwise fun i j ↦ IndepFun (X₁ i) (X₁ j) μ)
    (hI₂ : Pairwise fun i j ↦ IndepFun (X₂ i) (X₂ j) μ)
    (m₁ m₂ W₁ W₂ α : ℝ)
    (hm₁ : ∀ i, (∫ ω, X₁ i ω ∂μ) = m₁)
    (hm₂ : ∀ i, (∫ ω, X₂ i ω ∂μ) = m₂)
    (hW₁ : 0 ≤ W₁) (hW₂ : 0 ≤ W₂) (hα : 0 < α)
    (hv₁ : ∀ i, variance (X₁ i) μ ≤ W₁)
    (hv₂ : ∀ i, variance (X₂ i) μ ≤ W₂) :
    μ {ω | Real.sqrt (2 * W₁ / ((N : ℝ) * α)) < |sampleMean X₁ ω - m₁| ∨
      Real.sqrt (2 * W₂ / ((N : ℝ) * α)) < |sampleMean X₂ ω - m₂|} ≤ ENNReal.ofReal α := by
  apply simultaneous_nonnegative_ceiling_coverage μ
    (sampleMean X₁) (sampleMean X₂) (sampleMean_memLp μ X₁ hX₁)
    (sampleMean_memLp μ X₂ hX₂) m₁ m₂ W₁ W₂ (N : ℝ) α
    (sampleMean_unbiased μ X₁ hX₁ hN m₁ hm₁)
    (sampleMean_unbiased μ X₂ hX₂ hN m₂ hm₂) hW₁ hW₂
  · positivity
  · exact hα
  · exact sampleMean_variance_ceiling μ X₁ hX₁ hN hI₁ W₁ hv₁
  · exact sampleMean_variance_ceiling μ X₂ hX₂ hN hI₂ W₂ hv₂

/-- Conditional first and second factorial sample-moment coverage from one
pairwise-independent family. Integrability of the transform is explicit. -/
theorem factorial_sample_means_coverage {N : ℕ}
    (Y : Fin N → Ω → ℝ) (hY : ∀ i, MemLp (Y i) 2 μ)
    (hF : ∀ i, MemLp (fun ω ↦ Y i ω * (Y i ω - 1)) 2 μ) (hN : 0 < N)
    (hI : Pairwise fun i j ↦ IndepFun (Y i) (Y j) μ)
    (m₁ m₂ W₁ W₂ α : ℝ)
    (hm₁ : ∀ i, (∫ ω, Y i ω ∂μ) = m₁)
    (hm₂ : ∀ i, (∫ ω, Y i ω * (Y i ω - 1) ∂μ) = m₂)
    (hW₁ : 0 ≤ W₁) (hW₂ : 0 ≤ W₂) (hα : 0 < α)
    (hv₁ : ∀ i, variance (Y i) μ ≤ W₁)
    (hv₂ : ∀ i, variance (fun ω ↦ Y i ω * (Y i ω - 1)) μ ≤ W₂) :
    μ {ω | Real.sqrt (2 * W₁ / ((N : ℝ) * α)) < |sampleMean Y ω - m₁| ∨
      Real.sqrt (2 * W₂ / ((N : ℝ) * α)) <
        |sampleMean (fun i ω ↦ Y i ω * (Y i ω - 1)) ω - m₂|} ≤ ENNReal.ofReal α := by
  exact two_sample_means_coverage_nonnegative μ Y (fun i ω ↦ Y i ω * (Y i ω - 1))
    hY hF hN hI (pairwise_indepFun_factorial μ Y hI) m₁ m₂ W₁ W₂ α
    hm₁ hm₂ hW₁ hW₂ hα hv₁ hv₂

end Coverage
end CountConfidenceZeroAndTransforms

#print axioms CountConfidenceZeroAndTransforms.pairwise_indepFun_measurable_transform
#print axioms CountConfidenceZeroAndTransforms.pairwise_indepFun_factorial
#print axioms CountConfidenceZeroAndTransforms.nonnegative_ceiling_tail
#print axioms CountConfidenceZeroAndTransforms.simultaneous_nonnegative_ceiling_coverage
#print axioms CountConfidenceZeroAndTransforms.two_sample_means_coverage_nonnegative
#print axioms CountConfidenceZeroAndTransforms.factorial_sample_means_coverage
