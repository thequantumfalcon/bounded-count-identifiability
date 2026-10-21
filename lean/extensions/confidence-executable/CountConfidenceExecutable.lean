import CountConfidenceProjection
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Tactic.Tauto

/-!
Computable exact-rational decisions for the fixed-rate D=1 feasible region.
The Boolean programs below use only rational arithmetic and comparisons.
Their specifications quantify over real background/source witnesses where stated.
This does not verify Sage's algebraic-number implementation, parser or runtime.
-/

namespace CountConfidenceExecutable

open CountConfidenceProjection

def PairFeasible (B a c d e p b : ℝ) : Prop :=
  0 ≤ p ∧ p ≤ 1 ∧ 0 ≤ b ∧ b ≤ B ∧ a ≤ p+b ∧ p+b ≤ c ∧
    d ≤ (p+b)^2-p^2 ∧ (p+b)^2-p^2 ≤ e

def checkPair (B a c d e p b : ℚ) : Bool :=
  decide (0 ≤ p ∧ p ≤ 1 ∧ 0 ≤ b ∧ b ≤ B ∧ a ≤ p+b ∧ p+b ≤ c ∧
    d ≤ (p+b)^2-p^2 ∧ (p+b)^2-p^2 ≤ e)

def sourceChecks (B a c d e p : ℚ) : Prop :=
  0 ≤ B ∧ a ≤ c ∧ d ≤ e ∧
    0 ≤ p ∧ p ≤ 1 ∧ p ≤ c ∧ a ≤ p+B ∧
      a^2 ≤ e+p^2 ∧ d+p^2 ≤ c^2 ∧ d ≤ B^2+2*B*p

instance (B a c d e p : ℚ) : Decidable (sourceChecks B a c d e p) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))

def checkSource (B a c d e p : ℚ) : Bool :=
  decide (sourceChecks B (max 0 a) (min (1+B) c)
    (max 0 d) (min (B^2+2*B) e) p)

theorem checkPair_eq_true_iff (B a c d e p b : ℚ) :
    checkPair B a c d e p b = true ↔
      PairFeasible (B:ℝ) a c d e p b := by
  simp only [checkPair, decide_eq_true_eq, PairFeasible]
  norm_cast

theorem checkPair_eq_false_iff (B a c d e p b : ℚ) :
    checkPair B a c d e p b = false ↔
      ¬ PairFeasible (B:ℝ) a c d e p b := by
  rw [Bool.eq_false_iff]
  exact not_congr (checkPair_eq_true_iff B a c d e p b)

private theorem clipped_feasible_iff_checks (B a c d e p : ℝ) :
    Feasible B a c d e p ↔
      0 ≤ B ∧ max 0 a ≤ min (1+B) c ∧ max 0 d ≤ min (B^2+2*B) e ∧
        PolynomialBounds B (max 0 a) (min (1+B) c)
          (max 0 d) (min (B^2+2*B) e) p := by
  rw [← feasible_clip_iff B a c d e p]
  constructor
  · intro hp
    have hp' := hp
    obtain ⟨_, _, b, hb0, hbB, ha, hc, hd, he⟩ := hp'
    have hB := hb0.trans hbB
    exact ⟨hB, ha.trans hc, hd.trans he,
      (feasible_iff_polynomialBounds hB (le_max_left _ _) (le_max_left _ _)
        (ha.trans hc) (hd.trans he)).mp hp⟩
  · rintro ⟨hB, hac, hde, hp⟩
    exact (feasible_iff_polynomialBounds hB (le_max_left _ _) (le_max_left _ _)
      hac hde).mpr hp

theorem checkSource_eq_true_iff (B a c d e p : ℚ) :
    checkSource B a c d e p = true ↔
      Feasible (B:ℝ) a c d e p := by
  rw [clipped_feasible_iff_checks]
  simp only [checkSource, sourceChecks, PolynomialBounds]
  norm_cast
  simp

theorem checkSource_eq_false_iff (B a c d e p : ℚ) :
    checkSource B a c d e p = false ↔
      ¬ Feasible (B:ℝ) a c d e p := by
  rw [Bool.eq_false_iff]
  exact not_congr (checkSource_eq_true_iff B a c d e p)

theorem checkPair_implies_checkSource {B a c d e p b : ℚ}
    (h : checkPair B a c d e p b = true) : checkSource B a c d e p = true := by
  obtain ⟨hp0, hp1, hb0, hbB, ha, hc, hd, he⟩ := (checkPair_eq_true_iff ..).mp h
  exact (checkSource_eq_true_iff ..).mpr ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩

/-- Rational lower endpoint excluding the square-root term. -/
def linearLower (B a d : ℚ) : ℚ := max (max 0 (a-B)) ((d-B^2)/(2*B))

def positiveChecks (B a c d e : ℚ) : Prop :=
  d ≤ c^2 ∧ linearLower B a d ≤ min 1 c ∧
    (linearLower B a d)^2 ≤ c^2-d ∧ max 0 (a^2-e) ≤ (min 1 c)^2 ∧
      max 0 (a^2-e) ≤ c^2-d

instance (B a c d e : ℚ) : Decidable (positiveChecks B a c d e) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

def nonemptyChecks (B a c d e : ℚ) : Prop :=
  0 ≤ B ∧ a ≤ c ∧ d ≤ e ∧ if B = 0 then d = 0 else positiveChecks B a c d e

