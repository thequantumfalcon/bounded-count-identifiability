import PoissonFactorialMomentsV1
import CountD1BackgroundUncertainty

/-!
Finite mixtures of actual Bernoulli-plus-Poisson product measures.
All mixture components share the Bernoulli parameter. No measurement,
calibration or cross-window independence is asserted.
-/

noncomputable section
open MeasureTheory ProbabilityTheory CountPoissonObservation CountD1LawBridge
open scoped BigOperators NNReal ENNReal

namespace CountFiniteMixedPoisson

variable {I : Type*} [Fintype I]

def component (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0) :
    Measure (Fin 2 × ℕ) :=
  independentPairMeasure 1 (bernoulliMass p) (bernoulliMass_isBoundedLaw p hp0 hp1) r

def mixture (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (w r : I → ℝ≥0) :
    Measure (Fin 2 × ℕ) := ∑ i, w i • component p hp0 hp1 (r i)

def rateMean (w r : I → ℝ≥0) : ℝ := ∑ i, (w i : ℝ) * r i

def rateVariance (w r : I → ℝ≥0) : ℝ :=
  ∑ i, (w i : ℝ) * ((r i : ℝ) - rateMean w r)^2

def observedMean (μ : Measure (Fin 2 × ℕ)) : ℝ :=
  ∫ ω, (((ω.1 : ℕ) + ω.2 : ℕ) : ℝ) ∂μ

def observedSecond (μ : Measure (Fin 2 × ℕ)) : ℝ :=
  (∫ ω, (((ω.1 : ℕ) + ω.2).descFactorial 2 : ℝ) ∂μ) - (observedMean μ)^2

theorem mixture_isProbability (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    IsProbabilityMeasure (mixture p hp0 hp1 w r) := by
  have hi (i : I) := independentPairMeasure_isProbability 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) (r i)
  constructor
  simp only [mixture, Measure.finsetSum_apply, Measure.smul_apply,
    component, measure_univ]
  change (∑ i, (w i : ℝ≥0∞) * 1) = 1
  simp only [mul_one]
  exact_mod_cast hw

private theorem component_factorial (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (r : ℝ≥0) (k : ℕ) :
    Integrable (fun ω : Fin 2 × ℕ => (((ω.1 : ℕ) + ω.2).descFactorial (k+1) : ℝ))
        (component p hp0 hp1 r) ∧
    (∫ ω : Fin 2 × ℕ, (((ω.1 : ℕ) + ω.2).descFactorial (k+1) : ℝ)
      ∂component p hp0 hp1 r) = (r : ℝ)^(k+1) + (k+1 : ℝ)*p*(r : ℝ)^k := by
  have := independentPairMeasure_isProbability 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) r
  obtain ⟨hX, hY, hXY⟩ := independentPairMeasure_hasLaws 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) r
  exact PoissonFactorialMomentsV1.bernoulli_poisson_descFactorial p hp0 hp1 r
    Prod.fst Prod.snd hX hY hXY k

/-- The integrability and all positive-order factorial moments follow from actual laws. -/
theorem mixture_factorial (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (k : ℕ) :
    Integrable (fun ω : Fin 2 × ℕ => (((ω.1 : ℕ) + ω.2).descFactorial (k+1) : ℝ))
        (mixture p hp0 hp1 w r) ∧
    (∫ ω : Fin 2 × ℕ, (((ω.1 : ℕ) + ω.2).descFactorial (k+1) : ℝ)
      ∂mixture p hp0 hp1 w r) =
        ∑ i, (w i : ℝ) * ((r i : ℝ)^(k+1) + (k+1 : ℝ)*p*(r i : ℝ)^k) := by
  have hi (i : I) := (component_factorial p hp0 hp1 (r i) k).1.smul_measure_nnreal
    (c := w i)
  constructor
  · exact integrable_finsetSum_measure.mpr (fun i _ => hi i)
  · unfold mixture
    rw [integral_finsetSum_measure (fun i _ => hi i)]
    simp only [integral_smul_nnreal_measure, NNReal.smul_def, smul_eq_mul,
      (component_factorial p hp0 hp1 _ k).2]

theorem rateVariance_nonneg (w r : I → ℝ≥0) : 0 ≤ rateVariance w r := by
  unfold rateVariance
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (w i).coe_nonneg (sq_nonneg _))

