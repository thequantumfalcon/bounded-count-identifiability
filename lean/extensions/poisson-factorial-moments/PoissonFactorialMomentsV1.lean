import CountPoissonObservation
import CountD1LawBridge
import Mathlib.Data.Nat.Factorial.Cast
import Mathlib.Topology.Algebra.InfiniteSum.NatInt
import Mathlib.Probability.Moments.IntegrableExpMul
import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.Probability.Moments.Variance
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

open MeasureTheory ProbabilityTheory
open scoped NNReal Nat

namespace PoissonFactorialMomentsV1

private theorem poisson_factorial_shift (r : ℝ≥0) (k n : ℕ) :
    (Real.exp (-(r : ℝ)) * (r : ℝ) ^ (n + 1) / ((n + 1)!) : ℝ) *
        ((n + 1).descFactorial (k + 1) : ℝ) =
      (r : ℝ) * ((Real.exp (-(r : ℝ)) * (r : ℝ) ^ n / (n !) : ℝ) *
        (n.descFactorial k : ℝ)) := by
  rw [Nat.succ_descFactorial_succ, Nat.factorial_succ, Nat.cast_mul, Nat.cast_mul,
    pow_succ]
  have hn : ((n + 1 : ℕ) : ℝ) ≠ 0 := by positivity
  have hf : (n.factorial : ℝ) ≠ 0 := by positivity
  field_simp

