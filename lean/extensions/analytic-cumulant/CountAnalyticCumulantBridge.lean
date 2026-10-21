import CountTaylorJetProduct
import CountPoissonObservation
import CountObservedIdentification
import Mathlib.Analysis.Calculus.ContDiff.Polynomial
import Mathlib.Analysis.Calculus.Deriv.Polynomial
import Mathlib.Analysis.SpecialFunctions.Log.Deriv

noncomputable section
open scoped Topology BigOperators
open CountTaylorJetFoundation CountTaylorJetProduct

namespace CountAnalyticCumulantBridge

theorem polynomial_contDiff (P : Polynomial ℝ) (n : WithTop ℕ∞) :
    ContDiff ℝ n (fun x => P.eval x) := by
  simpa using P.contDiff_aeval (𝕜 := ℝ) n

theorem iteratedDeriv_polynomial (P : Polynomial ℝ) (n : ℕ) :
    iteratedDeriv n (fun x => P.eval x) =
      fun x => (Polynomial.derivative^[n] P).eval x := by
  induction n generalizing P with
  | zero => rfl
  | succ n ih =>
    rw [iteratedDeriv_succ']
    have hd : deriv (fun x => P.eval x) = fun x => P.derivative.eval x := by
      funext x
      exact P.deriv
    rw [hd, ih]
    rw [Function.iterate_succ_apply]

theorem jet0_polynomial (P : Polynomial ℝ) :
    jet0 (fun x => P.eval x) = (P : PowerSeries ℝ) := by
  ext n
  rw [coeff_jet0, iteratedDeriv_polynomial]
  simp only [← Polynomial.coeff_zero_eq_eval_zero, Polynomial.coeff_iterate_derivative,
    zero_add, Nat.descFactorial_self, nsmul_eq_mul, Polynomial.coeff_coe]
  have hn : (n.factorial : ℝ) ≠ 0 := by positivity
  field_simp

theorem jet0_log_polynomial (P : Polynomial ℝ) (hP : P.coeff 0 = 1) :
    jet0 (fun x => Real.log (P.eval x)) = PowerSeries.logOf (P : PowerSeries ℝ) := by
  have hp0 : P.eval 0 = 1 := by simpa only [← Polynomial.coeff_zero_eq_eval_zero] using hP
  have hs : ContDiffAt ℝ ⊤ (fun x => P.eval x) 0 := (polynomial_contDiff P ⊤).contDiffAt
  have hn0 : P.eval 0 ≠ 0 := by rw [hp0]; exact one_ne_zero
  have hl : ContDiffAt ℝ ⊤ (fun x => Real.log (P.eval x)) 0 := hs.log hn0
  have hld : ContDiffAt ℝ ⊤ (deriv (fun x => Real.log (P.eval x))) 0 :=
    hl.derivWithin (by simp)
  have hne : ∀ᶠ t in 𝓝 (0 : ℝ), P.eval t ≠ 0 := hs.continuousAt.eventually_ne hn0
  have heq : (fun t => deriv (fun x => Real.log (P.eval x)) t * P.eval t) =ᶠ[𝓝 0]
      (fun t => P.derivative.eval t) := by
    filter_upwards [hne] with t ht
    rw [((P.hasDerivAt t).log ht).deriv]
    exact div_mul_cancel₀ _ ht
  have hj := jet0_congr_eventuallyEq heq
  rw [jet0_mul hld hs, ← derivative_jet0, jet0_polynomial, jet0_polynomial] at hj
  have hc : PowerSeries.constantCoeff (P : PowerSeries ℝ) = 1 := by
    simpa only [Polynomial.constantCoeff_coe] using hP
  have hpne : (P : PowerSeries ℝ) ≠ 0 := by
    intro hzero
    have hz := congrArg (PowerSeries.constantCoeff (R := ℝ)) hzero
    rw [hc, map_zero] at hz
    exact one_ne_zero hz
  apply PowerSeries.derivative.ext
  · apply mul_right_cancel₀ hpne
    rw [CountSeriesCore.derivative_logOf_mul _ hc, hj]
    exact PowerSeries.derivative_coe P |>.symm
  · rw [PowerSeries.constantCoeff_logOf hc,
      ← PowerSeries.coeff_zero_eq_constantCoeff_apply, coeff_jet0]
    simp [hp0]

theorem factorialCumulant_polynomial_eq_iteratedDeriv_log
    (P : Polynomial ℝ) (hP : P.coeff 0 = 1) (n : ℕ) :
    CountSeriesCore.factorialCumulant (P : PowerSeries ℝ) n =
      iteratedDeriv n (fun x => Real.log (P.eval x)) 0 := by
  rw [CountSeriesCore.factorialCumulant, ← jet0_log_polynomial P hP, coeff_jet0]
  have hn : (n.factorial : ℝ) ≠ 0 := by positivity
  field_simp

theorem factorialCumulant_channel_eq_iteratedDeriv_log
    (P : Polynomial ℝ) (hP : P.coeff 0 = 1) (b : ℝ) (n : ℕ) :
    CountSeriesCore.factorialCumulant
        (CountPoissonChannel.channel (P : PowerSeries ℝ) b) n =
      iteratedDeriv n (fun x => Real.log (P.eval x * Real.exp (b * x))) 0 := by
  have hp0 : P.eval 0 = 1 := by simpa only [← Polynomial.coeff_zero_eq_eval_zero] using hP
  have hs : ContDiffAt ℝ ⊤ (fun x => P.eval x) 0 := (polynomial_contDiff P ⊤).contDiffAt
  have hn0 : P.eval 0 ≠ 0 := by rw [hp0]; exact one_ne_zero
  have hl : ContDiffAt ℝ ⊤ (fun x => Real.log (P.eval x)) 0 := hs.log hn0
  have hne : ∀ᶠ t in 𝓝 (0 : ℝ), P.eval t ≠ 0 := hs.continuousAt.eventually_ne hn0
  have heq : (fun t => Real.log (P.eval t * Real.exp (b * t))) =ᶠ[𝓝 0]
      (fun t => Real.log (P.eval t) + b * t) := by
    filter_upwards [hne] with t ht
    rw [Real.log_mul ht (Real.exp_ne_zero _), Real.log_exp]
  have hb : ContDiffAt ℝ n (fun t : ℝ => b * t) 0 :=
    contDiffAt_const.mul contDiffAt_id
  have hlinear : iteratedDeriv n (fun t : ℝ => b * t) 0 = if n = 1 then b else 0 := by
    rw [iteratedDeriv_const_mul_field, iteratedDeriv_fun_id_zero]
    split_ifs <;> simp
  have hc : PowerSeries.constantCoeff (P : PowerSeries ℝ) = 1 := by
    simpa only [Polynomial.constantCoeff_coe] using hP
  rw [heq.iteratedDeriv_eq n, iteratedDeriv_fun_add (hl.of_le le_top) hb,
    ← factorialCumulant_polynomial_eq_iteratedDeriv_log P hP n, hlinear]
  by_cases hn : n = 1
  · subst n
    simpa using CountPoissonChannel.first_factorialCumulant_channel (P : PowerSeries ℝ) b hc
  by_cases hz : n = 0
  · subst n
    simp [CountSeriesCore.factorialCumulant, PowerSeries.coeff_zero_eq_constantCoeff_apply,
      PowerSeries.constantCoeff_logOf hc,
      PowerSeries.constantCoeff_logOf (CountPoissonChannel.channel_constant _ b hc)]
  · rw [ite_eq_right hn, add_zero]
    exact CountPoissonChannel.higher_factorialCumulant_channel (P : PowerSeries ℝ) b n hc (by omega)

theorem lawFactorialCumulant_eq_iteratedDeriv_log
    (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) (n : ℕ) :
    BoundedCountLaw.lawFactorialCumulant D p n =
      iteratedDeriv n (fun t => Real.log ((BoundedCountLaw.factorialPGF D p).eval t)) 0 := by
  exact factorialCumulant_polynomial_eq_iteratedDeriv_log _
    (BoundedCountLaw.factorialPGF_constant D p hp.2.1) n

theorem observedFactorialCumulant_eq_iteratedDeriv_log
    (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) (b : ℝ) (n : ℕ) :
    BoundedCountLaw.observedFactorialCumulant D p b n =
      iteratedDeriv n (fun t => Real.log
        ((BoundedCountLaw.factorialPGF D p).eval t * Real.exp (b * t))) 0 := by
  exact factorialCumulant_channel_eq_iteratedDeriv_log _
    (BoundedCountLaw.factorialPGF_constant D p hp.2.1) b n

open MeasureTheory ProbabilityTheory

theorem lawFactorialCumulant_eq_iteratedDeriv_log_expectation
    (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) (n : ℕ) :
    BoundedCountLaw.lawFactorialCumulant D p n =
      iteratedDeriv n (fun t => Real.log (∫ x : Fin (D+1), (1+t)^(x : ℕ)
        ∂CountProbabilityBridge.boundedMeasure D p hp)) 0 := by
  rw [lawFactorialCumulant_eq_iteratedDeriv_log D p hp n]
  congr 1
  funext t
  rw [CountProbabilityBridge.factorialPGF_eval_eq_expectation D p hp]

theorem observedFactorialCumulant_eq_iteratedDeriv_log_expectation
    {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (b : NNReal) (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (CountProbabilityBridge.boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure b) μ) (hXY : IndepFun X Y μ) (n : ℕ) :
    BoundedCountLaw.observedFactorialCumulant D p (b : ℝ) n =
      iteratedDeriv n (fun t => Real.log (∫ ω, (1+t)^((X ω : ℕ) + Y ω) ∂μ)) 0 := by
  rw [observedFactorialCumulant_eq_iteratedDeriv_log D p hp (b : ℝ) n]
  apply Filter.EventuallyEq.iteratedDeriv_eq n
  have ht : ∀ᶠ t : ℝ in 𝓝 0, -1 < t := Ioi_mem_nhds (by norm_num)
  filter_upwards [ht] with t ht
  rw [CountPoissonObservation.observed_factorialPGF_integral D p hp b X Y hX hY hXY t ht]

theorem independentPairMeasure_cumulant_eq_iteratedDeriv_log_expectation
    (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) (b : NNReal) (n : ℕ) :
    BoundedCountLaw.observedFactorialCumulant D p (b : ℝ) n =
      iteratedDeriv n (fun t => Real.log (∫ ω : Fin (D+1) × ℕ, (1+t)^((ω.1 : ℕ) + ω.2)
        ∂CountPoissonObservation.independentPairMeasure D p hp b)) 0 := by
  have := CountPoissonObservation.independentPairMeasure_isProbability D p hp b
  obtain ⟨hX, hY, hXY⟩ := CountPoissonObservation.independentPairMeasure_hasLaws D p hp b
  exact observedFactorialCumulant_eq_iteratedDeriv_log_expectation D p hp b
    Prod.fst Prod.snd hX hY hXY n

section ObservedIdentification

variable {Ω₁ Ω₂ : Type*} [MeasurableSpace Ω₁] [MeasurableSpace Ω₂]
  {μ₁ : Measure Ω₁} {μ₂ : Measure Ω₂} [IsProbabilityMeasure μ₁] [IsProbabilityMeasure μ₂]
  (D : ℕ) (p q : ℕ → ℝ)
  (hp : BoundedCountLaw.IsBoundedLaw D p) (hq : BoundedCountLaw.IsBoundedLaw D q)
  (b₁ b₂ : NNReal) (X₁ : Ω₁ → Fin (D+1)) (Y₁ : Ω₁ → ℕ)
  (X₂ : Ω₂ → Fin (D+1)) (Y₂ : Ω₂ → ℕ)
  (hX₁ : HasLaw X₁ (CountProbabilityBridge.boundedMeasure D p hp) μ₁)
  (hY₁ : HasLaw Y₁ (poissonMeasure b₁) μ₁) (hXY₁ : IndepFun X₁ Y₁ μ₁)
  (hX₂ : HasLaw X₂ (CountProbabilityBridge.boundedMeasure D q hq) μ₂)
  (hY₂ : HasLaw Y₂ (poissonMeasure b₂) μ₂) (hXY₂ : IndepFun X₂ Y₂ μ₂)

include hp hq hX₁ hY₁ hXY₁ hX₂ hY₂ hXY₂

theorem observed_log_derivatives_identify_source
    (hc : ∀ n : ℕ, 2 ≤ n → n ≤ D+1 →
      iteratedDeriv n (fun t => Real.log (∫ ω, (1+t)^((X₁ ω : ℕ) + Y₁ ω) ∂μ₁)) 0 =
      iteratedDeriv n (fun t => Real.log (∫ ω, (1+t)^((X₂ ω : ℕ) + Y₂ ω) ∂μ₂)) 0) :
    p = q := by
  apply BoundedCountLaw.observed_higher_cumulants_identify_source D p q
    (b₁ : ℝ) (b₂ : ℝ) hp hq
  intro n hn hD
  rw [observedFactorialCumulant_eq_iteratedDeriv_log_expectation D p hp b₁ X₁ Y₁ hX₁ hY₁ hXY₁ n,
    observedFactorialCumulant_eq_iteratedDeriv_log_expectation D q hq b₂ X₂ Y₂ hX₂ hY₂ hXY₂ n]
  exact hc n hn hD

theorem observed_log_derivatives_identify_source_and_background
    (hc : ∀ n : ℕ, 1 ≤ n → n ≤ D+1 →
      iteratedDeriv n (fun t => Real.log (∫ ω, (1+t)^((X₁ ω : ℕ) + Y₁ ω) ∂μ₁)) 0 =
      iteratedDeriv n (fun t => Real.log (∫ ω, (1+t)^((X₂ ω : ℕ) + Y₂ ω) ∂μ₂)) 0) :
    p = q ∧ b₁ = b₂ := by
  have h := BoundedCountLaw.observed_cumulants_identify_source_and_background D p q
    (b₁ : ℝ) (b₂ : ℝ) hp hq (fun n hn hD => by
      rw [observedFactorialCumulant_eq_iteratedDeriv_log_expectation D p hp b₁ X₁ Y₁ hX₁ hY₁ hXY₁ n,
        observedFactorialCumulant_eq_iteratedDeriv_log_expectation D q hq b₂ X₂ Y₂ hX₂ hY₂ hXY₂ n]
      exact hc n hn hD)
  exact ⟨h.1, NNReal.coe_injective h.2⟩

end ObservedIdentification

end CountAnalyticCumulantBridge

#print axioms CountAnalyticCumulantBridge.polynomial_contDiff
#print axioms CountAnalyticCumulantBridge.iteratedDeriv_polynomial
#print axioms CountAnalyticCumulantBridge.jet0_polynomial
#print axioms CountAnalyticCumulantBridge.jet0_log_polynomial
#print axioms CountAnalyticCumulantBridge.factorialCumulant_polynomial_eq_iteratedDeriv_log
#print axioms CountAnalyticCumulantBridge.factorialCumulant_channel_eq_iteratedDeriv_log
#print axioms CountAnalyticCumulantBridge.lawFactorialCumulant_eq_iteratedDeriv_log
#print axioms CountAnalyticCumulantBridge.observedFactorialCumulant_eq_iteratedDeriv_log
#print axioms CountAnalyticCumulantBridge.lawFactorialCumulant_eq_iteratedDeriv_log_expectation
#print axioms CountAnalyticCumulantBridge.observedFactorialCumulant_eq_iteratedDeriv_log_expectation
#print axioms CountAnalyticCumulantBridge.independentPairMeasure_cumulant_eq_iteratedDeriv_log_expectation
#print axioms CountAnalyticCumulantBridge.observed_log_derivatives_identify_source
#print axioms CountAnalyticCumulantBridge.observed_log_derivatives_identify_source_and_background
