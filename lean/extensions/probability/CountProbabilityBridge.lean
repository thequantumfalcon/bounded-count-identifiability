import CountIdentification
import Mathlib.Probability.ProbabilityMassFunction.Basic
import Mathlib.MeasureTheory.Integral.Bochner.SumMeasure

/-!
The finite nonnegative mass vector from the core theorem gives an actual
mathlib PMF and probability measure. The generating polynomial is the
Bochner expectation of the ordinary finite random variable on this space.
No Poisson independence or analytic logarithm theorem is asserted here.
-/

noncomputable section
open scoped BigOperators
open MeasureTheory BoundedCountLaw

namespace CountProbabilityBridge

def boundedPMF (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p) : PMF (Fin (D+1)) :=
  ⟨fun n => ENNReal.ofReal (p n), by
    have hs : ∑ n : Fin (D+1), ENNReal.ofReal (p n) = 1 := by
      rw [← ENNReal.ofReal_sum_of_nonneg (s := Finset.univ)
        (f := fun n : Fin (D+1) => p n) (fun n _ => hp.1 n)]
      rw [Fin.sum_univ_eq_sum_range, hp.2.1]
      exact ENNReal.ofReal_one
    exact hs ▸ hasSum_fintype (fun n : Fin (D+1) => ENNReal.ofReal (p n))⟩

theorem boundedPMF_mass (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p)
    (n : Fin (D+1)) : (boundedPMF D p hp n).toReal = p n := by
  exact ENNReal.toReal_ofReal (hp.1 n)

def boundedMeasure (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p) :
    Measure (Fin (D+1)) := (boundedPMF D p hp).toMeasure

theorem boundedMeasure_isProbability (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p) :
    IsProbabilityMeasure (boundedMeasure D p hp) := by
  unfold boundedMeasure
  infer_instance

theorem boundedMeasure_singleton (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p)
    (n : Fin (D+1)) : boundedMeasure D p hp {n} = ENNReal.ofReal (p n) := by
  exact (boundedPMF D p hp).toMeasure_apply_singleton n (MeasurableSet.singleton n)

theorem integral_boundedMeasure (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p)
    (f : ℕ → ℝ) :
    ∫ n : Fin (D+1), f n ∂(boundedMeasure D p hp) =
      ∑ n ∈ Finset.range (D+1), p n * f n := by
  have := boundedMeasure_isProbability D p hp
  rw [integral_fintype Integrable.of_finite]
  simp_rw [measureReal_def, boundedMeasure_singleton, ENNReal.toReal_ofReal (hp.1 _),
    smul_eq_mul]
  exact Fin.sum_univ_eq_sum_range (fun n => p n * f n) (D+1)

theorem factorialPGF_eval_eq_expectation (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (t : ℝ) :
    (factorialPGF D p).eval t =
      ∫ n : Fin (D+1), (1+t)^(n : ℕ) ∂(boundedMeasure D p hp) := by
  rw [integral_boundedMeasure]
  simp [factorialPGF, Polynomial.eval_finsetSum]

theorem factorialPGF_coeff_eq_binomial_expectation (D k : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) :
    (factorialPGF D p).coeff k =
      ∫ n : Fin (D+1), ((n : ℕ).choose k : ℝ) ∂(boundedMeasure D p hp) := by
  rw [integral_boundedMeasure D p hp (fun n : ℕ => (n.choose k : ℝ)), factorialPGF_coeff]

theorem higher_factorial_cumulants_identify_measures (D : ℕ) (p q : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (hq : IsBoundedLaw D q)
    (hc : ∀ r, 2 ≤ r → r ≤ D+1 →
      lawFactorialCumulant D p r = lawFactorialCumulant D q r) :
    boundedMeasure D p hp = boundedMeasure D q hq := by
  have h := higher_factorial_cumulants_identify D p q hp hq hc
  subst q
  rfl

end CountProbabilityBridge

#print axioms CountProbabilityBridge.boundedPMF_mass
#print axioms CountProbabilityBridge.boundedMeasure_isProbability
#print axioms CountProbabilityBridge.boundedMeasure_singleton
#print axioms CountProbabilityBridge.integral_boundedMeasure
#print axioms CountProbabilityBridge.factorialPGF_eval_eq_expectation
#print axioms CountProbabilityBridge.factorialPGF_coeff_eq_binomial_expectation
#print axioms CountProbabilityBridge.higher_factorial_cumulants_identify_measures
