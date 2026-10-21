import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Inverse stability for the algebraic D = 1 count model.

The interpretation of `secondCumulant p = -p^2` as the second factorial
cumulant of a Bernoulli count is a separate generating-function identity.
No new probability-space or independent-Poisson construction is formalized
in this file. The inequalities hold for every nonnegative real p and q;
physical Bernoulli parameters additionally lie in [0, 1].
No originality or optimality claim is made.
-/

noncomputable section

namespace CountD1Stability

def secondCumulant (p : ℝ) : ℝ := -(p ^ 2)

def backgroundFromMean (μ p : ℝ) : ℝ := μ - p

theorem abs_sub_le_sum (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p - q| ≤ p + q := by
  rw [abs_le]
  constructor <;> linarith

theorem abs_square_difference (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p ^ 2 - q ^ 2| = |p - q| * (p + q) := by
  rw [show p ^ 2 - q ^ 2 = (p - q) * (p + q) by ring,
    abs_mul, abs_of_nonneg (add_nonneg hp hq)]

theorem squared_parameter_error_le (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p - q| ^ 2 ≤ |p ^ 2 - q ^ 2| := by
  rw [abs_square_difference p q hp hq, pow_two]
  exact mul_le_mul_of_nonneg_left (abs_sub_le_sum p q hp hq) (abs_nonneg _)

theorem parameter_error_le_sqrt (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p - q| ≤ Real.sqrt |p ^ 2 - q ^ 2| := by
  have h := Real.sqrt_le_sqrt (squared_parameter_error_le p q hp hq)
  simpa only [Real.sqrt_sq_eq_abs, abs_abs] using h

theorem second_cumulant_abs_difference (p q : ℝ) :
    |secondCumulant p - secondCumulant q| = |p ^ 2 - q ^ 2| := by
  unfold secondCumulant
  rw [show -(p ^ 2) - -(q ^ 2) = -(p ^ 2 - q ^ 2) by ring, abs_neg]

theorem parameter_error_from_cumulant (p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |p - q| ≤ Real.sqrt |secondCumulant p - secondCumulant q| := by
  rw [second_cumulant_abs_difference]
  exact parameter_error_le_sqrt p q hp hq

theorem background_error_le (μ ν p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    |backgroundFromMean μ p - backgroundFromMean ν q| ≤
      |μ - ν| + Real.sqrt |secondCumulant p - secondCumulant q| := by
  calc
    |backgroundFromMean μ p - backgroundFromMean ν q| = |(μ - ν) - (p - q)| := by
      unfold backgroundFromMean
      congr 1
      ring
    _ ≤ |μ - ν| + |p - q| := abs_sub _ _
    _ ≤ |μ - ν| + Real.sqrt |secondCumulant p - secondCumulant q| :=
      add_le_add_right (parameter_error_from_cumulant p q hp hq) _

theorem bounded_observation_error (μ ν p q ε δ : ℝ)
    (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hκ : |secondCumulant p - secondCumulant q| ≤ ε)
    (hμ : |μ - ν| ≤ δ) :
    |p - q| ≤ Real.sqrt ε ∧
      |backgroundFromMean μ p - backgroundFromMean ν q| ≤ δ + Real.sqrt ε := by
  have hs : Real.sqrt |secondCumulant p - secondCumulant q| ≤ Real.sqrt ε :=
    Real.sqrt_le_sqrt hκ
  constructor
  · exact (parameter_error_from_cumulant p q hp hq).trans hs
  · exact (background_error_le μ ν p q hp hq).trans (add_le_add hμ hs)

end CountD1Stability

#print axioms CountD1Stability.squared_parameter_error_le
#print axioms CountD1Stability.parameter_error_le_sqrt
#print axioms CountD1Stability.parameter_error_from_cumulant
#print axioms CountD1Stability.background_error_le
#print axioms CountD1Stability.bounded_observation_error
