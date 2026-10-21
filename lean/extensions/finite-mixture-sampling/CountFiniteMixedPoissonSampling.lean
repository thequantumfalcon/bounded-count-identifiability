import CountFiniteMixedPoisson
import BernoulliPoissonStatisticsV1

/-!
Finite-mixture population variances and simultaneous sample-moment coverage.
Windows have the same specified actual mixture law; their observed counts
are pairwise independent without conditioning on a persistent latent variable.
No executable inference, physical calibration or identification under arbitrary
mixed backgrounds is asserted.
-/

noncomputable section
open MeasureTheory ProbabilityTheory CountFiniteMixedPoisson
open CountPoissonObservation CountD1LawBridge CountProbabilityBridge
open scoped BigOperators NNReal ENNReal

namespace CountFiniteMixedPoissonSampling

variable {I : Type*} [Fintype I]

/-- Square integrability survives a finite nonnegative weighted sum of measures. -/
theorem finite_sum_memLp {Ω : Type*} [MeasurableSpace Ω]
    (ν : I → Measure Ω) (w : I → ℝ≥0) (f : Ω → ℝ)
    (hf : ∀ i, MemLp f 2 (ν i)) : MemLp f 2 (∑ i, w i • ν i) := by
  classical
  have h (s : Finset I) : MemLp f 2 (∑ i ∈ s, w i • ν i) := by
    induction s using Finset.induction_on with
    | empty => simp
    | @insert i s hi ih =>
      rw [Finset.sum_insert hi]
      exact memLp_add_measure.mpr ⟨(hf i).smul_measure_nnreal, ih⟩
  exact h Finset.univ

private theorem weighted_probability {Ω : Type*} [MeasurableSpace Ω]
    (ν : I → Measure Ω) [∀ i, IsProbabilityMeasure (ν i)]
    (w : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    IsProbabilityMeasure (∑ i, w i • ν i) := by
  constructor
  simp only [Measure.finsetSum_apply, Measure.smul_apply, measure_univ]
  change (∑ i, (w i : ℝ≥0∞)*1) = 1
  simp only [mul_one]
  exact_mod_cast hw

/-- Finite total variance, with actual integrals as component-mean premises. -/
theorem finite_total_variance {Ω : Type*} [MeasurableSpace Ω]
    (ν : I → Measure Ω) [∀ i, IsProbabilityMeasure (ν i)]
    (w a : I → ℝ≥0) (hw : ∑ i, w i = 1) (f : Ω → ℝ)
    (hf : ∀ i, MemLp f 2 (ν i)) (ha : ∀ i, (∫ ω, f ω ∂ν i) = (a i : ℝ)) :
    variance f (∑ i, w i • ν i) =
      (∑ i, (w i : ℝ)*variance f (ν i)) + rateVariance w a := by
  let := weighted_probability ν w hw
  have hm := finite_sum_memLp ν w f hf
  have hfi (i : I) := (hf i).integrable (by norm_num : (1 : ℝ≥0∞) ≤ 2)
  have hfs (i : I) := (hf i).integrable_sq
  have hv (i : I) : variance f (ν i) = (∫ ω, (f ω)^2 ∂ν i) - (a i : ℝ)^2 := by
    rw [variance_eq_sub (hf i), ha i]
    simp only [Pi.pow_apply]
  rw [variance_eq_sub hm]
  simp only [Pi.pow_apply]
  rw [
    integral_finsetSum_measure (fun i _ => (hfs i).smul_measure_nnreal),
    integral_finsetSum_measure (fun i _ => (hfi i).smul_measure_nnreal)]
  simp_rw [integral_smul_nnreal_measure, NNReal.smul_def, smul_eq_mul, ha,
    hv, rateVariance_eq w a hw, mul_sub, Finset.sum_sub_distrib]
  unfold rateMean
  ring

def count (ω : Fin 2 × ℕ) : ℝ := (((ω.1 : ℕ) + ω.2 : ℕ) : ℝ)

def factorialTwo (ω : Fin 2 × ℕ) : ℝ := count ω * (count ω - 1)

def secondMoment (p : ℝ) (w r : I → ℝ≥0) : ℝ :=
  ∑ i, (w i : ℝ)*((r i : ℝ)^2 + 2*p*r i)

private theorem component_facts (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0) :
    MemLp count 2 (component p hp0 hp1 r) ∧
    MemLp factorialTwo 2 (component p hp0 hp1 r) ∧
    (∫ ω, count ω ∂component p hp0 hp1 r) = p+r ∧
    (∫ ω, factorialTwo ω ∂component p hp0 hp1 r) = (r : ℝ)^2+2*p*r ∧
    variance count (component p hp0 hp1 r) = (r : ℝ)+p*(1-p) ∧
    variance factorialTwo (component p hp0 hp1 r) =
      4*(r : ℝ)^3+(12*p+2-4*p^2)*(r : ℝ)^2+4*p*r := by
  have := independentPairMeasure_isProbability 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) r
  obtain ⟨hX,hY,hXY⟩ := independentPairMeasure_hasLaws 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) r
  have h := BernoulliPoissonStatisticsV1.means_and_variances p hp0 hp1 r
    Prod.fst Prod.snd hX hY hXY
  exact ⟨BernoulliPoissonStatisticsV1.count_memLp p hp0 hp1 r
      Prod.fst Prod.snd hX hY hXY,
    BernoulliPoissonStatisticsV1.factorial_two_memLp p hp0 hp1 r
      Prod.fst Prod.snd hX hY hXY, h⟩

