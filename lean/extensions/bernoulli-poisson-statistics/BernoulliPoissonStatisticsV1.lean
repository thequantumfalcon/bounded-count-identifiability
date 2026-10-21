import PoissonFactorialMomentsV1
import CountConfidenceZeroAndTransforms
import CountConfidenceProjection

open MeasureTheory ProbabilityTheory
open scoped NNReal

namespace BernoulliPoissonStatisticsV1

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- The actual observed count, viewed as a real random variable. -/
def count (X : Ω → Fin 2) (Y : Ω → ℕ) : Ω → ℝ :=
  fun ω => (((X ω : ℕ) + Y ω : ℕ) : ℝ)

private theorem cast_descFactorial_succ (n k : ℕ) :
    (n.descFactorial (k + 1) : ℝ) = (n.descFactorial k : ℝ) * ((n : ℝ) - k) := by
  have h := congrArg (fun m : ℕ => (m : ℝ)) (Nat.descFactorial_mul_self n k)
  push_cast at h
  nlinarith

private theorem cast_descFactorial_three (n : ℕ) :
    (n.descFactorial 3 : ℝ) = (n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2) := by
  rw [show 3 = 2 + 1 from rfl, cast_descFactorial_succ, Nat.cast_descFactorial_two]
  norm_num

private theorem cast_descFactorial_four (n : ℕ) :
    (n.descFactorial 4 : ℝ) =
      (n : ℝ) * ((n : ℝ) - 1) * ((n : ℝ) - 2) * ((n : ℝ) - 3) := by
  rw [show 4 = 3 + 1 from rfl, cast_descFactorial_succ, cast_descFactorial_three]
  norm_num

open BoundedCountLaw CountProbabilityBridge CountD1LawBridge PoissonFactorialMomentsV1

