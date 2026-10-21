import CountIdentification
import CountPoissonChannel
import CountObservedIdentification
import Mathlib.Algebra.Polynomial.Degree.Lemmas

/-!
Sharpness for the bounded-count cumulant cutoff, using the classical
truncated-exponential/generalized-matching (quasi-Poisson) family.
No originality claim is made for this family or its matched moments.
Existing verified theorem files are imported without modification.
-/

noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountSharpness
open CountSeriesCore

def truncatedExp (D : ℕ) (h : ℝ) : Polynomial ℝ :=
  PowerSeries.trunc (D + 1) (expShift h)

@[simp] theorem truncatedExp_coeff (D n : ℕ) (h : ℝ) :
    (truncatedExp D h).coeff n =
      if n ≤ D then h ^ n / (Nat.factorial n : ℝ) else 0 := by
  simp [truncatedExp, PowerSeries.coeff_trunc]

@[simp] theorem truncatedExp_series_coeff (D n : ℕ) (h : ℝ) :
    coeff n (truncatedExp D h : PowerSeries ℝ) =
      if n ≤ D then h ^ n / (Nat.factorial n : ℝ) else 0 := by
  rw [Polynomial.coeff_coe, truncatedExp_coeff]

@[simp] theorem truncatedExp_constant (D : ℕ) (h : ℝ) :
    constantCoeff (truncatedExp D h : PowerSeries ℝ) = 1 := by
  rw [← coeff_zero_eq_constantCoeff_apply]
  simp

