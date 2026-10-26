import CountIdentification

/-!
The largest-root location of the mean (T05). Built on the bounded-count formal core: for the factorial-moment
series `Q` of a law, the coefficient of `t^(D+1)` of any normalized series sharing `Q`'s factorial cumulants of
orders 2..D+1 depends only on its first cumulant `m`, through `topCoeff D Q m`. That function vanishes at the true
mean and is strictly positive above it, so the mean is its largest real root.
-/

noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountLargestRoot

open CountSeriesCore

/-- The top coefficient after moving the first log coefficient of `Q` to `m`. -/
def topCoeff (D : ℕ) (Q : PowerSeries ℝ) (m : ℝ) : ℝ :=
  coeff (D + 1) (Q * expShift (m - coeff 1 (logOf Q)))

/-- T1: the top coefficient of any normalized series with the same higher log coefficients is `topCoeff` at its
own first log coefficient. -/
theorem top_coeff_of_matching_cumulants (D : ℕ) (Q R : PowerSeries ℝ)
    (hQ0 : constantCoeff Q = 1) (hR0 : constantCoeff R = 1)
    (hlog : ∀ r, 2 ≤ r → r ≤ D + 1 → coeff r (logOf R) = coeff r (logOf Q)) :
    coeff (D + 1) R = topCoeff D Q (coeff 1 (logOf R)) :=
  tilt_jet_of_log_coefficients D R Q hR0 hQ0 hlog (D + 1) le_rfl

/-- T2: the location identity, `topCoeff` at `m₀ + Δ` as an explicit polynomial in `Δ`. -/
theorem top_coeff_location (D : ℕ) (Q : PowerSeries ℝ) (Δ : ℝ) :
    topCoeff D Q (coeff 1 (logOf Q) + Δ) =
      ∑ p ∈ Finset.antidiagonal (D + 1), coeff p.1 Q * (Δ ^ p.2 / (Nat.factorial p.2 : ℝ)) := by
  unfold topCoeff
  rw [add_sub_cancel_left, coeff_mul]
  simp only [coeff_expShift]

theorem top_coeff_at_mean (D : ℕ) (Q : PowerSeries ℝ) (hQtop : coeff (D + 1) Q = 0) :
    topCoeff D Q (coeff 1 (logOf Q)) = 0 := by
  unfold topCoeff
  rw [sub_self, expShift_zero, mul_one, hQtop]

theorem top_coeff_pos_above_mean (D : ℕ) (Q : PowerSeries ℝ)
    (hQ0 : constantCoeff Q = 1) (hQ : ∀ j, 0 ≤ coeff j Q) (m : ℝ) (hm : coeff 1 (logOf Q) < m) :
    0 < topCoeff D Q m := by
  unfold topCoeff
  exact coeff_mul_expShift_pos Q _ (D + 1) hQ0 hQ (sub_pos.mpr hm)

/-- T3: the first log coefficient is a root, and every real root lies at or below it. -/
theorem mean_is_largest_root (D : ℕ) (Q : PowerSeries ℝ)
    (hQ0 : constantCoeff Q = 1) (hQ : ∀ j, 0 ≤ coeff j Q) (hQtop : coeff (D + 1) Q = 0) :
    topCoeff D Q (coeff 1 (logOf Q)) = 0 ∧
      ∀ m, topCoeff D Q m = 0 → m ≤ coeff 1 (logOf Q) := by
  refine ⟨top_coeff_at_mean D Q hQtop, fun m hm => ?_⟩
  by_contra h
  have hpos := top_coeff_pos_above_mean D Q hQ0 hQ m (lt_of_not_ge h)
  rw [hm] at hpos
  exact lt_irrefl 0 hpos

/-- T4: for a bounded law, its mean is the largest real root of `topCoeff` of its factorial-moment series. -/
theorem law_mean_is_largest_root (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) :
    topCoeff D (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ)
        (∑ n ∈ Finset.range (D + 1), p n * n) = 0 ∧
      ∀ m, topCoeff D (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ) m = 0 →
        m ≤ ∑ n ∈ Finset.range (D + 1), p n * n := by
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
  have hmean : coeff 1 (logOf Q) = ∑ n ∈ Finset.range (D + 1), p n * n := by
    rw [coeff_one_logOf Q hQ0, hQdef, Polynomial.coeff_coe, BoundedCountLaw.factorialPGF_coeff]
    simp [Nat.choose_one_right]
  rw [← hmean]
  exact mean_is_largest_root D Q hQ0 hQ hQtop

end CountLargestRoot

#print axioms CountLargestRoot.top_coeff_of_matching_cumulants
#print axioms CountLargestRoot.top_coeff_location
#print axioms CountLargestRoot.mean_is_largest_root
#print axioms CountLargestRoot.law_mean_is_largest_root
