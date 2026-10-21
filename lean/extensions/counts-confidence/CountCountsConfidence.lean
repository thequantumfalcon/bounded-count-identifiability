import CountConfidenceExecutable
import BernoulliPoissonStatisticsV1

/-!
Exact rational aggregation of a finite natural-count record, outward radius
certification, and model-conditional coverage of the resulting rational box.
Parsing, acquisition, model calibration, and compiled runtime correctness are
not asserted. The probability theorem is for fixed independent Poisson noise.
-/

open MeasureTheory ProbabilityTheory
open scoped BigOperators NNReal

namespace CountCountsConfidence

def firstMean {N : ℕ} (counts : Fin N → ℕ) : ℚ :=
  (N : ℚ)⁻¹ * ∑ i, (counts i : ℚ)

def secondMean {N : ℕ} (counts : Fin N → ℕ) : ℚ :=
  (N : ℚ)⁻¹ * ∑ i, ((counts i).descFactorial 2 : ℚ)

theorem firstMean_cast {N : ℕ} {Ω : Type*}
    (counts : Fin N → Ω → ℕ) (ω : Ω) :
    (firstMean (fun i => counts i ω) : ℝ) =
      CountFiniteSampleMean.sampleMean (fun i ω => (counts i ω : ℝ)) ω := by
  simp [firstMean, CountFiniteSampleMean.sampleMean]

theorem secondMean_cast {N : ℕ} {Ω : Type*}
    (counts : Fin N → Ω → ℕ) (ω : Ω) :
    (secondMean (fun i => counts i ω) : ℝ) =
      CountFiniteSampleMean.sampleMean
        (fun i ω => (counts i ω : ℝ) * ((counts i ω : ℝ) - 1)) ω := by
  unfold secondMean CountFiniteSampleMean.sampleMean
  push_cast
  congr 1
  exact Finset.sum_congr rfl (fun i _ => Nat.cast_descFactorial_two ℝ (counts i ω))

def radiusChecks (N : ℕ) (B α R1 R2 : ℚ) : Prop :=
  0 < N ∧ 0 ≤ B ∧ 0 < α ∧ 0 ≤ R1 ∧ 0 ≤ R2 ∧
    2*(B+1/4) ≤ (N:ℚ)*α*R1^2 ∧
    2*(4*B^3+10*B^2+4*B) ≤ (N:ℚ)*α*R2^2

instance (N : ℕ) (B α R1 R2 : ℚ) : Decidable (radiusChecks N B α R1 R2) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))

def checkRadii (N : ℕ) (B α R1 R2 : ℚ) : Bool :=
  decide (radiusChecks N B α R1 R2)

theorem checkRadii_eq_true_iff (N : ℕ) (B α R1 R2 : ℚ) :
    checkRadii N B α R1 R2 = true ↔ radiusChecks N B α R1 R2 := by
  simp only [checkRadii, decide_eq_true_eq]

theorem checkRadii_eq_false_iff (N : ℕ) (B α R1 R2 : ℚ) :
    checkRadii N B α R1 R2 = false ↔ ¬ radiusChecks N B α R1 R2 := by
  simp only [checkRadii, decide_eq_false_iff_not]

/-- An exact rational squared inequality certifies an outward real radius. -/
theorem sqrt_radius_le {N : ℕ} {W α R : ℚ}
    (hN : 0 < N) (hα : 0 < α) (hR : 0 ≤ R)
    (hsq : 2*W ≤ (N:ℚ)*α*R^2) :
    Real.sqrt (2*(W:ℝ)/((N:ℝ)*(α:ℝ))) ≤ (R:ℝ) := by
  apply (Real.sqrt_le_left (by exact_mod_cast hR)).mpr
  apply (div_le_iff₀ (by positivity : 0 < (N:ℝ)*(α:ℝ))).mpr
  have h : 2*(W:ℝ) ≤ (N:ℝ)*(α:ℝ)*(R:ℝ)^2 := by exact_mod_cast hsq
  nlinarith