section Model
variable [IsProbabilityMeasure μ]
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (X : Ω → Fin 2) (Y : Ω → ℕ)
    (hX : HasLaw X (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : HasLaw Y (poissonMeasure r) μ) (hXY : IndepFun X Y μ)

include hp0 hp1 hX hY hXY

omit [IsProbabilityMeasure μ] in
theorem count_memLp : MemLp (count X Y) 2 μ := by
  exact observed_memLp 1 (bernoulliMass p) (bernoulliMass_isBoundedLaw p hp0 hp1)
    r X Y hX hY hXY 2

omit [IsProbabilityMeasure μ] in
theorem factorial_two_memLp :
    MemLp (fun ω => count X Y ω * (count X Y ω - 1)) 2 μ :=
  observed_factorial_two_memLp 1 (bernoulliMass p)
    (bernoulliMass_isBoundedLaw p hp0 hp1) r X Y hX hY hXY

/-- Explicit first four factorial moments of the actual independent sum. -/
theorem first_four_factorial_moments :
    (∫ ω, count X Y ω ∂μ) = p + r ∧
    (∫ ω, count X Y ω * (count X Y ω - 1) ∂μ) = (r : ℝ)^2 + 2*p*r ∧
    (∫ ω, count X Y ω * (count X Y ω - 1) * (count X Y ω - 2) ∂μ) =
      (r : ℝ)^3 + 3*p*(r : ℝ)^2 ∧
    (∫ ω, count X Y ω * (count X Y ω - 1) *
      (count X Y ω - 2) * (count X Y ω - 3) ∂μ) =
      (r : ℝ)^4 + 4*p*(r : ℝ)^3 := by
  have h (k : ℕ) := (bernoulli_poisson_descFactorial p hp0 hp1 r X Y hX hY hXY k).2
  constructor
  · simpa [count, Nat.descFactorial_one, add_comm] using h 0
  constructor
  · simpa only [Nat.reduceAdd, Nat.cast_ofNat, Nat.cast_one, one_add_one_eq_two, count,
      Nat.cast_descFactorial_two, pow_one] using h 1
  constructor
  · simpa only [Nat.reduceAdd, Nat.cast_ofNat, count, cast_descFactorial_three,
      show (2 : ℝ) + 1 = 3 by norm_num] using h 2
  · simpa only [Nat.reduceAdd, Nat.cast_ofNat, count, cast_descFactorial_four,
      show (3 : ℝ) + 1 = 4 by norm_num] using h 3

/-- Actual expectations and variances of the two statistics used by the confidence region. -/
theorem means_and_variances :
    (∫ ω, count X Y ω ∂μ) = p + r ∧
    (∫ ω, count X Y ω * (count X Y ω - 1) ∂μ) = (r : ℝ)^2 + 2*p*r ∧
    variance (count X Y) μ = (r : ℝ) + p*(1-p) ∧
    variance (fun ω => count X Y ω * (count X Y ω - 1)) μ =
      4*(r : ℝ)^3 + (12*p + 2 - 4*p^2)*(r : ℝ)^2 + 4*p*r := by
  obtain ⟨h1, h2, h3, h4⟩ := first_four_factorial_moments p hp0 hp1 r X Y hX hY hXY
  have hZ := count_memLp p hp0 hp1 r X Y hX hY hXY
  have hF := factorial_two_memLp p hp0 hp1 r X Y hX hY hXY
  have hiZ := hZ.integrable (by norm_num : (1 : ENNReal) ≤ 2)
  have hiF := hF.integrable (by norm_num : (1 : ENNReal) ≤ 2)
  have hi3 : Integrable
      (fun ω => count X Y ω * (count X Y ω - 1) * (count X Y ω - 2)) μ := by
    simpa only [Nat.reduceAdd, count, cast_descFactorial_three] using
      (bernoulli_poisson_descFactorial p hp0 hp1 r X Y hX hY hXY 2).1
  have hi4 : Integrable
      (fun ω => count X Y ω * (count X Y ω - 1) *
        (count X Y ω - 2) * (count X Y ω - 3)) μ := by
    simpa only [Nat.reduceAdd, count, cast_descFactorial_four] using
      (bernoulli_poisson_descFactorial p hp0 hp1 r X Y hX hY hXY 3).1
  have hzsq : (fun ω => (count X Y ω)^2) =
      (fun ω => count X Y ω * (count X Y ω - 1) + count X Y ω) := by
    funext ω
    ring
  have hfsq : (fun ω => (count X Y ω * (count X Y ω - 1))^2) =
      (fun ω => (count X Y ω * (count X Y ω - 1) *
        (count X Y ω - 2) * (count X Y ω - 3)) +
        4 * (count X Y ω * (count X Y ω - 1) * (count X Y ω - 2)) +
        2 * (count X Y ω * (count X Y ω - 1))) := by
    funext ω
    ring
  have hi43 : Integrable (fun ω => (count X Y ω * (count X Y ω - 1) *
      (count X Y ω - 2) * (count X Y ω - 3)) +
      4 * (count X Y ω * (count X Y ω - 1) * (count X Y ω - 2))) μ :=
    hi4.add (hi3.const_mul 4)
  refine ⟨h1, h2, ?_, ?_⟩
  · rw [variance_eq_sub hZ]
    change (∫ ω, (count X Y ω)^2 ∂μ) - (∫ ω, count X Y ω ∂μ)^2 = _
    rw [hzsq, integral_add hiF hiZ, h1, h2]
    ring
  · rw [variance_eq_sub hF]
    change (∫ ω, (count X Y ω * (count X Y ω - 1))^2 ∂μ) -
      (∫ ω, count X Y ω * (count X Y ω - 1) ∂μ)^2 = _
    rw [hfsq, integral_add hi43 (hiF.const_mul 2),
      integral_add hi4 (hi3.const_mul 4), integral_const_mul, integral_const_mul,
      h2, h3, h4]
    ring

end Model

open CountFiniteSampleMean

/-- Simultaneous finite-sample factorial-moment coverage, derived from actual count laws.
Only pairwise independence across observed windows is required. -/
theorem sample_means_coverage [IsProbabilityMeasure μ] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (B : ℝ) (hrB : (r : ℝ) ≤ B)
    (X : Fin N → Ω → Fin 2) (Y : Fin N → Ω → ℕ)
    (hX : ∀ i, HasLaw (X i) (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : ∀ i, HasLaw (Y i) (poissonMeasure r) μ)
    (hXY : ∀ i, IndepFun (X i) (Y i) μ)
    (hI : Pairwise fun i j => IndepFun (count (X i) (Y i)) (count (X j) (Y j)) μ)
    (hN : 0 < N) (α : ℝ) (hα : 0 < α) :
    μ {ω | Real.sqrt (2 * (B + 1/4) / ((N : ℝ) * α)) <
          |sampleMean (fun i => count (X i) (Y i)) ω - (p + r)| ∨
        Real.sqrt (2 * (4*B^3 + 10*B^2 + 4*B) / ((N : ℝ) * α)) <
          |sampleMean (fun i ω => count (X i) (Y i) ω *
            (count (X i) (Y i) ω - 1)) ω - ((r : ℝ)^2 + 2*p*r)|} ≤
      ENNReal.ofReal α := by
  have hB : 0 ≤ B := r.coe_nonneg.trans hrB
  have hm (i : Fin N) := means_and_variances p hp0 hp1 r (X i) (Y i) (hX i) (hY i) (hXY i)
  have hv1 (i : Fin N) : variance (count (X i) (Y i)) μ ≤ B + 1/4 := by
    rw [(hm i).2.2.1]
    exact CountD1VarianceCoverage.first_variance_ceiling p r B hrB
  have hv2 (i : Fin N) :
      variance (fun ω => count (X i) (Y i) ω * (count (X i) (Y i) ω - 1)) μ ≤
        4*B^3 + 10*B^2 + 4*B := by
    rw [(hm i).2.2.2]
    exact CountD1VarianceCoverage.second_variance_ceiling p r B hp0 hp1 r.coe_nonneg hrB
  exact CountConfidenceZeroAndTransforms.factorial_sample_means_coverage μ
    (fun i => count (X i) (Y i))
    (fun i => count_memLp p hp0 hp1 r (X i) (Y i) (hX i) (hY i) (hXY i))
    (fun i => factorial_two_memLp p hp0 hp1 r (X i) (Y i) (hX i) (hY i) (hXY i))
    hN hI (p + r) ((r : ℝ)^2 + 2*p*r) (B + 1/4)
    (4*B^3 + 10*B^2 + 4*B) α (fun i => (hm i).1) (fun i => (hm i).2.1)
    (by positivity) (by positivity) hα hv1 hv2

omit [MeasurableSpace Ω] in
private theorem infeasible_subset_moment_failure
    (T1 T2 : Ω → ℝ) (p b B R1 R2 : ℝ)
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hb0 : 0 ≤ b) (hbB : b ≤ B) :
    {ω | ¬ CountConfidenceProjection.Feasible B
      (T1 ω - R1) (T1 ω + R1) (T2 ω - R2) (T2 ω + R2) p} ⊆
    {ω | R1 < |T1 ω - (p+b)| ∨ R2 < |T2 ω - (b^2 + 2*p*b)|} := by
  intro ω h
  by_contra hbad
  have h1 := abs_le.mp (not_lt.mp (not_or.mp hbad).1)
  have h2 := abs_le.mp (not_lt.mp (not_or.mp hbad).2)
  apply h
  refine ⟨hp0, hp1, b, hb0, hbB, ?_, ?_, ?_, ?_⟩ <;> nlinarith [h1.1, h1.2, h2.1, h2.2]

/-- The projected region covers the true Bernoulli parameter with failure probability at most α.
This includes zero background bound; no strict positivity of variance ceilings is assumed. -/
theorem projected_region_coverage [IsProbabilityMeasure μ] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (B : ℝ) (hrB : (r : ℝ) ≤ B)
    (X : Fin N → Ω → Fin 2) (Y : Fin N → Ω → ℕ)
    (hX : ∀ i, HasLaw (X i) (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : ∀ i, HasLaw (Y i) (poissonMeasure r) μ)
    (hXY : ∀ i, IndepFun (X i) (Y i) μ)
    (hI : Pairwise fun i j => IndepFun (count (X i) (Y i)) (count (X j) (Y j)) μ)
    (hN : 0 < N) (α : ℝ) (hα : 0 < α) :
    let T1 := sampleMean (fun i => count (X i) (Y i))
    let T2 := sampleMean (fun i ω => count (X i) (Y i) ω * (count (X i) (Y i) ω - 1))
    let R1 := Real.sqrt (2 * (B + 1/4) / ((N : ℝ) * α))
    let R2 := Real.sqrt (2 * (4*B^3 + 10*B^2 + 4*B) / ((N : ℝ) * α))
    μ {ω | ¬ CountConfidenceProjection.Feasible B
      (T1 ω - R1) (T1 ω + R1) (T2 ω - R2) (T2 ω + R2) p} ≤ ENNReal.ofReal α := by
  dsimp only
  exact (measure_mono (infeasible_subset_moment_failure _ _ p r B _ _
    hp0 hp1 r.coe_nonneg hrB)).trans
    (sample_means_coverage p hp0 hp1 r B hrB X Y hX hY hXY hI hN α hα)

end BernoulliPoissonStatisticsV1

#print axioms BernoulliPoissonStatisticsV1.count_memLp
#print axioms BernoulliPoissonStatisticsV1.factorial_two_memLp
#print axioms BernoulliPoissonStatisticsV1.first_four_factorial_moments
#print axioms BernoulliPoissonStatisticsV1.means_and_variances
#print axioms BernoulliPoissonStatisticsV1.sample_means_coverage
#print axioms BernoulliPoissonStatisticsV1.projected_region_coverage
