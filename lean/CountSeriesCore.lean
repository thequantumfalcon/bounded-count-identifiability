import Mathlib.RingTheory.PowerSeries.Log
import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountSeriesCore

def factorialCumulant (P : PowerSeries ℝ) (r : ℕ) : ℝ :=
  (Nat.factorial r : ℝ) * coeff r (logOf P)

def expShift (c : ℝ) : PowerSeries ℝ :=
  PowerSeries.mk fun n => c ^ n / (Nat.factorial n : ℝ)

@[simp] theorem coeff_expShift (c : ℝ) (n : ℕ) :
    coeff n (expShift c) = c ^ n / (Nat.factorial n : ℝ) := by
  simp [expShift]

@[simp] theorem constantCoeff_expShift (c : ℝ) :
    constantCoeff (expShift c) = 1 := by
  rw [← coeff_zero_eq_constantCoeff_apply]
  simp

theorem derivative_expShift (c : ℝ) :
    derivative (expShift c) = C c * expShift c := by
  ext n
  rw [coeff_derivative, coeff_C_mul, coeff_expShift, coeff_expShift]
  rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, pow_succ]
  have hn : (n : ℝ) + 1 ≠ 0 := by positivity
  have hf : (Nat.factorial n : ℝ) ≠ 0 := by positivity
  field_simp

theorem derivative_logOf_mul (P : PowerSeries ℝ) (hP : constantCoeff P = 1) :
    derivative (logOf P) * P = derivative P := by
  have hsubst : HasSubst (P - 1) :=
    HasSubst.of_constantCoeff_zero' (by simp [hP])
  have hkey : (derivative (PowerSeries.log ℝ)).subst (P - 1) * P = 1 := by
    have h := congrArg (fun f : PowerSeries ℝ => f.subst (P - 1))
      (derivative_log_mul_one_add_X (A := ℝ))
    have harg : (1 + X : PowerSeries ℝ).subst (P - 1) = P := by
      rw [← coe_substAlgHom hsubst, map_add, map_one, substAlgHom_X]
      ring
    have hone : (1 : PowerSeries ℝ).subst (P - 1) = 1 := by
      rw [← coe_substAlgHom hsubst, map_one]
    rw [subst_mul hsubst, harg, hone] at h
    exact h
  rw [logOf_eq, derivative_subst hsubst]
  simp only [map_sub, derivative_one, sub_zero]
  calc
    (derivative (PowerSeries.log ℝ)).subst (P - 1) * derivative P * P =
        derivative P * ((derivative (PowerSeries.log ℝ)).subst (P - 1) * P) := by ring
    _ = derivative P := by rw [hkey, mul_one]

theorem factorialCumulant_eq_formal_derivative (P : PowerSeries ℝ) (r : ℕ) :
    factorialCumulant P r = constantCoeff (derivative^[r] (logOf P)) := by
  exact (constantCoeff_iterate_derivative (logOf P) r).symm

theorem coeff_one_logOf (P : PowerSeries ℝ) (hP : constantCoeff P = 1) :
    coeff 1 (logOf P) = coeff 1 P := by
  have h := congrArg (constantCoeff (R := ℝ)) (derivative_logOf_mul P hP)
  rw [map_mul, hP, mul_one] at h
  simpa only [← coeff_zero_eq_constantCoeff_apply, coeff_derivative,
    Nat.cast_zero, zero_add, mul_one] using h

theorem coeff_mul_congr_upto (P Q U V : PowerSeries ℝ) (n : ℕ)
    (hPQ : ∀ i ≤ n, coeff i P = coeff i Q)
    (hUV : ∀ i ≤ n, coeff i U = coeff i V) :
    coeff n (P * U) = coeff n (Q * V) := by
  rw [coeff_mul, coeff_mul]
  apply Finset.sum_congr rfl
  intro ij hij
  have hs : ij.1 + ij.2 = n := Finset.mem_antidiagonal.mp hij
  rw [hPQ ij.1 (by omega), hUV ij.2 (by omega)]

theorem ode_coeff_unique (N : ℕ) (P Q U V : PowerSeries ℝ)
    (hP : derivative P = P * U) (hQ : derivative Q = Q * V)
    (hzero : constantCoeff P = constantCoeff Q)
    (hUV : ∀ i < N, coeff i U = coeff i V) :
    ∀ n ≤ N, coeff n P = coeff n Q := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro hn
    cases n with
    | zero => simpa only [coeff_zero_eq_constantCoeff_apply] using hzero
    | succ n =>
      have hprod : coeff n (P * U) = coeff n (Q * V) :=
        coeff_mul_congr_upto P Q U V n
          (fun i hi => ih i (by omega) (by omega))
          (fun i hi => hUV i (by omega))
      have hder : coeff n (derivative P) = coeff n (derivative Q) := by
        rw [hP, hQ]
        exact hprod
      rw [coeff_derivative, coeff_derivative] at hder
      have hnz : (n : ℝ) + 1 ≠ 0 := by positivity
      exact mul_right_cancel₀ hnz hder

