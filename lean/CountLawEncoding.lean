import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Tactic.Positivity

/-!
Finite probability mass vectors and their factorial generating polynomials.
This file provides the concrete law-to-polynomial bridge. The cumulant
identification theorem is developed separately.
-/

noncomputable section
open scoped BigOperators
open Polynomial

namespace BoundedCountLaw

def factorialPGF (D : ℕ) (p : ℕ → ℝ) : ℝ[X] :=
  ∑ n ∈ Finset.range (D+1), C (p n) * (1+X)^n

def ordinaryPGF (D : ℕ) (p : ℕ → ℝ) : ℝ[X] :=
  ∑ n ∈ Finset.range (D+1), C (p n) * X^n

theorem factorialPGF_coeff (D k : ℕ) (p : ℕ → ℝ) :
    (factorialPGF D p).coeff k =
      ∑ n ∈ Finset.range (D+1), p n * (n.choose k : ℝ) := by
  simp [factorialPGF, Polynomial.coeff_C_mul, Polynomial.coeff_one_add_X_pow]

theorem factorialPGF_constant (D : ℕ) (p : ℕ → ℝ)
    (hp : ∑ n ∈ Finset.range (D+1), p n = 1) :
    (factorialPGF D p).coeff 0 = 1 := by
  simpa [factorialPGF_coeff] using hp

theorem factorialPGF_coeff_nonneg (D k : ℕ) (p : ℕ → ℝ)
    (hp : ∀ n ≤ D, 0 ≤ p n) :
    0 ≤ (factorialPGF D p).coeff k := by
  rw [factorialPGF_coeff]
  apply Finset.sum_nonneg
  intro n hn
  apply mul_nonneg
  · exact hp n (Nat.le_of_lt_succ (Finset.mem_range.mp hn))
  · positivity

theorem factorialPGF_coeff_above (D k : ℕ) (p : ℕ → ℝ) (hk : D < k) :
    (factorialPGF D p).coeff k = 0 := by
  rw [factorialPGF_coeff]
  apply Finset.sum_eq_zero
  intro n hn
  have hnk : n < k := lt_of_le_of_lt (Nat.le_of_lt_succ (Finset.mem_range.mp hn)) hk
  simp [Nat.choose_eq_zero_of_lt hnk]

theorem ordinaryPGF_coeff (D k : ℕ) (p : ℕ → ℝ) (hk : k ≤ D) :
    (ordinaryPGF D p).coeff k = p k := by
  simp [ordinaryPGF, Finset.mem_range, Nat.lt_succ_of_le hk]

theorem factorialPGF_unshift (D : ℕ) (p : ℕ → ℝ) :
    (factorialPGF D p).comp (X-1) = ordinaryPGF D p := by
  simp [factorialPGF, ordinaryPGF, Polynomial.sum_comp, Polynomial.mul_comp,
    Polynomial.pow_comp, Polynomial.add_comp]

theorem factorialPGF_injective_on_support (D : ℕ) (p q : ℕ → ℝ)
    (h : factorialPGF D p = factorialPGF D q) :
    ∀ k ≤ D, p k = q k := by
  have h' := congrArg (fun P : ℝ[X] => P.comp (X-1)) h
  rw [factorialPGF_unshift, factorialPGF_unshift] at h'
  intro k hk
  have hc := congrArg (fun P : ℝ[X] => P.coeff k) h'
  simpa [ordinaryPGF_coeff D k p hk, ordinaryPGF_coeff D k q hk] using hc

end BoundedCountLaw

#print axioms BoundedCountLaw.factorialPGF_constant
#print axioms BoundedCountLaw.factorialPGF_coeff_nonneg
#print axioms BoundedCountLaw.factorialPGF_coeff_above
#print axioms BoundedCountLaw.factorialPGF_injective_on_support
