import CountLargestRoot

/-!
Root structure at the mean (T05, Proposition 3). The location identity makes `topCoeff` at `m₀ + Δ` a polynomial in
`Δ` whose `k`-th derivative at zero is the binomial moment `q_{D+1-k}`. For a bounded law the first derivative is the
top probability `p D`.
-/

noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountRootStructure

open CountSeriesCore CountLargestRoot

/-- The location polynomial in `Δ`. -/
def locPoly (D : ℕ) (Q : PowerSeries ℝ) : Polynomial ℝ :=
  ∑ p ∈ Finset.antidiagonal (D + 1),
    Polynomial.C (coeff p.1 Q / (Nat.factorial p.2 : ℝ)) * Polynomial.X ^ p.2

/-- R1: the location polynomial evaluates to `topCoeff` at `m₀ + Δ`. -/
theorem locPoly_eval (D : ℕ) (Q : PowerSeries ℝ) (Δ : ℝ) :
    (locPoly D Q).eval Δ = topCoeff D Q (coeff 1 (logOf Q) + Δ) := by
  rw [top_coeff_location, locPoly, Polynomial.eval_finsetSum]
  refine Finset.sum_congr rfl fun p _ => ?_
  simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow, Polynomial.eval_X]
  ring

theorem locPoly_coeff (D : ℕ) (Q : PowerSeries ℝ) (k : ℕ) (hk : k ≤ D + 1) :
    (locPoly D Q).coeff k = coeff (D + 1 - k) Q / (Nat.factorial k : ℝ) := by
  rw [locPoly, Polynomial.finsetSum_coeff]
  simp only [Polynomial.coeff_C_mul_X_pow]
  rw [Finset.sum_eq_single (D + 1 - k, k)]
  · simp
  · intro p hp hne
    have hs : p.1 + p.2 = D + 1 := Finset.mem_antidiagonal.mp hp
    have : k ≠ p.2 := by
      intro h
      apply hne
      ext <;> simp <;> omega
    simp [this]
  · intro h
    exfalso
    apply h
    rw [Finset.mem_antidiagonal]
    omega

/-- R2: `f^(k)(m₀) = q_{D+1-k}`. -/
theorem locPoly_iterate_derivative_eval_zero (D : ℕ) (Q : PowerSeries ℝ) (k : ℕ) (hk : k ≤ D + 1) :
    (Polynomial.derivative^[k] (locPoly D Q)).eval 0 = coeff (D + 1 - k) Q := by
  rw [← Polynomial.coeff_zero_eq_eval_zero, Polynomial.coeff_iterate_derivative, zero_add,
    Nat.descFactorial_self, locPoly_coeff D Q k hk, nsmul_eq_mul]
  have hf : (Nat.factorial k : ℝ) ≠ 0 := by positivity
  field_simp

/-- R3: for a bounded law, `f'(m₀) = Pr(X = D)`. -/
theorem law_derivative_at_mean (D : ℕ) (p : ℕ → ℝ) (_hp : BoundedCountLaw.IsBoundedLaw D p) :
    (Polynomial.derivative (locPoly D (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ))).eval 0 = p D := by
  have h := locPoly_iterate_derivative_eval_zero D (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ) 1 (by omega)
  simp only [Function.iterate_one, Nat.add_sub_cancel] at h
  rw [h, Polynomial.coeff_coe, BoundedCountLaw.factorialPGF_coeff]
  rw [Finset.sum_eq_single D]
  · simp
  · intro n hn hne
    rcases Nat.lt_or_gt_of_ne hne with hlt | hgt
    · simp [Nat.choose_eq_zero_of_lt hlt]
    · exact absurd (Finset.mem_range.mp hn) (by omega)
  · intro h
    exact absurd (Finset.mem_range.mpr (by omega)) h

end CountRootStructure

#print axioms CountRootStructure.locPoly_eval
#print axioms CountRootStructure.locPoly_iterate_derivative_eval_zero
#print axioms CountRootStructure.law_derivative_at_mean
