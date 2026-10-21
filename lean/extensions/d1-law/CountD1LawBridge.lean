import CountSharpness
import CountD1Stability

/-!
The finite Bernoulli mass vector and its connection to D=1 stability.
The observed channel below remains the formal exponential-factor model.
No probability-space independence or finite-data guarantee is asserted.
-/

noncomputable section
open scoped BigOperators

namespace CountD1LawBridge

def bernoulliMass (p : ℝ) (n : ℕ) : ℝ :=
  if n = 0 then 1 - p else if n = 1 then p else 0

theorem truncatedExp_one (p : ℝ) :
    CountSharpness.truncatedExp 1 p =
      (1 : Polynomial ℝ) + Polynomial.C p * Polynomial.X := by
  ext n
  by_cases hn0 : n = 0
  · subst n
    simp [Polynomial.coeff_one, Polynomial.coeff_X]
  by_cases hn1 : n = 1
  · subst n
    simp [Polynomial.coeff_one]
  have hn : ¬ n ≤ 1 := by omega
  have hn1' : 1 ≠ n := Ne.symm hn1
  simp [CountSharpness.truncatedExp_coeff, Polynomial.coeff_one,
    Polynomial.coeff_X, hn, hn0, hn1']

theorem sharpLaw_one_eq_bernoulliMass (p : ℝ) :
    CountSharpness.sharpLaw 1 p = bernoulliMass p := by
  have hpoly : CountSharpness.ordinaryTrunc 1 p =
      (1 : Polynomial ℝ) + Polynomial.C p * (Polynomial.X - 1) := by
    simp [CountSharpness.ordinaryTrunc, truncatedExp_one,
      Polynomial.add_comp, Polynomial.mul_comp]
  funext n
  rw [CountSharpness.sharpLaw, hpoly]
  by_cases hn0 : n = 0
  · subst n
    simp [bernoulliMass, sub_eq_add_neg]
  by_cases hn1 : n = 1
  · subst n
    simp [bernoulliMass, Polynomial.coeff_one]
  have hn1' : 1 ≠ n := Ne.symm hn1
  simp [bernoulliMass, Polynomial.coeff_one, Polynomial.coeff_X, hn0, hn1, hn1']

theorem bernoulliMass_isBoundedLaw (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    BoundedCountLaw.IsBoundedLaw 1 (bernoulliMass p) := by
  refine ⟨?_, ?_, ?_⟩
  · intro n
    unfold bernoulliMass
    split_ifs <;> linarith
  · simp [bernoulliMass, Finset.sum_range_succ]
  · intro n hn
    have hn0 : n ≠ 0 := by omega
    have hn1 : n ≠ 1 := by omega
    simp [bernoulliMass, hn0, hn1]

theorem bernoulli_first_cumulant (p : ℝ) :
    BoundedCountLaw.lawFactorialCumulant 1 (bernoulliMass p) 1 = p := by
  rw [← sharpLaw_one_eq_bernoulliMass]
  exact CountSharpness.sharpLaw_first_cumulant 1 p (by omega)

theorem bernoulli_second_cumulant (p : ℝ) :
    BoundedCountLaw.lawFactorialCumulant 1 (bernoulliMass p) 2 =
      CountD1Stability.secondCumulant p := by
  rw [← sharpLaw_one_eq_bernoulliMass]
  exact CountSharpness.sharpLaw_top_cumulant 1 p (by omega)

theorem bernoulli_parameter_stability (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p - q| ≤ Real.sqrt
      |BoundedCountLaw.lawFactorialCumulant 1 (bernoulliMass p) 2 -
       BoundedCountLaw.lawFactorialCumulant 1 (bernoulliMass q) 2| := by
  rw [bernoulli_second_cumulant, bernoulli_second_cumulant]
  exact CountD1Stability.parameter_error_from_cumulant p q hp hq

theorem observed_bernoulli_cumulants (p b : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass p) b 1 = p + b ∧
    BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass p) b 2 =
      CountD1Stability.secondCumulant p := by
  have hp := bernoulliMass_isBoundedLaw p hp0 hp1
  constructor
  · rw [BoundedCountLaw.observed_first_cumulant_eq 1 _ b hp, bernoulli_first_cumulant]
  · rw [BoundedCountLaw.observed_higher_cumulant_eq 1 _ b 2 hp (by omega),
      bernoulli_second_cumulant]

theorem observed_bernoulli_stability (p q b c : ℝ)
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) :
    |p - q| ≤ Real.sqrt
      |BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass p) b 2 -
       BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass q) c 2| ∧
    |b - c| ≤
      |BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass p) b 1 -
       BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass q) c 1| +
      Real.sqrt
      |BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass p) b 2 -
       BoundedCountLaw.observedFactorialCumulant 1 (bernoulliMass q) c 2| := by
  obtain ⟨hpmean, hpcumulant⟩ := observed_bernoulli_cumulants p b hp0 hp1
  obtain ⟨hqmean, hqcumulant⟩ := observed_bernoulli_cumulants q c hq0 hq1
  rw [hpmean, hqmean, hpcumulant, hqcumulant]
  constructor
  · exact CountD1Stability.parameter_error_from_cumulant p q hp0 hq0
  · have h := CountD1Stability.background_error_le (p + b) (q + c) p q hp0 hq0
    simpa [CountD1Stability.backgroundFromMean] using h

end CountD1LawBridge

#print axioms CountD1LawBridge.sharpLaw_one_eq_bernoulliMass
#print axioms CountD1LawBridge.bernoulliMass_isBoundedLaw
#print axioms CountD1LawBridge.bernoulli_second_cumulant
#print axioms CountD1LawBridge.bernoulli_parameter_stability
#print axioms CountD1LawBridge.observed_bernoulli_cumulants
#print axioms CountD1LawBridge.observed_bernoulli_stability
