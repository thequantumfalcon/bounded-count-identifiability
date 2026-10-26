import CountLargestRoot

/-!
Exact admissibility (T05, Theorem 2). A normalized series `S` whose degree-`D+1` coefficient vanishes yields masses
`mass D S`, the coefficients of its degree-`D` truncation after `t = z - 1`. When those masses are nonnegative they
form a bounded law with the factorial cumulants of `S` through order `D+1` (sufficiency). Conversely, a bounded law
sharing the higher cumulants is recovered from `S` taken at the largest root (necessity and uniqueness).
-/

noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountAdmissibility

open CountSeriesCore CountLargestRoot

/-- A1: logarithm coefficients through order `n` depend only on coefficients through order `n`. -/
theorem logOf_coeff_congr (n : ℕ) (P S : PowerSeries ℝ) (hP0 : constantCoeff P = 1)
    (hS0 : constantCoeff S = 1) (h : ∀ i ≤ n, coeff i P = coeff i S) :
    ∀ i ≤ n, coeff i (logOf P) = coeff i (logOf S) := by
  have hP := derivative_logOf_mul P hP0
  have hS := derivative_logOf_mul S hS0
  have hd : ∀ k, k < n → coeff k (derivative (logOf P)) = coeff k (derivative (logOf S)) := by
    intro k
    induction k using Nat.strong_induction_on with
    | h k ih =>
      intro hk
      have e1 := congrArg (coeff k) hP
      have e2 := congrArg (coeff k) hS
      rw [coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk, Finset.sum_range_succ] at e1 e2
      simp only [Nat.sub_self, coeff_zero_eq_constantCoeff_apply, hP0, hS0, mul_one] at e1 e2
      have hrest : ∑ x ∈ Finset.range k, coeff x (derivative (logOf P)) * coeff (k - x) P =
          ∑ x ∈ Finset.range k, coeff x (derivative (logOf S)) * coeff (k - x) S := by
        refine Finset.sum_congr rfl fun x hx => ?_
        have hxk : x < k := Finset.mem_range.mp hx
        rw [ih x hxk (by omega), h (k - x) (by omega)]
      have hdP : coeff k (derivative P) = coeff k (derivative S) := by
        rw [coeff_derivative, coeff_derivative, h (k + 1) (by omega)]
      linarith
  intro i hi
  cases i with
  | zero =>
    rw [coeff_zero_eq_constantCoeff_apply, coeff_zero_eq_constantCoeff_apply,
      constantCoeff_logOf hP0, constantCoeff_logOf hS0]
  | succ j =>
    have hj := hd j (by omega)
    rw [coeff_derivative, coeff_derivative] at hj
    have hnz : (j : ℝ) + 1 ≠ 0 := by positivity
    exact mul_right_cancel₀ hnz hj

/-- The reconstructed masses: coefficients of the degree-`D` truncation after substituting `t = z - 1`. -/
def mass (D : ℕ) (S : PowerSeries ℝ) (j : ℕ) : ℝ :=
  ((PowerSeries.trunc (D + 1) S).comp (Polynomial.X - 1)).coeff j

theorem natDegree_shifted_le (D : ℕ) (S : PowerSeries ℝ) :
    ((PowerSeries.trunc (D + 1) S).comp (Polynomial.X - 1)).natDegree ≤ D := by
  have h1 : (PowerSeries.trunc (D + 1) S).natDegree ≤ D :=
    Nat.lt_succ_iff.mp (PowerSeries.natDegree_trunc_lt S D)
  calc ((PowerSeries.trunc (D + 1) S).comp (Polynomial.X - 1)).natDegree
      ≤ (PowerSeries.trunc (D + 1) S).natDegree * (Polynomial.X - 1 : Polynomial ℝ).natDegree :=
        Polynomial.natDegree_comp_le
    _ ≤ D := by
        rw [show (Polynomial.X - 1 : Polynomial ℝ) = Polynomial.X - Polynomial.C 1 by simp,
          Polynomial.natDegree_X_sub_C, mul_one]
        exact h1

theorem factorialPGF_mass (D : ℕ) (S : PowerSeries ℝ) :
    BoundedCountLaw.factorialPGF D (mass D S) = PowerSeries.trunc (D + 1) S := by
  set T := PowerSeries.trunc (D + 1) S with hT
  have hord : BoundedCountLaw.ordinaryPGF D (mass D S) = T.comp (Polynomial.X - 1) := by
    rw [BoundedCountLaw.ordinaryPGF]
    conv_rhs => rw [Polynomial.as_sum_range' (T.comp (Polynomial.X - 1)) (D + 1)
      (Nat.lt_succ_of_le (natDegree_shifted_le D S))]
    refine Finset.sum_congr rfl fun n _ => ?_
    rw [mass, ← hT, Polynomial.C_mul_X_pow_eq_monomial]
  have hshift : (Polynomial.X - 1 : Polynomial ℝ).comp (Polynomial.X + 1) = Polynomial.X := by
    simp
  have hu := congrArg (fun F : Polynomial ℝ => F.comp (Polynomial.X + 1))
    (BoundedCountLaw.factorialPGF_unshift D (mass D S))
  simp only [Polynomial.comp_assoc, hshift, Polynomial.comp_X] at hu
  rw [hu, hord, Polynomial.comp_assoc, hshift, Polynomial.comp_X]