private theorem weight_sum_real (w : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    ∑ i, (w i : ℝ) = 1 := by exact_mod_cast hw

theorem rateVariance_eq (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    rateVariance w r = (∑ i, (w i : ℝ) * (r i : ℝ)^2) - (rateMean w r)^2 := by
  unfold rateVariance
  have heq (i : I) : (w i : ℝ) * ((r i : ℝ) - rateMean w r)^2 =
      (w i : ℝ)*(r i : ℝ)^2 - 2*rateMean w r*((w i : ℝ)*r i) +
        (w i : ℝ)*(rateMean w r)^2 := by ring
  simp_rw [heq, Finset.sum_add_distrib, Finset.sum_sub_distrib,
    ← Finset.mul_sum, ← Finset.sum_mul, weight_sum_real w hw]
  change _ - 2*rateMean w r*rateMean w r + 1*(rateMean w r)^2 = _
  ring

theorem mixture_mean (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    observedMean (mixture p hp0 hp1 w r) = p + rateMean w r := by
  have h := (mixture_factorial p hp0 hp1 w r 0).2
  simp only [Nat.descFactorial_one, pow_one, Nat.cast_zero,
    zero_add, one_mul, pow_zero, mul_one] at h
  change _ = _ at h
  rw [observedMean, h]
  simp_rw [mul_add, Finset.sum_add_distrib, ← Finset.sum_mul, weight_sum_real w hw]
  simp [rateMean, add_comm]

/-- The second factorial cumulant of the actual finite-mixture law. -/
theorem mixture_second (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    observedSecond (mixture p hp0 hp1 w r) =
      CountD1BackgroundUncertainty.perturbedSecond p (rateVariance w r) := by
  rw [observedSecond, (mixture_factorial p hp0 hp1 w r 1).2,
    mixture_mean p hp0 hp1 w r hw, rateVariance_eq w r hw]
  simp only [Nat.cast_one, one_add_one_eq_two, pow_one, mul_add, Finset.sum_add_distrib]
  have heq (i : I) : (w i : ℝ)*(2*p*(r i : ℝ)) = 2*p*((w i : ℝ)*r i) := by ring
  simp_rw [heq, ← Finset.mul_sum]
  unfold CountD1BackgroundUncertainty.perturbedSecond rateMean
  ring

/-- A deterministic rate range supplies a variance allowance; it is not inferred from data. -/
theorem rateVariance_le_range (w r : I → ℝ≥0) (hw : ∑ i, w i = 1)
    (L U : ℝ) (hrL : ∀ i, L ≤ (r i : ℝ)) (hrU : ∀ i, (r i : ℝ) ≤ U) :
    rateVariance w r ≤ (U-L)^2/4 := by
  have hi (i : I) : (r i : ℝ)^2 ≤ (L+U)*(r i : ℝ)-L*U := by
    nlinarith [mul_nonneg (sub_nonneg.mpr (hrL i)) (sub_nonneg.mpr (hrU i))]
  have hs := Finset.sum_le_sum (s := Finset.univ)
    (fun i _ => mul_le_mul_of_nonneg_left (hi i) (w i).coe_nonneg)
  have heq (i : I) : (w i : ℝ)*((L+U)*(r i : ℝ)-L*U) =
      (L+U)*((w i : ℝ)*r i) - L*U*(w i : ℝ) := by ring
  simp_rw [heq, Finset.sum_sub_distrib, ← Finset.mul_sum, weight_sum_real w hw] at hs
  rw [rateVariance_eq w r hw]
  change (∑ i, (w i : ℝ)*(r i : ℝ)^2) ≤ (L+U)*rateMean w r-L*U*1 at hs
  nlinarith [sq_nonneg (2*rateMean w r-(L+U))]

/-- Both compared actual mixture laws must satisfy the same variance allowance. -/
theorem mixture_stability {J : Type*} [Fintype J]
    (p q : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hq0 : 0 ≤ q) (hq1 : q ≤ 1)
    (w r : I → ℝ≥0) (v s : J → ℝ≥0) (hw : ∑ i, w i = 1) (hv : ∑ j, v j = 1)
    (η ε δ : ℝ) (hr : rateVariance w r ≤ η) (hs : rateVariance v s ≤ η)
    (hκ : |observedSecond (mixture p hp0 hp1 w r) -
      observedSecond (mixture q hq0 hq1 v s)| ≤ ε)
    (hμ : |observedMean (mixture p hp0 hp1 w r) -
      observedMean (mixture q hq0 hq1 v s)| ≤ δ) :
    |p-q| ≤ Real.sqrt (ε+η) ∧ |rateMean w r-rateMean v s| ≤ δ+Real.sqrt (ε+η) := by
  rw [mixture_second p hp0 hp1 w r hw, mixture_second q hq0 hq1 v s hv] at hκ
  have h := CountD1BackgroundUncertainty.bounded_observation_error
    (observedMean (mixture p hp0 hp1 w r)) (observedMean (mixture q hq0 hq1 v s))
    p q (rateVariance w r) (rateVariance v s) η ε δ hp0 hq0
    (rateVariance_nonneg w r) hr (rateVariance_nonneg v s) hs hκ hμ
  simpa only [CountD1Stability.backgroundFromMean, mixture_mean p hp0 hp1 w r hw,
    mixture_mean q hq0 hq1 v s hv, add_sub_cancel_left] using h

end CountFiniteMixedPoisson