theorem checkRadii_encloses {N : ℕ} {B α R1 R2 : ℚ}
    (h : checkRadii N B α R1 R2 = true) :
    Real.sqrt (2*((B:ℝ)+1/4)/((N:ℝ)*(α:ℝ))) ≤ (R1:ℝ) ∧
    Real.sqrt (2*(4*(B:ℝ)^3+10*(B:ℝ)^2+4*(B:ℝ))/((N:ℝ)*(α:ℝ))) ≤ (R2:ℝ) := by
  obtain ⟨hN, _, hα, h1, h2, hs1, hs2⟩ := (checkRadii_eq_true_iff ..).mp h
  constructor
  · simpa only [Rat.cast_add, Rat.cast_div, Rat.cast_one, Rat.cast_ofNat] using
      (sqrt_radius_le hN hα h1 hs1)
  · simpa only [Rat.cast_add, Rat.cast_mul, Rat.cast_pow, Rat.cast_ofNat] using
      (sqrt_radius_le hN hα h2 hs2)

/-- If the actual two moments are in the computed box, the true pair is feasible. -/
theorem pairFeasible_of_errors {N : ℕ} (counts : Fin N → ℕ)
    (B R1 R2 : ℚ) (p b : ℝ)
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hb0 : 0 ≤ b) (hbB : b ≤ (B:ℝ))
    (h1 : |(firstMean counts : ℝ)-(p+b)| ≤ (R1:ℝ))
    (h2 : |(secondMean counts : ℝ)-(b^2+2*p*b)| ≤ (R2:ℝ)) :
    CountConfidenceExecutable.PairFeasible (B:ℝ)
      (firstMean counts-R1 : ℚ) (firstMean counts+R1 : ℚ)
      (secondMean counts-R2 : ℚ) (secondMean counts+R2 : ℚ) p b := by
  obtain ⟨h1l, h1u⟩ := abs_le.mp h1
  obtain ⟨h2l, h2u⟩ := abs_le.mp h2
  unfold CountConfidenceExecutable.PairFeasible
  push_cast
  exact ⟨hp0, hp1, hb0, hbB, by linarith, by linarith, by nlinarith, by nlinarith⟩

open BoundedCountLaw CountProbabilityBridge CountD1LawBridge
open BernoulliPoissonStatisticsV1

