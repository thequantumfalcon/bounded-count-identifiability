import CountProbabilityBridge
import PoissonMGFV1
import Mathlib.Probability.HasLaw
import Mathlib.Probability.Independence.Integration

/-!
The generating-function identity for a bounded source plus an independent
Poisson count, stated for actual probability laws. Integrability is proved
explicitly. The logarithmic substitution is restricted to t > -1.
This does not identify analytic logarithm derivatives with formal cumulants.
-/

noncomputable section
open MeasureTheory ProbabilityTheory BoundedCountLaw CountProbabilityBridge
open scoped NNReal

namespace CountPoissonObservation

theorem bounded_exp_integrable (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (s : ℝ) :
    Integrable (fun n : Fin (D+1) => Real.exp (s * (n : ℕ)))
      (boundedMeasure D p hp) := by
  have := boundedMeasure_isProbability D p hp
  exact Integrable.of_finite

theorem bounded_exp_integral (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (s : ℝ) :
    (∫ n : Fin (D+1), Real.exp (s * (n : ℕ)) ∂boundedMeasure D p hp) =
      (factorialPGF D p).eval (Real.exp s - 1) := by
  rw [factorialPGF_eval_eq_expectation D p hp]
  apply integral_congr_ae
  filter_upwards [] with n
  rw [mul_comm s, Real.exp_nat_mul]
  congr 1
  ring

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

theorem observed_exp_integrable (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ)
    (hXY : IndepFun X Y μ) (s : ℝ) :
    Integrable (fun ω => Real.exp (s * (((X ω : ℕ) + Y ω : ℕ) : ℝ))) μ := by
  have hi := hXY.comp
    (measurable_of_countable (f := fun n : Fin (D+1) => Real.exp (s * (n : ℕ)) ))
    (measurable_of_countable (f := fun n : ℕ => Real.exp (s * (n : ℝ)) ))
  have hx := hX.integrable_comp (bounded_exp_integrable D p hp s)
  have hy := hY.integrable_comp (PoissonMGFV1.poisson_exp_integrable r s)
  have h := hi.integrable_mul hx hy
  simpa only [Function.comp_def, Pi.mul_def, Nat.cast_add, mul_add, Real.exp_add]
    using h

theorem observed_exp_integral [IsProbabilityMeasure μ] (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ)
    (hXY : IndepFun X Y μ) (s : ℝ) :
    (∫ ω, Real.exp (s * (((X ω : ℕ) + Y ω : ℕ) : ℝ)) ∂μ) =
      (factorialPGF D p).eval (Real.exp s - 1) *
        Real.exp ((r : ℝ) * (Real.exp s - 1)) := by
  have hi := hXY.comp
    (measurable_of_countable (f := fun n : Fin (D+1) => Real.exp (s * (n : ℕ)) ))
    (measurable_of_countable (f := fun n : ℕ => Real.exp (s * (n : ℝ)) ))
  have hxf := bounded_exp_integrable D p hp s
  have hyf := PoissonMGFV1.poisson_exp_integrable r s
  have hx := hX.integrable_comp hxf
  have hy := hY.integrable_comp hyf
  calc
    _ = (∫ ω, Real.exp (s * (X ω : ℕ)) * Real.exp (s * (Y ω : ℝ)) ∂μ) := by
      simp only [Nat.cast_add, mul_add, Real.exp_add]
    _ = (∫ ω, Real.exp (s * (X ω : ℕ)) ∂μ) *
        (∫ ω, Real.exp (s * (Y ω : ℝ)) ∂μ) :=
      hi.integral_fun_mul_eq_mul_integral hx.aestronglyMeasurable hy.aestronglyMeasurable
    _ = (∫ n : Fin (D+1), Real.exp (s * (n : ℕ)) ∂boundedMeasure D p hp) *
        (∫ n : ℕ, Real.exp (s * (n : ℝ)) ∂poissonMeasure r) := by
      simpa only [Function.comp_def] using congrArg₂ (fun a b : ℝ => a * b)
        (hX.integral_comp hxf.aestronglyMeasurable)
        (hY.integral_comp hyf.aestronglyMeasurable)
    _ = _ := by rw [bounded_exp_integral, PoissonMGFV1.poisson_exp_integral]

theorem observed_factorialPGF_integrable (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ)
    (hXY : IndepFun X Y μ) (t : ℝ) (ht : -1 < t) :
    Integrable (fun ω => (1+t)^((X ω : ℕ) + Y ω)) μ := by
  have ht0 : 0 < 1+t := by linarith
  have h := observed_exp_integrable D p hp r X Y hX hY hXY (Real.log (1+t))
  simpa only [mul_comm (Real.log (1+t)), Real.exp_nat_mul, Real.exp_log ht0] using h

theorem observed_factorialPGF_integral [IsProbabilityMeasure μ] (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ)
    (hXY : IndepFun X Y μ) (t : ℝ) (ht : -1 < t) :
    (∫ ω, (1+t)^((X ω : ℕ) + Y ω) ∂μ) =
      (factorialPGF D p).eval t * Real.exp ((r : ℝ) * t) := by
  have ht0 : 0 < 1+t := by linarith
  have h := observed_exp_integral D p hp r X Y hX hY hXY (Real.log (1+t))
  have ht1 : 1+t-1 = t := by ring
  simpa only [mul_comm (Real.log (1+t)), Real.exp_nat_mul, Real.exp_log ht0, ht1] using h

def independentPairMeasure (D : ℕ) (p : ℕ → ℝ) (hp : IsBoundedLaw D p)
    (r : ℝ≥0) : Measure (Fin (D+1) × ℕ) :=
  (boundedMeasure D p hp).prod (poissonMeasure r)

theorem independentPairMeasure_isProbability (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0) :
    IsProbabilityMeasure (independentPairMeasure D p hp r) := by
  have := boundedMeasure_isProbability D p hp
  unfold independentPairMeasure
  infer_instance

/-- A concrete probability space realizes both marginals and their independence. -/
theorem independentPairMeasure_hasLaws (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0) :
    HasLaw Prod.fst (boundedMeasure D p hp) (independentPairMeasure D p hp r) ∧
    HasLaw Prod.snd (poissonMeasure r) (independentPairMeasure D p hp r) ∧
    IndepFun Prod.fst Prod.snd (independentPairMeasure D p hp r) := by
  have := boundedMeasure_isProbability D p hp
  unfold independentPairMeasure
  exact ⟨measurePreserving_fst.hasLaw, measurePreserving_snd.hasLaw,
    indepFun_prod (X := id) (Y := id) measurable_id measurable_id⟩

theorem independentPairMeasure_factorialPGF (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0) (t : ℝ) (ht : -1 < t) :
    Integrable (fun ω : Fin (D+1) × ℕ => (1+t)^((ω.1 : ℕ) + ω.2))
      (independentPairMeasure D p hp r) ∧
    (∫ ω : Fin (D+1) × ℕ, (1+t)^((ω.1 : ℕ) + ω.2)
      ∂independentPairMeasure D p hp r) =
        (factorialPGF D p).eval t * Real.exp ((r : ℝ) * t) := by
  have := independentPairMeasure_isProbability D p hp r
  obtain ⟨hX, hY, hXY⟩ := independentPairMeasure_hasLaws D p hp r
  exact ⟨observed_factorialPGF_integrable D p hp r Prod.fst Prod.snd hX hY hXY t ht,
    observed_factorialPGF_integral D p hp r Prod.fst Prod.snd hX hY hXY t ht⟩

end CountPoissonObservation

#print axioms CountPoissonObservation.bounded_exp_integrable
#print axioms CountPoissonObservation.bounded_exp_integral
#print axioms CountPoissonObservation.observed_exp_integrable
#print axioms CountPoissonObservation.observed_exp_integral
#print axioms CountPoissonObservation.observed_factorialPGF_integrable
#print axioms CountPoissonObservation.observed_factorialPGF_integral
#print axioms CountPoissonObservation.independentPairMeasure_isProbability
#print axioms CountPoissonObservation.independentPairMeasure_hasLaws
#print axioms CountPoissonObservation.independentPairMeasure_factorialPGF