theorem truncatedExp_derivative_defect (D : ℕ) (h : ℝ) :
    derivative (truncatedExp D h : PowerSeries ℝ) =
      C h * (truncatedExp D h : PowerSeries ℝ) -
        C (h ^ (D + 1) / (Nat.factorial D : ℝ)) * X ^ D := by
  ext n
  rw [coeff_derivative, map_sub, coeff_C_mul, coeff_C_mul_X_pow]
  by_cases hlt : n < D
  · have hnext : n + 1 ≤ D := by omega
    have hle : n ≤ D := by omega
    have hne : n ≠ D := by omega
    simp only [truncatedExp_series_coeff, ite_eq_left hnext, ite_eq_left hle,
      ite_eq_right hne, sub_zero]
    have he := congrArg (coeff n) (derivative_expShift h)
    simpa only [coeff_derivative, coeff_C_mul, coeff_expShift] using he
  · by_cases heq : n = D
    · subst n
      simp [pow_succ]
      ring
    · have hn : ¬ n ≤ D := by omega
      have hn' : ¬ n + 1 ≤ D := by omega
      simp [hn, hn', heq]

theorem truncatedExp_log_derivative (D : ℕ) (h : ℝ) :
    derivative (logOf (truncatedExp D h : PowerSeries ℝ)) =
      C h - C (h ^ (D + 1) / (Nat.factorial D : ℝ)) *
        ((truncatedExp D h : PowerSeries ℝ)⁻¹ * X ^ D) := by
  let P : PowerSeries ℝ := truncatedExp D h
  have hP0 : constantCoeff P = 1 := truncatedExp_constant D h
  have hinv : P * P⁻¹ = 1 := PowerSeries.mul_inv_cancel P (by rw [hP0]; exact one_ne_zero)
  calc
    derivative (logOf P) = (derivative (logOf P) * P) * P⁻¹ := by
      rw [mul_assoc, hinv, mul_one]
    _ = derivative P * P⁻¹ := by rw [derivative_logOf_mul P hP0]
    _ = C h - C (h ^ (D + 1) / (Nat.factorial D : ℝ)) * (P⁻¹ * X ^ D) := by
      change derivative (truncatedExp D h : PowerSeries ℝ) * P⁻¹ = _
      rw [truncatedExp_derivative_defect]
      change (C h * P - C (h ^ (D + 1) / (Nat.factorial D : ℝ)) * X ^ D) * P⁻¹ = _
      calc
        _ = C h * (P * P⁻¹) - C (h ^ (D + 1) / (Nat.factorial D : ℝ)) *
            (P⁻¹ * X ^ D) := by ring
        _ = _ := by rw [hinv, mul_one]

theorem truncatedExp_higher_cumulants_zero (D r : ℕ) (h : ℝ)
    (hr : 2 ≤ r) (hrD : r ≤ D) :
    factorialCumulant (truncatedExp D h : PowerSeries ℝ) r = 0 := by
  cases r with
  | zero => omega
  | succ n =>
    have hn : n ≠ 0 := by omega
    have hnD : ¬ D ≤ n := by omega
    have hc := congrArg (coeff n) (truncatedExp_log_derivative D h)
    rw [coeff_derivative, map_sub, coeff_C_of_ne_zero hn, coeff_C_mul,
      coeff_mul_X_pow', ite_eq_right hnD] at hc
    simp only [mul_zero, sub_zero] at hc
    have he := (mul_eq_zero.mp hc).resolve_right (by positivity : (n : ℝ) + 1 ≠ 0)
    unfold factorialCumulant
    rw [he, mul_zero]

theorem truncatedExp_top_cumulant (D : ℕ) (h : ℝ) (hD : 1 ≤ D) :
    factorialCumulant (truncatedExp D h : PowerSeries ℝ) (D + 1) = -h ^ (D + 1) := by
  have hDne : D ≠ 0 := by omega
  have hc := congrArg (coeff D) (truncatedExp_log_derivative D h)
  rw [coeff_derivative, map_sub, coeff_C_of_ne_zero hDne, coeff_C_mul,
    coeff_mul_X_pow', ite_eq_left (le_refl D), Nat.sub_self,
    coeff_zero_eq_constantCoeff_apply, constantCoeff_inv, truncatedExp_constant] at hc
  simp only [inv_one, mul_one, zero_sub] at hc
  unfold factorialCumulant
  rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  calc
    _ = (Nat.factorial D : ℝ) *
      (coeff (D + 1) (logOf (truncatedExp D h : PowerSeries ℝ)) * ((D : ℝ) + 1)) := by ring
    _ = (Nat.factorial D : ℝ) * (-(h ^ (D + 1) / (Nat.factorial D : ℝ))) := by rw [hc]
    _ = -h ^ (D + 1) := by
      have hf : (Nat.factorial D : ℝ) ≠ 0 := by positivity
      field_simp

theorem truncatedExp_first_cumulant (D : ℕ) (h : ℝ) (hD : 1 ≤ D) :
    factorialCumulant (truncatedExp D h : PowerSeries ℝ) 1 = h := by
  unfold factorialCumulant
  rw [coeff_one_logOf _ (truncatedExp_constant D h)]
  simp [hD]

def alternatingExpSum (n : ℕ) (h : ℝ) : ℝ :=
  ∑ k ∈ Finset.range (n + 1), (-h) ^ k / (Nat.factorial k : ℝ)

theorem alternatingExpSum_succ (n : ℕ) (h : ℝ) :
    alternatingExpSum (n + 1) h = alternatingExpSum n h +
      (-h) ^ (n + 1) / (Nat.factorial (n + 1) : ℝ) := by
  simp only [alternatingExpSum, Finset.sum_range_succ]

theorem neg_even_power (h : ℝ) (k : ℕ) : (-h) ^ (2 * k) = h ^ (2 * k) := by
  rw [pow_mul, pow_mul]
  simp

theorem alternating_pair_pos (k : ℕ) (h : ℝ) (hh0 : 0 < h) (hh1 : h < 1) :
    0 < (-h) ^ (2*k) / (Nat.factorial (2*k) : ℝ) +
      (-h) ^ (2*k+1) / (Nat.factorial (2*k+1) : ℝ) := by
  have hodd : (-h) ^ (2*k+1) = -(h ^ (2*k+1)) := by
    rw [pow_succ, neg_even_power, pow_succ]
    ring
  rw [neg_even_power, hodd]
  have hlt : h ^ (2*k+1) / (Nat.factorial (2*k+1) : ℝ) <
      h ^ (2*k) / (Nat.factorial (2*k) : ℝ) := by
    apply (div_lt_div_iff₀ (by positivity) (by positivity)).mpr
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, pow_succ]
    have hnat : (0 : ℝ) ≤ (2*k : ℕ) := by positivity
    have hsmall : h < ((2*k : ℕ) : ℝ) + 1 := by linarith
    have hpos : 0 < h ^ (2*k) * (Nat.factorial (2*k) : ℝ) := by positivity
    have hm := mul_lt_mul_of_pos_left hsmall hpos
    nlinarith
  simpa only [neg_div, ← sub_eq_add_neg] using sub_pos.mpr hlt

theorem alternatingExpSum_odd_pos (k : ℕ) (h : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) : 0 < alternatingExpSum (2*k+1) h := by
  induction k with
  | zero =>
    simp [alternatingExpSum, Finset.sum_range_succ]
    exact hh1
  | succ k ih =>
    have hstep : alternatingExpSum (2*(k+1)+1) h =
        alternatingExpSum (2*k+1) h +
        ((-h) ^ (2*(k+1)) / (Nat.factorial (2*(k+1)) : ℝ) +
          (-h) ^ (2*(k+1)+1) / (Nat.factorial (2*(k+1)+1) : ℝ)) := by
      rw [show 2*(k+1)+1 = (2*k+1)+1+1 by omega,
        alternatingExpSum_succ, alternatingExpSum_succ]
      rw [show 2*k+1+1 = 2*(k+1) by omega]
      ring
    rw [hstep]
    exact add_pos ih (alternating_pair_pos (k+1) h hh0 hh1)

theorem alternatingExpSum_even_pos (k : ℕ) (h : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) : 0 < alternatingExpSum (2*k) h := by
  cases k with
  | zero => simp [alternatingExpSum]
  | succ k =>
    rw [show 2*(k+1) = (2*k+1)+1 by omega, alternatingExpSum_succ]
    apply add_pos (alternatingExpSum_odd_pos k h hh0 hh1)
    rw [show 2*k+1+1 = 2*(k+1) by omega, neg_even_power]
    positivity

theorem alternatingExpSum_pos (n : ℕ) (h : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) : 0 < alternatingExpSum n h := by
  have hn : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega
  rcases hn with he | ho
  · rw [he]
    exact alternatingExpSum_even_pos _ h hh0 hh1
  · rw [ho]
    exact alternatingExpSum_odd_pos _ h hh0 hh1

theorem truncatedExp_eval_neg_one (D : ℕ) (h : ℝ) :
    (truncatedExp D h).eval (-1) = alternatingExpSum D h := by
  change (PowerSeries.trunc (D+1) (expShift h)).eval₂ (RingHom.id ℝ) (-1) = _
  rw [eval₂_trunc_eq_sum_range]
  unfold alternatingExpSum
  apply Finset.sum_congr rfl
  intro i hi
  simp only [RingHom.id_apply, coeff_expShift]
  rw [neg_pow h i]
  ring

theorem truncatedExp_polynomial_derivative_succ (D : ℕ) (h : ℝ) :
    (truncatedExp (D+1) h).derivative = Polynomial.C h * truncatedExp D h := by
  ext n
  rw [Polynomial.coeff_derivative, Polynomial.coeff_C_mul,
      truncatedExp_coeff, truncatedExp_coeff]
  by_cases hn : n ≤ D
  · have hn' : n+1 ≤ D+1 := by omega
    rw [ite_eq_left hn, ite_eq_left hn']
    have he := congrArg (coeff n) (derivative_expShift h)
    simpa only [coeff_derivative, coeff_C_mul, coeff_expShift] using he
  · have hn' : ¬ n+1 ≤ D+1 := by omega
    simp [hn, hn']

def ordinaryTrunc (D : ℕ) (h : ℝ) : Polynomial ℝ :=
  (truncatedExp D h).comp (Polynomial.X - 1)

def sharpLaw (D : ℕ) (h : ℝ) (n : ℕ) : ℝ :=
  (ordinaryTrunc D h).coeff n

theorem ordinaryTrunc_coeff_zero (D : ℕ) (h : ℝ) :
    (ordinaryTrunc D h).coeff 0 = alternatingExpSum D h := by
  rw [Polynomial.coeff_zero_eq_eval_zero, ordinaryTrunc, Polynomial.eval_comp]
  simpa using truncatedExp_eval_neg_one D h

theorem ordinaryTrunc_derivative_succ (D : ℕ) (h : ℝ) :
    (ordinaryTrunc (D+1) h).derivative = Polynomial.C h * ordinaryTrunc D h := by
  unfold ordinaryTrunc
  rw [Polynomial.derivative_comp, truncatedExp_polynomial_derivative_succ]
  simp [Polynomial.mul_comp]

theorem ordinaryTrunc_coeff_pos (D : ℕ) (h : ℝ) (hh0 : 0 < h) (hh1 : h < 1) :
    ∀ j ≤ D, 0 < (ordinaryTrunc D h).coeff j := by
  induction D with
  | zero =>
    intro j hj
    have hj0 : j = 0 := by omega
    rw [hj0, ordinaryTrunc_coeff_zero]
    exact alternatingExpSum_pos 0 h hh0 hh1
  | succ D ih =>
    intro j hj
    cases j with
    | zero =>
      rw [ordinaryTrunc_coeff_zero]
      exact alternatingExpSum_pos _ h hh0 hh1
    | succ j =>
      have he := congrArg (fun P : Polynomial ℝ => P.coeff j)
        (ordinaryTrunc_derivative_succ D h)
      rw [Polynomial.coeff_derivative, Polynomial.coeff_C_mul] at he
      have hp : 0 < h * (ordinaryTrunc D h).coeff j := mul_pos hh0 (ih j (by omega))
      rw [← he] at hp
      exact (mul_pos_iff_of_pos_right (by positivity : (j : ℝ) + 1 > 0)).mp hp

theorem ordinaryTrunc_degree_bound (D : ℕ) (h : ℝ) :
    (ordinaryTrunc D h).natDegree ≤ D := by
  have hX : (Polynomial.X - (1 : Polynomial ℝ)).natDegree = 1 := by
    simpa using Polynomial.natDegree_X_sub_C (1 : ℝ)
  have hdeg := Polynomial.natDegree_comp_le (p := truncatedExp D h)
    (q := Polynomial.X - 1)
  rw [hX, mul_one] at hdeg
  exact hdeg.trans (Nat.le_of_lt_succ (PowerSeries.natDegree_trunc_lt (expShift h) D))

theorem sharpLaw_above (D n : ℕ) (h : ℝ) (hn : D < n) : sharpLaw D h n = 0 := by
  apply Polynomial.coeff_eq_zero_of_natDegree_lt
  exact lt_of_le_of_lt (ordinaryTrunc_degree_bound D h) hn

theorem ordinaryTrunc_eval_one (D : ℕ) (h : ℝ) :
    (ordinaryTrunc D h).eval 1 = 1 := by
  simp [ordinaryTrunc, Polynomial.eval_comp, ← Polynomial.coeff_zero_eq_eval_zero]

theorem sharpLaw_isBoundedLaw (D : ℕ) (h : ℝ) (hh0 : 0 < h) (hh1 : h < 1) :
    BoundedCountLaw.IsBoundedLaw D (sharpLaw D h) := by
  refine ⟨?_, ?_, ?_⟩
  · intro n
    by_cases hn : n ≤ D
    · exact le_of_lt (ordinaryTrunc_coeff_pos D h hh0 hh1 n hn)
    · rw [sharpLaw_above D n h (by omega)]
  · have he := Polynomial.eval_eq_sum_range' (p := ordinaryTrunc D h)
      (Nat.lt_succ_of_le (ordinaryTrunc_degree_bound D h)) (1 : ℝ)
    simp only [one_pow, mul_one] at he
    rw [ordinaryTrunc_eval_one] at he
    exact he.symm
  · intro n hn
    exact sharpLaw_above D n h hn

theorem sharpLaw_ordinaryPGF (D : ℕ) (h : ℝ) :
    BoundedCountLaw.ordinaryPGF D (sharpLaw D h) = ordinaryTrunc D h := by
  exact ((ordinaryTrunc D h).as_sum_range_C_mul_X_pow'
    (Nat.lt_succ_of_le (ordinaryTrunc_degree_bound D h))).symm

theorem sharpLaw_factorialPGF (D : ℕ) (h : ℝ) :
    BoundedCountLaw.factorialPGF D (sharpLaw D h) = truncatedExp D h := by
  have hu := BoundedCountLaw.factorialPGF_unshift D (sharpLaw D h)
  rw [sharpLaw_ordinaryPGF] at hu
  have he := congrArg (fun P : Polynomial ℝ => P.comp (1 + Polynomial.X)) hu
  simpa [ordinaryTrunc, Polynomial.comp_assoc] using he

theorem sharpLaw_first_cumulant (D : ℕ) (h : ℝ) (hD : 1 ≤ D) :
    BoundedCountLaw.lawFactorialCumulant D (sharpLaw D h) 1 = h := by
  unfold BoundedCountLaw.lawFactorialCumulant
  rw [sharpLaw_factorialPGF]
  exact truncatedExp_first_cumulant D h hD

theorem sharpLaw_higher_cumulants_zero (D r : ℕ) (h : ℝ) (hr : 2 ≤ r) (hrD : r ≤ D) :
    BoundedCountLaw.lawFactorialCumulant D (sharpLaw D h) r = 0 := by
  unfold BoundedCountLaw.lawFactorialCumulant
  rw [sharpLaw_factorialPGF]
  exact truncatedExp_higher_cumulants_zero D r h hr hrD

theorem sharpLaw_top_cumulant (D : ℕ) (h : ℝ) (hD : 1 ≤ D) :
    BoundedCountLaw.lawFactorialCumulant D (sharpLaw D h) (D+1) = -h^(D+1) := by
  unfold BoundedCountLaw.lawFactorialCumulant
  rw [sharpLaw_factorialPGF]
  exact truncatedExp_top_cumulant D h hD

theorem sharpLaw_positive (D : ℕ) (h : ℝ) (hh0 : 0 < h) (hh1 : h < 1) :
    ∀ n ≤ D, 0 < sharpLaw D h n := ordinaryTrunc_coeff_pos D h hh0 hh1

def zeroLaw (n : ℕ) : ℝ := if n = 0 then 1 else 0

theorem zeroLaw_isBoundedLaw (D : ℕ) : BoundedCountLaw.IsBoundedLaw D zeroLaw := by
  refine ⟨?_, ?_, ?_⟩
  · intro n
    simp only [zeroLaw]
    split_ifs <;> norm_num
  · simp [zeroLaw]
  · intro n hn
    have hn0 : n ≠ 0 := by omega
    simp [zeroLaw, hn0]

theorem zeroLaw_factorialPGF (D : ℕ) : BoundedCountLaw.factorialPGF D zeroLaw = 1 := by
  simp [BoundedCountLaw.factorialPGF, zeroLaw]

theorem zeroLaw_cumulant (D r : ℕ) : BoundedCountLaw.lawFactorialCumulant D zeroLaw r = 0 := by
  have hl : logOf (1 : PowerSeries ℝ) = 0 := by
    rw [logOf_eq, sub_self]
    exact subst_zero_of_constantCoeff_zero constantCoeff_log
  simp [BoundedCountLaw.lawFactorialCumulant, zeroLaw_factorialPGF,
    factorialCumulant, hl]

theorem sharpLaw_ne_zeroLaw (D : ℕ) (h : ℝ) (hD : 1 ≤ D) (hh0 : 0 < h) :
    sharpLaw D h ≠ zeroLaw := by
  intro heq
  have hc := congrArg (fun p => BoundedCountLaw.lawFactorialCumulant D p 1) heq
  rw [sharpLaw_first_cumulant D h hD, zeroLaw_cumulant] at hc
  exact (ne_of_gt hh0) hc

theorem cutoff_is_sharp (D : ℕ) (hD : 1 ≤ D) :
    ∃ p q : ℕ → ℝ,
      BoundedCountLaw.IsBoundedLaw D p ∧ BoundedCountLaw.IsBoundedLaw D q ∧ p ≠ q ∧
      ∀ r, 2 ≤ r → r ≤ D →
        BoundedCountLaw.lawFactorialCumulant D p r =
          BoundedCountLaw.lawFactorialCumulant D q r := by
  refine ⟨sharpLaw D (1/2), zeroLaw,
    sharpLaw_isBoundedLaw D (1/2) (by norm_num) (by norm_num),
    zeroLaw_isBoundedLaw D,
    sharpLaw_ne_zeroLaw D (1/2) hD (by norm_num), ?_⟩
  intro r hr hrd
  rw [sharpLaw_higher_cumulants_zero D r (1/2) hr hrd, zeroLaw_cumulant]

theorem lower_observed_cumulants_match (D : ℕ) (h : ℝ)
    (hD : 1 ≤ D) (hh0 : 0 < h) (hh1 : h < 1)
    (r : ℕ) (hr1 : 1 ≤ r) (hrD : r ≤ D) :
    BoundedCountLaw.observedFactorialCumulant D (sharpLaw D h) 0 r =
      BoundedCountLaw.observedFactorialCumulant D zeroLaw h r := by
  by_cases hr : r = 1
  · subst r
    rw [BoundedCountLaw.observed_first_cumulant_eq D (sharpLaw D h) 0
        (sharpLaw_isBoundedLaw D h hh0 hh1),
      BoundedCountLaw.observed_first_cumulant_eq D zeroLaw h (zeroLaw_isBoundedLaw D),
      sharpLaw_first_cumulant D h hD, zeroLaw_cumulant]
    ring
  · have hr2 : 2 ≤ r := by omega
    rw [BoundedCountLaw.observed_higher_cumulant_eq D (sharpLaw D h) 0 r
        (sharpLaw_isBoundedLaw D h hh0 hh1) hr2,
      BoundedCountLaw.observed_higher_cumulant_eq D zeroLaw h r (zeroLaw_isBoundedLaw D) hr2,
      sharpLaw_higher_cumulants_zero D r h hr2 hrD, zeroLaw_cumulant]

#print axioms truncatedExp_higher_cumulants_zero
#print axioms truncatedExp_top_cumulant
#print axioms alternatingExpSum_pos
#print axioms sharpLaw_isBoundedLaw
#print axioms sharpLaw_higher_cumulants_zero
#print axioms sharpLaw_top_cumulant
#print axioms cutoff_is_sharp
#print axioms lower_observed_cumulants_match

end CountSharpness