instance (B a c d e : ℚ) : Decidable (nonemptyChecks B a c d e) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _))

def checkNonempty (B a c d e : ℚ) : Bool :=
  decide (nonemptyChecks B (max 0 a) (min (1+B) c)
    (max 0 d) (min (B^2+2*B) e))

private theorem radical_interval_iff {L U A C : ℝ}
    (hL : 0 ≤ L) (hU : 0 ≤ U) (hC : 0 ≤ C) :
    max L (Real.sqrt A) ≤ min U (Real.sqrt C) ↔
      L ≤ U ∧ L^2 ≤ C ∧ A ≤ U^2 ∧ A ≤ C := by
  simp only [le_min_iff, max_le_iff, Real.le_sqrt hL hC,
    Real.sqrt_le_left hU, Real.sqrt_le_sqrt_iff hC]
  tauto

private theorem positive_exists_iff {B a c d e : ℝ}
    (hB : 0 < B) (ha : 0 ≤ a) (hd : 0 ≤ d) (hac : a ≤ c) (hde : d ≤ e) :
    (∃ p, Feasible B a c d e p) ↔
      d ≤ c^2 ∧ max (max 0 (a-B)) ((d-B^2)/(2*B)) ≤ min 1 c ∧
        (max (max 0 (a-B)) ((d-B^2)/(2*B)))^2 ≤ c^2-d ∧
          max 0 (a^2-e) ≤ (min 1 c)^2 ∧ max 0 (a^2-e) ≤ c^2-d := by
  rw [exists_feasible_iff hB ha hd hac hde]
  by_cases hcd : d ≤ c^2
  · simp only [hcd, true_and]
    have hshape : lower B a d e =
        max (max (max 0 (a-B)) ((d-B^2)/(2*B))) (Real.sqrt (max 0 (a^2-e))) := by
      simp only [lower, max_assoc, max_comm, max_left_comm]
    rw [hshape]
    exact radical_interval_iff ((le_max_left 0 (a-B)).trans (le_max_left _ _))
      (le_min (by norm_num) (ha.trans hac)) (sub_nonneg.mpr hcd)
  · simp [hcd]

private theorem normalized_exists_iff {B a c d e : ℝ}
    (ha : 0 ≤ a) (hd : 0 ≤ d) (hc : c ≤ 1+B) :
    (∃ p, Feasible B a c d e p) ↔
      0 ≤ B ∧ a ≤ c ∧ d ≤ e ∧ if B = 0 then d = 0 else
        d ≤ c^2 ∧ max (max 0 (a-B)) ((d-B^2)/(2*B)) ≤ min 1 c ∧
          (max (max 0 (a-B)) ((d-B^2)/(2*B)))^2 ≤ c^2-d ∧
            max 0 (a^2-e) ≤ (min 1 c)^2 ∧ max 0 (a^2-e) ≤ c^2-d := by
  constructor
  · intro h
    obtain ⟨p, hp⟩ := h
    have hp' := hp
    obtain ⟨_, _, b, hb0, hbB, hal, hcu, hdl, heu⟩ := hp'
    have hB := hb0.trans hbB
    have hac := hal.trans hcu
    have hde := hdl.trans heu
    refine ⟨hB, hac, hde, ?_⟩
    split_ifs with hz
    · subst B
      exact ((exists_feasible_zero_clipped_iff ha (by simpa using hc) hd hde).mp ⟨p, hp⟩).2
    · exact (positive_exists_iff (lt_of_le_of_ne hB (Ne.symm hz)) ha hd hac hde).mp ⟨p, hp⟩
  · rintro ⟨hB, hac, hde, h⟩
    split_ifs at h with hz
    · subst B
      exact (exists_feasible_zero_clipped_iff ha (by simpa using hc) hd hde).mpr ⟨hac, h⟩
    · exact (positive_exists_iff (lt_of_le_of_ne hB (Ne.symm hz)) ha hd hac hde).mpr h

theorem checkNonempty_eq_true_iff (B a c d e : ℚ) :
    checkNonempty B a c d e = true ↔
      ∃ p : ℝ, Feasible (B:ℝ) a c d e p := by
  have hclip : (∃ p : ℝ, Feasible (B:ℝ) a c d e p) ↔
      ∃ p : ℝ, Feasible (B:ℝ) (max 0 a) (min (1+B) c)
        (max 0 d) (min ((B:ℝ)^2+2*B) e) p := by
    exact exists_congr (fun p => (feasible_clip_iff (B:ℝ) a c d e p).symm)
  rw [hclip, normalized_exists_iff (le_max_left _ _) (le_max_left _ _) (min_le_left _ _)]
  simp only [checkNonempty, nonemptyChecks, positiveChecks, linearLower]
  norm_cast
  simp

theorem checkNonempty_eq_false_iff (B a c d e : ℚ) :
    checkNonempty B a c d e = false ↔
      ¬ ∃ p : ℝ, Feasible (B:ℝ) a c d e p := by
  rw [Bool.eq_false_iff]
  exact not_congr (checkNonempty_eq_true_iff B a c d e)

theorem checkSource_implies_checkNonempty {B a c d e p : ℚ}
    (h : checkSource B a c d e p = true) : checkNonempty B a c d e = true := by
  exact (checkNonempty_eq_true_iff ..).mpr ⟨p, (checkSource_eq_true_iff ..).mp h⟩

end CountConfidenceExecutable