private theorem poisson_descFactorial_hasSum (r : ℝ≥0) (k : ℕ) :
    HasSum (fun n : ℕ =>
      (Real.exp (-(r : ℝ)) * (r : ℝ) ^ n / (n !) : ℝ) *
        (n.descFactorial k : ℝ)) ((r : ℝ) ^ k) := by
  induction k with
  | zero => simpa using hasSum_one_poissonMeasure r
  | succ k ih =>
    rw [← hasSum_nat_add_iff' 1]
    simp only [Finset.sum_range_one, Nat.zero_descFactorial_succ,
      Nat.cast_zero, mul_zero, sub_zero]
    simp_rw [poisson_factorial_shift]
    simpa only [pow_succ, mul_comm (r : ℝ)] using ih.mul_left (r : ℝ)

/-- Every descending factorial is integrable for the actual Poisson measure. -/
theorem poisson_descFactorial_integrable (r : ℝ≥0) (k : ℕ) :
    Integrable (fun n : ℕ => (n.descFactorial k : ℝ)) (poissonMeasure r) := by
  rw [integrable_poissonMeasure_iff]
  simpa only [Real.norm_natCast] using (poisson_descFactorial_hasSum r k).summable

/-- The actual kth Poisson factorial moment equals the kth power of its rate. -/
theorem poisson_descFactorial_integral (r : ℝ≥0) (k : ℕ) :
    (∫ n : ℕ, (n.descFactorial k : ℝ) ∂poissonMeasure r) = (r : ℝ) ^ k := by
  have h := hasSum_integral_poissonMeasure (poisson_descFactorial_integrable r k)
  simp only [smul_eq_mul] at h
  exact h.unique (poisson_descFactorial_hasSum r k)

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

private theorem memLp_of_all_exp {Z : Ω → ℝ}
    (hZ : ∀ s : ℝ, Integrable (fun ω => Real.exp (s * Z ω)) μ) (q : ℝ≥0) :
    MemLp Z q μ := by
  apply memLp_of_mem_interior_integrableExpSet _ q
  have hset : integrableExpSet Z μ = Set.univ := Set.eq_univ_of_forall hZ
  rw [hset, interior_univ]
  trivial

private theorem factorial_two_memLp_of_all_exp {Z : Ω → ℝ}
    (hZ : ∀ s : ℝ, Integrable (fun ω => Real.exp (s * Z ω)) μ) :
    MemLp (fun ω => Z ω * (Z ω - 1)) 2 μ := by
  have hp (n : ℕ) : Integrable (fun ω => Z ω ^ n) μ :=
    integrable_pow_of_integrable_exp_mul (by norm_num : (1 : ℝ) ≠ 0) (hZ 1) (hZ (-1)) n
  have hm : AEStronglyMeasurable Z μ := by simpa using (hp 1).aestronglyMeasurable
  apply (memLp_two_iff_integrable_sq (hm.mul (hm.sub aestronglyMeasurable_const))).2
  convert ((hp 4).sub ((hp 3).const_mul 2)).add (hp 2) using 1
  ext ω
  simp only [Pi.mul_apply, Pi.sub_apply, Pi.add_apply]
  ring

/-- A Poisson count belongs to every finite Lp space, including zero rate. -/
theorem poisson_memLp (r : ℝ≥0) (q : ℝ≥0) :
    MemLp (fun n : ℕ => (n : ℝ)) q (poissonMeasure r) :=
  memLp_of_all_exp (PoissonMGFV1.poisson_exp_integrable r) q

open BoundedCountLaw CountProbabilityBridge CountPoissonObservation

/-- Every natural power of a bounded source plus independent Poisson count is integrable. -/
theorem observed_pow_integrable (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ) (k : ℕ) :
    Integrable (fun ω => (((X ω : ℕ) + Y ω : ℕ) : ℝ) ^ k) μ := by
  exact integrable_pow_of_integrable_exp_mul (by norm_num : (1 : ℝ) ≠ 0)
    (observed_exp_integrable D p hp r X Y hX hY hXY 1)
    (observed_exp_integrable D p hp r X Y hX hY hXY (-1)) k

/-- The actual observed count belongs to every finite Lp space. -/
theorem observed_memLp (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ) (q : ℝ≥0) :
    MemLp (fun ω => (((X ω : ℕ) + Y ω : ℕ) : ℝ)) q μ :=
  memLp_of_all_exp (observed_exp_integrable D p hp r X Y hX hY hXY) q

/-- Square integrability of the actual quadratic factorial statistic. -/
theorem observed_factorial_two_memLp (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (r : ℝ≥0)
    (X : Ω → Fin (D+1)) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure D p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ) :
    MemLp (fun ω => (((X ω : ℕ) + Y ω : ℕ) : ℝ) *
      ((((X ω : ℕ) + Y ω : ℕ) : ℝ) - 1)) 2 μ :=
  factorial_two_memLp_of_all_exp (observed_exp_integrable D p hp r X Y hX hY hXY)

private theorem cast_descFactorial_succ (n k : ℕ) :
    (n.descFactorial (k + 1) : ℝ) = (n.descFactorial k : ℝ) * ((n : ℝ) - k) := by
  have h := congrArg (fun m : ℕ => (m : ℝ)) (Nat.descFactorial_mul_self n k)
  push_cast at h
  nlinarith

private theorem cast_succ_descFactorial (n k : ℕ) :
    ((n + 1).descFactorial (k + 1) : ℝ) = (n.descFactorial (k + 1) : ℝ) +
      (k + 1 : ℝ) * (n.descFactorial k : ℝ) := by
  rw [Nat.succ_descFactorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one,
    cast_descFactorial_succ]
  ring

private theorem fin_two_add_descFactorial (x : Fin 2) (n k : ℕ) :
    (((x : ℕ) + n).descFactorial (k + 1) : ℝ) =
      (n.descFactorial (k + 1) : ℝ) +
        (k + 1 : ℝ) * ((x : ℕ) : ℝ) * (n.descFactorial k : ℝ) := by
  have hx : (x : ℕ) = 0 ∨ (x : ℕ) = 1 := by omega
  rcases hx with hx | hx
  · simp [hx]
  · simpa [hx, Nat.add_comm] using cast_succ_descFactorial n k

/-- All positive-order factorial moments of an independent {0,1} source plus Poisson count. -/
theorem fin_two_poisson_descFactorial [IsProbabilityMeasure μ]
    (p : ℕ → ℝ) (hp : IsBoundedLaw 1 p) (r : ℝ≥0)
    (X : Ω → Fin 2) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure 1 p hp) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ) (k : ℕ) :
    Integrable (fun ω => (((X ω : ℕ) + Y ω).descFactorial (k + 1) : ℝ)) μ ∧
    (∫ ω, (((X ω : ℕ) + Y ω).descFactorial (k + 1) : ℝ) ∂μ) =
      (r : ℝ) ^ (k + 1) + (k + 1 : ℝ) * p 1 * (r : ℝ) ^ k := by
  have := boundedMeasure_isProbability 1 p hp
  have hx : Integrable (fun ω => ((X ω : ℕ) : ℝ)) μ :=
    hX.integrable_comp (Integrable.of_finite
      (f := fun x : Fin 2 => ((x : ℕ) : ℝ)) (μ := boundedMeasure 1 p hp))
  have hy (j : ℕ) : Integrable (fun ω => ((Y ω).descFactorial j : ℝ)) μ :=
    hY.integrable_comp (poisson_descFactorial_integrable r j)
  have hi : IndepFun (fun ω => ((X ω : ℕ) : ℝ))
      (fun ω => ((Y ω).descFactorial k : ℝ)) μ :=
    hXY.comp (measurable_of_countable (fun x : Fin 2 => ((x : ℕ) : ℝ)))
      (measurable_of_countable (fun n : ℕ => (n.descFactorial k : ℝ)))
  have hprod : Integrable (fun ω => ((X ω : ℕ) : ℝ) *
      ((Y ω).descFactorial k : ℝ)) μ := hi.integrable_mul hx (hy k)
  have hprodC : Integrable (fun ω => (k + 1 : ℝ) *
      (((X ω : ℕ) : ℝ) * ((Y ω).descFactorial k : ℝ))) μ :=
    hprod.const_mul (k + 1 : ℝ)
  have heq : (fun ω => (((X ω : ℕ) + Y ω).descFactorial (k + 1) : ℝ)) =
      (fun ω => ((Y ω).descFactorial (k + 1) : ℝ) +
        (k + 1 : ℝ) * (((X ω : ℕ) : ℝ) * ((Y ω).descFactorial k : ℝ))) := by
    funext ω
    rw [fin_two_add_descFactorial]
    ring
  have hxint : (∫ ω, ((X ω : ℕ) : ℝ) ∂μ) = p 1 := by
    calc
      _ = ∫ x : Fin 2, ((x : ℕ) : ℝ) ∂boundedMeasure 1 p hp :=
        hX.integral_comp (measurable_of_countable
          (fun x : Fin 2 => ((x : ℕ) : ℝ))).aestronglyMeasurable
      _ = p 1 := by rw [integral_boundedMeasure]; simp [Finset.sum_range_succ]
  have hyint (j : ℕ) : (∫ ω, ((Y ω).descFactorial j : ℝ) ∂μ) = (r : ℝ) ^ j := by
    calc
      _ = ∫ n : ℕ, (n.descFactorial j : ℝ) ∂poissonMeasure r :=
        hY.integral_comp (measurable_of_countable
          (fun n : ℕ => (n.descFactorial j : ℝ))).aestronglyMeasurable
      _ = _ := poisson_descFactorial_integral r j
  rw [heq]
  constructor
  · exact (hy (k + 1)).add hprodC
  · rw [integral_add (hy (k + 1)) hprodC, integral_const_mul,
      hi.integral_fun_mul_eq_mul_integral hx.aestronglyMeasurable (hy k).aestronglyMeasurable,
      hxint, hyint, hyint]
    ring