/-- A2: nonnegative reconstructed masses give a bounded law with the cumulants of `S` (sufficiency). -/
theorem admissible_of_nonneg_masses (D : ℕ) (S : PowerSeries ℝ) (hS0 : constantCoeff S = 1)
    (htop : coeff (D + 1) S = 0) (hmass : ∀ j ≤ D, 0 ≤ mass D S j) :
    BoundedCountLaw.IsBoundedLaw D (mass D S) ∧
      ∀ r ≤ D + 1, BoundedCountLaw.lawFactorialCumulant D (mass D S) r = factorialCumulant S r := by
  have hfac := factorialPGF_mass D S
  have habove : ∀ n, D < n → mass D S n = 0 := fun n hn =>
    Polynomial.coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt (natDegree_shifted_le D S) hn)
  have hT0 : (PowerSeries.trunc (D + 1) S).coeff 0 = 1 := by
    rw [PowerSeries.coeff_trunc, ite_eq_left (by omega), coeff_zero_eq_constantCoeff_apply, hS0]
  refine ⟨⟨fun n => ?_, ?_, habove⟩, fun r hr => ?_⟩
  · by_cases hn : n ≤ D
    · exact hmass n hn
    · rw [habove n (by omega)]
  · have h0 := BoundedCountLaw.factorialPGF_coeff D 0 (mass D S)
    rw [hfac, hT0] at h0
    simpa using h0.symm
  · unfold BoundedCountLaw.lawFactorialCumulant factorialCumulant
    rw [hfac]
    have hagree : ∀ i ≤ D + 1, coeff i ((PowerSeries.trunc (D + 1) S : Polynomial ℝ) : PowerSeries ℝ) =
        coeff i S := by
      intro i hi
      rw [Polynomial.coeff_coe, PowerSeries.coeff_trunc]
      by_cases hlt : i < D + 1
      · rw [ite_eq_left hlt]
      · rw [ite_eq_right hlt, show i = D + 1 by omega, htop]
    have hc0 : constantCoeff ((PowerSeries.trunc (D + 1) S : Polynomial ℝ) : PowerSeries ℝ) = 1 := by
      rw [← coeff_zero_eq_constantCoeff_apply, hagree 0 (by omega), coeff_zero_eq_constantCoeff_apply, hS0]
    rw [logOf_coeff_congr (D + 1) _ S hc0 hS0 hagree r hr]

/-- A3: at the largest root the masses are the admissible law (necessity and uniqueness). -/
theorem mass_eq_of_admissible (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (S : PowerSeries ℝ) (hS0 : constantCoeff S = 1) (htop : coeff (D + 1) S = 0)
    (hlog : ∀ r, 2 ≤ r → r ≤ D + 1 →
      coeff r (logOf S) = coeff r (logOf (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ)))
    (hρ : coeff 1 (logOf (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ)) ≤ coeff 1 (logOf S)) :
    ∀ j ≤ D, mass D S j = p j := by
  set Q : PowerSeries ℝ := (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ) with hQdef
  have hQ0 : constantCoeff Q = 1 := by
    simpa only [hQdef, Polynomial.constantCoeff_coe] using
      BoundedCountLaw.factorialPGF_constant D p hp.2.1
  have hQ : ∀ j, 0 ≤ coeff j Q := by
    intro j
    simpa only [hQdef, Polynomial.coeff_coe] using
      BoundedCountLaw.factorialPGF_coeff_nonneg D j p (fun k _ => hp.1 k)
  have hQtop : coeff (D + 1) Q = 0 := by
    simpa only [hQdef, Polynomial.coeff_coe] using
      BoundedCountLaw.factorialPGF_coeff_above D (D + 1) p (by omega)
  have hroot : topCoeff D Q (coeff 1 (logOf S)) = 0 := by
    rw [← top_coeff_of_matching_cumulants D Q S hQ0 hS0 hlog, htop]
  have hle := (mean_is_largest_root D Q hQ0 hQ hQtop).2 _ hroot
  have heq : coeff 1 (logOf S) - coeff 1 (logOf Q) = 0 := by linarith
  have hjet := tilt_jet_of_log_coefficients D S Q hS0 hQ0 hlog
  rw [heq, expShift_zero, mul_one] at hjet
  have hpoly : PowerSeries.trunc (D + 1) S = BoundedCountLaw.factorialPGF D p := by
    ext n
    rw [PowerSeries.coeff_trunc]
    by_cases hn : n < D + 1
    · rw [ite_eq_left hn, hjet n (by omega), hQdef, Polynomial.coeff_coe]
    · rw [ite_eq_right hn, BoundedCountLaw.factorialPGF_coeff_above D n p (by omega)]
  intro j hj
  rw [mass, hpoly, BoundedCountLaw.factorialPGF_unshift, BoundedCountLaw.ordinaryPGF_coeff D j p hj]

end CountAdmissibility

#print axioms CountAdmissibility.logOf_coeff_congr
#print axioms CountAdmissibility.admissible_of_nonneg_masses
#print axioms CountAdmissibility.mass_eq_of_admissible