/-- With specified marginal laws and unconditional pairwise independent observed
windows, rational outward radii give failure probability at most alpha.
The true source and fixed background parameters need not be rational. -/
theorem rational_pair_coverage {Ω : Type*} [MeasurableSpace Ω]
    {μ : Measure Ω} [IsProbabilityMeasure μ] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (B α R1 R2 : ℚ) (hrB : (r:ℝ) ≤ (B:ℝ))
    (hR : checkRadii N B α R1 R2 = true)
    (X : Fin N → Ω → Fin 2) (Y : Fin N → Ω → ℕ)
    (hX : ∀ i, HasLaw (X i) (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : ∀ i, HasLaw (Y i) (poissonMeasure r) μ)
    (hXY : ∀ i, IndepFun (X i) (Y i) μ)
    (hI : Pairwise fun i j => IndepFun (count (X i) (Y i)) (count (X j) (Y j)) μ) :
    let records := fun ω i => ((X i ω : ℕ) + Y i ω)
    μ {ω | ¬ CountConfidenceExecutable.PairFeasible (B:ℝ)
      (firstMean (records ω)-R1 : ℚ) (firstMean (records ω)+R1 : ℚ)
      (secondMean (records ω)-R2 : ℚ) (secondMean (records ω)+R2 : ℚ) p r} ≤
        ENNReal.ofReal (α:ℝ) := by
  dsimp only
  obtain ⟨hN, _, hα, _, _, _, _⟩ := (checkRadii_eq_true_iff ..).mp hR
  obtain ⟨hR1, hR2⟩ := checkRadii_encloses hR
  refine (measure_mono ?_).trans (sample_means_coverage p hp0 hp1 r (B:ℝ) hrB
    X Y hX hY hXY hI hN (α:ℝ) (by exact_mod_cast hα))
  intro ω hbad
  by_contra hgood
  have h1 := (not_lt.mp (not_or.mp hgood).1).trans hR1
  have h2 := (not_lt.mp (not_or.mp hgood).2).trans hR2
  apply hbad
  apply pairFeasible_of_errors _ B R1 R2 p r hp0 hp1 r.coe_nonneg hrB
  · rw [firstMean_cast (fun i ω => ((X i ω : ℕ) + Y i ω)) ω]
    exact h1
  · rw [secondMean_cast (fun i ω => ((X i ω : ℕ) + Y i ω)) ω]
    exact h2

/-- The exact rational moment box also covers the true projected source. -/
theorem rational_projected_coverage {Ω : Type*} [MeasurableSpace Ω]
    {μ : Measure Ω} [IsProbabilityMeasure μ] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (B α R1 R2 : ℚ) (hrB : (r:ℝ) ≤ (B:ℝ))
    (hR : checkRadii N B α R1 R2 = true)
    (X : Fin N → Ω → Fin 2) (Y : Fin N → Ω → ℕ)
    (hX : ∀ i, HasLaw (X i) (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : ∀ i, HasLaw (Y i) (poissonMeasure r) μ)
    (hXY : ∀ i, IndepFun (X i) (Y i) μ)
    (hI : Pairwise fun i j => IndepFun (count (X i) (Y i)) (count (X j) (Y j)) μ) :
    let records := fun ω i => ((X i ω : ℕ) + Y i ω)
    μ {ω | ¬ CountConfidenceProjection.Feasible (B:ℝ)
      (firstMean (records ω)-R1 : ℚ) (firstMean (records ω)+R1 : ℚ)
      (secondMean (records ω)-R2 : ℚ) (secondMean (records ω)+R2 : ℚ) p} ≤
        ENNReal.ofReal (α:ℝ) := by
  dsimp only
  refine (measure_mono ?_).trans
    (rational_pair_coverage p hp0 hp1 r B α R1 R2 hrB hR X Y hX hY hXY hI)
  intro ω hbad hpair
  obtain ⟨hp0', hp1', hb0, hbB, ha, hc, hd, he⟩ := hpair
  exact hbad ⟨hp0', hp1', r, hb0, hbB, ha, hc, hd, he⟩

/-- Under the same model, the executable empty-region verdict occurs with
probability at most alpha. This does not require rational true parameters. -/
theorem nonempty_decision_coverage {Ω : Type*} [MeasurableSpace Ω]
    {μ : Measure Ω} [IsProbabilityMeasure μ] {N : ℕ}
    (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (r : ℝ≥0)
    (B α R1 R2 : ℚ) (hrB : (r:ℝ) ≤ (B:ℝ))
    (hR : checkRadii N B α R1 R2 = true)
    (X : Fin N → Ω → Fin 2) (Y : Fin N → Ω → ℕ)
    (hX : ∀ i, HasLaw (X i) (boundedMeasure 1 (bernoulliMass p)
      (bernoulliMass_isBoundedLaw p hp0 hp1)) μ)
    (hY : ∀ i, HasLaw (Y i) (poissonMeasure r) μ)
    (hXY : ∀ i, IndepFun (X i) (Y i) μ)
    (hI : Pairwise fun i j => IndepFun (count (X i) (Y i)) (count (X j) (Y j)) μ) :
    let records := fun ω i => ((X i ω : ℕ) + Y i ω)
    μ {ω | CountConfidenceExecutable.checkNonempty B
      (firstMean (records ω)-R1) (firstMean (records ω)+R1)
      (secondMean (records ω)-R2) (secondMean (records ω)+R2) = false} ≤
        ENNReal.ofReal (α:ℝ) := by
  dsimp only
  refine (measure_mono ?_).trans
    (rational_projected_coverage p hp0 hp1 r B α R1 R2 hrB hR X Y hX hY hXY hI)
  intro ω hbad hfeasible
  exact ((CountConfidenceExecutable.checkNonempty_eq_false_iff ..).mp hbad) ⟨p, hfeasible⟩

end CountCountsConfidence