theorem tilt_jet_of_log_coefficients (D : ℕ) (P Q : PowerSeries ℝ)
    (hP0 : constantCoeff P = 1) (hQ0 : constantCoeff Q = 1)
    (hlog : ∀ r, 2 ≤ r → r ≤ D + 1 → coeff r (logOf P) = coeff r (logOf Q)) :
    ∀ n ≤ D + 1, coeff n P =
      coeff n (Q * expShift (coeff 1 (logOf P) - coeff 1 (logOf Q))) := by
  let c := coeff 1 (logOf P) - coeff 1 (logOf Q)
  have hPode : derivative P = P * derivative (logOf P) := by
    rw [mul_comm]
    exact (derivative_logOf_mul P hP0).symm
  have hQode : derivative Q = Q * derivative (logOf Q) := by
    rw [mul_comm]
    exact (derivative_logOf_mul Q hQ0).symm
  have hTode : derivative (Q * expShift c) =
      (Q * expShift c) * (derivative (logOf Q) + C c) := by
    rw [Derivation.leibniz, hQode, derivative_expShift]
    simp only [smul_eq_mul]
    ring
  apply ode_coeff_unique (D + 1) P (Q * expShift c)
      (derivative (logOf P)) (derivative (logOf Q) + C c) hPode hTode
  · simp [hP0, hQ0]
  · intro i hi
    by_cases hiz : i = 0
    · subst i
      simp only [map_add, coeff_derivative, coeff_zero_C]
      dsimp [c]
      ring
    · rw [map_add, coeff_C_of_ne_zero hiz, add_zero,
          coeff_derivative, coeff_derivative]
      rw [hlog (i + 1) (by omega) (by omega)]

theorem coeff_mul_expShift_pos (Q : PowerSeries ℝ) (c : ℝ) (n : ℕ)
    (hQ0 : constantCoeff Q = 1) (hQ : ∀ j, 0 ≤ coeff j Q) (hc : 0 < c) :
    0 < coeff n (Q * expShift c) := by
  rw [coeff_mul]
  apply Finset.sum_pos'
  · intro ij hij
    rw [coeff_expShift]
    have := hQ ij.1
    positivity
  · refine ⟨(0, n), ?_, ?_⟩
    · simp
    · rw [coeff_expShift, coeff_zero_eq_constantCoeff_apply, hQ0]
      positivity

theorem first_log_coeff_le (D : ℕ) (P Q : PowerSeries ℝ)
    (hP0 : constantCoeff P = 1) (hQ0 : constantCoeff Q = 1)
    (hQ : ∀ j, 0 ≤ coeff j Q) (hPtop : coeff (D + 1) P = 0)
    (hlog : ∀ r, 2 ≤ r → r ≤ D + 1 → coeff r (logOf P) = coeff r (logOf Q)) :
    coeff 1 (logOf P) ≤ coeff 1 (logOf Q) := by
  by_contra hnot
  have hc : 0 < coeff 1 (logOf P) - coeff 1 (logOf Q) := sub_pos.mpr (lt_of_not_ge hnot)
  have hjet := tilt_jet_of_log_coefficients D P Q hP0 hQ0 hlog (D + 1) (le_refl _)
  have hpos := coeff_mul_expShift_pos Q _ (D + 1) hQ0 hQ hc
  rw [← hjet, hPtop] at hpos
  exact (lt_irrefl 0) hpos

@[simp] theorem expShift_zero : expShift 0 = (1 : PowerSeries ℝ) := by
  ext n
  by_cases hn : n = 0
  · subst n
    simp
  · simp [coeff_expShift, PowerSeries.coeff_one, hn]

theorem bounded_nonnegative_series_identified (D : ℕ) (P Q : PowerSeries ℝ)
    (hP0 : constantCoeff P = 1) (hQ0 : constantCoeff Q = 1)
    (hP : ∀ j, 0 ≤ coeff j P) (hQ : ∀ j, 0 ≤ coeff j Q)
    (hPdegree : ∀ n, D < n → coeff n P = 0)
    (hQdegree : ∀ n, D < n → coeff n Q = 0)
    (hcumulant : ∀ r, 2 ≤ r → r ≤ D + 1 → factorialCumulant P r = factorialCumulant Q r) :
    P = Q := by
  have hlog : ∀ r, 2 ≤ r → r ≤ D + 1 → coeff r (logOf P) = coeff r (logOf Q) := by
    intro r hr hD
    have h := hcumulant r hr hD
    unfold factorialCumulant at h
    exact mul_left_cancel₀ (by positivity : (Nat.factorial r : ℝ) ≠ 0) h
  have hle := first_log_coeff_le D P Q hP0 hQ0 hQ (hPdegree (D + 1) (by omega)) hlog
  have hge := first_log_coeff_le D Q P hQ0 hP0 hP (hQdegree (D + 1) (by omega))
    (fun r hr hD => (hlog r hr hD).symm)
  have hc : coeff 1 (logOf P) - coeff 1 (logOf Q) = 0 := sub_eq_zero.mpr (le_antisymm hle hge)
  have hjet := tilt_jet_of_log_coefficients D P Q hP0 hQ0 hlog
  rw [hc, expShift_zero, mul_one] at hjet
  ext n
  by_cases hn : n ≤ D + 1
  · exact hjet n hn
  · rw [hPdegree n (by omega), hQdegree n (by omega)]

#print axioms derivative_logOf_mul
#print axioms tilt_jet_of_log_coefficients
#print axioms bounded_nonnegative_series_identified

end CountSeriesCore