theorem count_memLp (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (w r : I → ℝ≥0) :
    MemLp count 2 (mixture p hp0 hp1 w r) :=
  finite_sum_memLp (fun i => component p hp0 hp1 (r i)) w count
    (fun i => (component_facts p hp0 hp1 (r i)).1)

theorem factorial_two_memLp (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) : MemLp factorialTwo 2 (mixture p hp0 hp1 w r) :=
  finite_sum_memLp (fun i => component p hp0 hp1 (r i)) w factorialTwo
    (fun i => (component_facts p hp0 hp1 (r i)).2.1)

theorem mixture_means (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) :
    (∫ ω, count ω ∂mixture p hp0 hp1 w r) = p+rateMean w r ∧
    (∫ ω, factorialTwo ω ∂mixture p hp0 hp1 w r) = secondMoment p w r := by
  constructor
  · exact mixture_mean p hp0 hp1 w r hw
  · simpa only [factorialTwo, count, secondMoment, Nat.cast_descFactorial_two,
      Nat.cast_one, one_add_one_eq_two, pow_one] using (mixture_factorial p hp0 hp1 w r 1).2

private theorem weighted_le (w : I → ℝ≥0) (hw : ∑ i, w i = 1)
    (f : I → ℝ) (C : ℝ) (hf : ∀ i, f i ≤ C) : ∑ i, (w i : ℝ)*f i ≤ C := by
  have hs := Finset.sum_le_sum (s := Finset.univ)
    (fun i _ => mul_le_mul_of_nonneg_left (hf i) (w i).coe_nonneg)
  have hwR : ∑ i, (w i : ℝ) = 1 := by exact_mod_cast hw
  simpa only [← Finset.sum_mul, hwR, one_mul] using hs

theorem count_variance_ceiling (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) (B : ℝ)
    (hrB : ∀ i, (r i : ℝ) ≤ B) :
    variance count (mixture p hp0 hp1 w r) ≤ B+1/4+B^2/4 := by
  let : ∀ i, IsProbabilityMeasure (component p hp0 hp1 (r i)) := fun i =>
    independentPairMeasure_isProbability 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1) (r i)
  let a : I → ℝ≥0 := fun i => ⟨p+r i, add_nonneg hp0 (r i).coe_nonneg⟩
  have hvar := finite_total_variance (fun i => component p hp0 hp1 (r i)) w a hw count
    (fun i => (component_facts p hp0 hp1 (r i)).1)
    (fun i => (component_facts p hp0 hp1 (r i)).2.2.1)
  have hwithin : (∑ i, (w i : ℝ)*variance count (component p hp0 hp1 (r i))) ≤ B+1/4 := by
    apply weighted_le w hw _ _
    intro i
    rw [(component_facts p hp0 hp1 (r i)).2.2.2.2.1]
    exact CountD1VarianceCoverage.first_variance_ceiling p (r i) B (hrB i)
  have hbetween := rateVariance_le_range w a hw p (p+B)
    (fun i => by change p ≤ p+(r i : ℝ); linarith [(r i).coe_nonneg])
    (fun i => by change p+(r i : ℝ) ≤ p+B; linarith [hrB i])
  change variance count (∑ i, w i • component p hp0 hp1 (r i)) ≤ _
  rw [hvar]
  nlinarith