/-- The actual Bernoulli-plus-Poisson factorial moment formula, valid also at all endpoints. -/
theorem bernoulli_poisson_descFactorial [IsProbabilityMeasure μ]
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (X : Ω → Fin 2) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure 1 (CountD1LawBridge.bernoulliMass p)
      (CountD1LawBridge.bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ) (k : ℕ) :
    Integrable (fun ω => (((X ω : ℕ) + Y ω).descFactorial (k + 1) : ℝ)) μ ∧
    (∫ ω, (((X ω : ℕ) + Y ω).descFactorial (k + 1) : ℝ) ∂μ) =
      (r : ℝ) ^ (k + 1) + (k + 1 : ℝ) * p * (r : ℝ) ^ k := by
  simpa [CountD1LawBridge.bernoulliMass] using fin_two_poisson_descFactorial
    (CountD1LawBridge.bernoulliMass p)
    (CountD1LawBridge.bernoulliMass_isBoundedLaw p hp0 hp1) r X Y hX hY hXY k

end PoissonFactorialMomentsV1

#print axioms PoissonFactorialMomentsV1.poisson_descFactorial_integrable
#print axioms PoissonFactorialMomentsV1.poisson_descFactorial_integral
#print axioms PoissonFactorialMomentsV1.poisson_memLp
#print axioms PoissonFactorialMomentsV1.observed_pow_integrable
#print axioms PoissonFactorialMomentsV1.observed_memLp
#print axioms PoissonFactorialMomentsV1.observed_factorial_two_memLp
#print axioms PoissonFactorialMomentsV1.fin_two_poisson_descFactorial
#print axioms PoissonFactorialMomentsV1.bernoulli_poisson_descFactorial