theorem factorial_variance_ceiling (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) (B : ℝ) (_hB : 0 ≤ B)
    (hrB : ∀ i, (r i : ℝ) ≤ B) :
    variance factorialTwo (mixture p hp0 hp1 w r) ≤
      4*B^3+10*B^2+4*B+(B^2+2*B)^2/4 := by
  let : ∀ i, IsProbabilityMeasure (component p hp0 hp1 (r i)) := fun i =>
    independentPairMeasure_isProbability 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1) (r i)
  let a : I → ℝ≥0 := fun i => ⟨(r i : ℝ)^2+2*p*r i, by positivity⟩
  have hvar := finite_total_variance (fun i => component p hp0 hp1 (r i)) w a hw factorialTwo
    (fun i => (component_facts p hp0 hp1 (r i)).2.1)
    (fun i => (component_facts p hp0 hp1 (r i)).2.2.2.1)
  have hwithin : (∑ i, (w i : ℝ)*variance factorialTwo (component p hp0 hp1 (r i))) ≤
      4*B^3+10*B^2+4*B := by
    apply weighted_le w hw _ _
    intro i
    rw [(component_facts p hp0 hp1 (r i)).2.2.2.2.2]
    exact CountD1VarianceCoverage.second_variance_ceiling p (r i) B
      hp0 hp1 (r i).coe_nonneg (hrB i)
  have haB (i : I) : (a i : ℝ) ≤ B^2+2*B := by
    change (r i : ℝ)^2+2*p*(r i : ℝ) ≤ B^2+2*B
    have hsq := pow_le_pow_left₀ (r i).coe_nonneg (hrB i) 2
    have hp := mul_le_mul_of_nonneg_right hp1 (r i).coe_nonneg
    nlinarith [hrB i]
  have hbetween := rateVariance_le_range w a hw 0 (B^2+2*B)
    (fun i => (a i).coe_nonneg) haB
  change variance factorialTwo (∑ i, w i • component p hp0 hp1 (r i)) ≤ _
  rw [hvar]
  nlinarith

private theorem variance_comp_hasLaw {Ω : Type*} [MeasurableSpace Ω]
    {P : Measure Ω} {ν : Measure (Fin 2 × ℕ)} {W : Ω → Fin 2 × ℕ}
    (hW : HasLaw W ν P) (f : Fin 2 × ℕ → ℝ) :
    variance (fun ω => f (W ω)) P = variance f ν := by
  have hf : Measurable f := measurable_of_countable f
  have h := variance_map (X := f) (μ := P) (Y := W) hf.aemeasurable hW.aemeasurable
  rw [hW.map_eq] at h
  exact h.symm

open CountFiniteSampleMean

/-- Simultaneous sample-moment coverage for actual common finite-mixture laws.
Independence is unconditional pairwise independence of the observed counts. -/
theorem sample_means_coverage {Ω : Type*} [MeasurableSpace Ω]
    (P : Measure Ω) [IsProbabilityMeasure P] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (w r : I → ℝ≥0) (hw : ∑ i, w i = 1) (B : ℝ) (hB : 0 ≤ B)
    (hrB : ∀ i, (r i : ℝ) ≤ B) (W : Fin N → Ω → Fin 2 × ℕ)
    (hW : ∀ i, HasLaw (W i) (mixture p hp0 hp1 w r) P)
    (hI : Pairwise fun i j => IndepFun (fun ω => count (W i ω)) (fun ω => count (W j ω)) P)
    (hN : 0 < N) (α : ℝ) (hα : 0 < α) :
    P {ω | Real.sqrt (2*(B+1/4+B^2/4)/((N : ℝ)*α)) <
        |sampleMean (fun i ω => count (W i ω)) ω-(p+rateMean w r)| ∨
      Real.sqrt (2*(4*B^3+10*B^2+4*B+(B^2+2*B)^2/4)/((N : ℝ)*α)) <
        |sampleMean (fun i ω => factorialTwo (W i ω)) ω-secondMoment p w r|} ≤
      ENNReal.ofReal α := by
  have hc := count_memLp p hp0 hp1 w r
  have hf := factorial_two_memLp p hp0 hp1 w r
  have hm := mixture_means p hp0 hp1 w r hw
  have hm1 (i : Fin N) : (∫ ω, count (W i ω) ∂P) = p+rateMean w r := by
    exact ((hW i).integral_comp hc.aestronglyMeasurable).trans hm.1
  have hm2 (i : Fin N) : (∫ ω, factorialTwo (W i ω) ∂P) = secondMoment p w r := by
    exact ((hW i).integral_comp hf.aestronglyMeasurable).trans hm.2
  have hv1 (i : Fin N) : variance (fun ω => count (W i ω)) P ≤ B+1/4+B^2/4 := by
    rw [variance_comp_hasLaw (hW i) count]
    exact count_variance_ceiling p hp0 hp1 w r hw B hrB
  have hv2 (i : Fin N) : variance (fun ω => factorialTwo (W i ω)) P ≤
      4*B^3+10*B^2+4*B+(B^2+2*B)^2/4 := by
    rw [variance_comp_hasLaw (hW i) factorialTwo]
    exact factorial_variance_ceiling p hp0 hp1 w r hw B hB hrB
  exact CountConfidenceZeroAndTransforms.factorial_sample_means_coverage P
    (fun i ω => count (W i ω)) (fun i => (hW i).memLp_comp hc)
    (fun i => (hW i).memLp_comp hf) hN hI (p+rateMean w r) (secondMoment p w r)
    (B+1/4+B^2/4) (4*B^3+10*B^2+4*B+(B^2+2*B)^2/4) α hm1 hm2
    (by positivity) (by positivity) hα hv1 hv2

end CountFiniteMixedPoissonSampling
