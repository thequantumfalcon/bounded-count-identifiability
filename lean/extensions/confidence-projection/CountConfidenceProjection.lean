import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Exact real interval elimination for the algebraic D=1 moment model.
The predicates state the model constraints explicitly. No sampling theorem,
distributional moment formula, or correctness of executable software is asserted.
-/

noncomputable section

namespace CountConfidenceProjection

def Feasible (B a c d e p : ℝ) : Prop :=
  0 ≤ p ∧ p ≤ 1 ∧ ∃ b : ℝ,
    0 ≤ b ∧ b ≤ B ∧ a ≤ p+b ∧ p+b ≤ c ∧
      d ≤ (p+b)^2-p^2 ∧ (p+b)^2-p^2 ≤ e

def MeanFeasible (B a c d e p : ℝ) : Prop :=
  0 ≤ p ∧ p ≤ 1 ∧ ∃ m : ℝ,
    p ≤ m ∧ m ≤ p+B ∧ a ≤ m ∧ m ≤ c ∧
      d ≤ m^2-p^2 ∧ m^2-p^2 ≤ e

def PolynomialBounds (B a c d e p : ℝ) : Prop :=
  0 ≤ p ∧ p ≤ 1 ∧ p ≤ c ∧ a ≤ p+B ∧
    a^2 ≤ e+p^2 ∧ d+p^2 ≤ c^2 ∧ d ≤ B^2+2*B*p

def lower (B a d e : ℝ) : ℝ :=
  max (max (max 0 (a-B)) (Real.sqrt (max 0 (a^2-e)))) ((d-B^2)/(2*B))

def upper (c d : ℝ) : ℝ := min (min 1 c) (Real.sqrt (c^2-d))

def meanWitness (a d p : ℝ) : ℝ := max a (max p (Real.sqrt (d+p^2)))

private theorem square_mono {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) :
    x^2 ≤ y^2 := by
  have h := mul_nonneg (sub_nonneg.mpr hxy) (show 0 ≤ y+x by linarith)
  nlinarith

theorem feasible_iff_mean (B a c d e p : ℝ) :
    Feasible B a c d e p ↔ MeanFeasible B a c d e p := by
  constructor
  · rintro ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩
    exact ⟨hp0, hp1, p+b, by linarith, by linarith, ha, hc, hd, he⟩
  · rintro ⟨hp0, hp1, m, hpm, hmB, ha, hc, hd, he⟩
    refine ⟨hp0, hp1, m-p, by linarith, by linarith, ?_, ?_, ?_, ?_⟩ <;>
      nlinarith

theorem feasible_iff_polynomialBounds {B a c d e p : ℝ}
    (hB : 0 ≤ B) (ha0 : 0 ≤ a) (hd0 : 0 ≤ d)
    (hac : a ≤ c) (hde : d ≤ e) :
    Feasible B a c d e p ↔ PolynomialBounds B a c d e p := by
  constructor
  · rintro ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩
    have hm0 : 0 ≤ p+b := add_nonneg hp0 hb0
    have ham := square_mono ha0 ha
    have hmc := square_mono hm0 hc
    have hmB := square_mono hm0 (show p+b ≤ p+B by linarith)
    exact ⟨hp0, hp1, by linarith, by linarith, by nlinarith,
      by nlinarith, by nlinarith⟩
  · rintro ⟨hp0, hp1, hpc, hapB, hae, hdc, hdB⟩
    have hc0 : 0 ≤ c := ha0.trans hac
    have he0 : 0 ≤ e := hd0.trans hde
    have hdp : 0 ≤ d+p^2 := add_nonneg hd0 (sq_nonneg p)
    have hep : 0 ≤ e+p^2 := add_nonneg he0 (sq_nonneg p)
    have hsm : Real.sqrt (d+p^2) ≤ meanWitness a d p :=
      (le_max_right p _).trans (le_max_right a _)
    have hpm : p ≤ meanWitness a d p :=
      (le_max_left p _).trans (le_max_right a _)
    have ham : a ≤ meanWitness a d p := le_max_left _ _
    have hm0 : 0 ≤ meanWitness a d p := hp0.trans hpm
    have hmc : meanWitness a d p ≤ c :=
      max_le hac (max_le hpc ((Real.sqrt_le_left hc0).mpr hdc))
    have hmB : meanWitness a d p ≤ p+B := by
      apply max_le hapB
      apply max_le (by linarith)
      apply (Real.sqrt_le_left (add_nonneg hp0 hB)).mpr
      nlinarith
    have hme : meanWitness a d p ≤ Real.sqrt (e+p^2) := by
      apply max_le (Real.le_sqrt_of_sq_le hae)
      apply max_le (Real.le_sqrt_of_sq_le (by nlinarith))
      exact Real.sqrt_le_sqrt (by linarith)
    have hsqlo := square_mono (Real.sqrt_nonneg (d+p^2)) hsm
    have hsqhi := square_mono hm0 hme
    rw [Real.sq_sqrt hdp] at hsqlo
    rw [Real.sq_sqrt hep] at hsqhi
    apply (feasible_iff_mean B a c d e p).mpr
    exact ⟨hp0, hp1, meanWitness a d p, hpm, hmB, ham, hmc,
      by nlinarith, by nlinarith⟩

theorem feasible_iff_closed_bounds {B a c d e p : ℝ}
    (hB : 0 < B) (ha0 : 0 ≤ a) (hd0 : 0 ≤ d)
    (hac : a ≤ c) (hde : d ≤ e) :
    Feasible B a c d e p ↔ d ≤ c^2 ∧ lower B a d e ≤ p ∧ p ≤ upper c d := by
  rw [feasible_iff_polynomialBounds hB.le ha0 hd0 hac hde]
  constructor
  · rintro ⟨hp0, hp1, hpc, hapB, hae, hdc, hdB⟩
    have hlow : Real.sqrt (max 0 (a^2-e)) ≤ p := by
      apply Real.sqrt_le_iff.mpr
      exact ⟨hp0, max_le (sq_nonneg p) (by nlinarith)⟩
    have hratio : (d-B^2)/(2*B) ≤ p :=
      (div_le_iff₀ (by positivity : 0 < 2*B)).mpr (by nlinarith)
    refine ⟨by nlinarith [sq_nonneg p], ?_, ?_⟩
    · exact max_le (max_le (max_le hp0 (by linarith)) hlow) hratio
    · exact le_min (le_min hp1 hpc) (Real.le_sqrt_of_sq_le (by nlinarith))
  · rintro ⟨hcd, hL, hU⟩
    simp only [lower, max_le_iff] at hL
    simp only [upper, le_min_iff] at hU
    rcases hL with ⟨⟨⟨hp0, haB⟩, hlow⟩, hratio⟩
    rcases hU with ⟨⟨hp1, hpc⟩, hu⟩
    have hmax := (Real.sqrt_le_iff.mp hlow).2
    have hae0 := (le_max_right 0 (a^2-e)).trans hmax
    have hsq := (Real.le_sqrt hp0 (sub_nonneg.mpr hcd)).mp hu
    have hr := (div_le_iff₀ (by positivity : 0 < 2*B)).mp hratio
    exact ⟨hp0, hp1, hpc, by linarith, by nlinarith, by nlinarith, by nlinarith⟩

theorem exists_feasible_iff {B a c d e : ℝ}
    (hB : 0 < B) (ha0 : 0 ≤ a) (hd0 : 0 ≤ d)
    (hac : a ≤ c) (hde : d ≤ e) :
    (∃ p, Feasible B a c d e p) ↔ d ≤ c^2 ∧ lower B a d e ≤ upper c d := by
  constructor
  · rintro ⟨p, hp⟩
    obtain ⟨hcd, hL, hU⟩ := (feasible_iff_closed_bounds hB ha0 hd0 hac hde).mp hp
    exact ⟨hcd, hL.trans hU⟩
  · rintro ⟨hcd, hLU⟩
    exact ⟨lower B a d e,
      (feasible_iff_closed_bounds hB ha0 hd0 hac hde).mpr ⟨hcd, le_rfl, hLU⟩⟩

theorem empty_of_reversed_mean {B a c d e : ℝ} (hca : c < a) :
    ¬∃ p, Feasible B a c d e p := by
  rintro ⟨p, _, _, b, _, _, ha, hc, _, _⟩
  linarith

theorem empty_of_reversed_second {B a c d e : ℝ} (hed : e < d) :
    ¬∃ p, Feasible B a c d e p := by
  rintro ⟨p, _, _, b, _, _, _, _, hd, he⟩
  linarith

theorem empty_of_sq_upper_lt_lower {B a c d e : ℝ} (hcd : c^2 < d) :
    ¬∃ p, Feasible B a c d e p := by
  rintro ⟨p, hp0, _, b, hb0, _, _, hc, hd, _⟩
  have hmc := square_mono (add_nonneg hp0 hb0) hc
  nlinarith [sq_nonneg p]

theorem feasible_zero_iff (a c d e p : ℝ) :
    Feasible 0 a c d e p ↔
      0 ≤ p ∧ p ≤ 1 ∧ a ≤ p ∧ p ≤ c ∧ d ≤ 0 ∧ 0 ≤ e := by
  constructor
  · rintro ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩
    have hb : b = 0 := le_antisymm hbB hb0
    subst b
    exact ⟨hp0, hp1, by simpa using ha, by simpa using hc,
      by simpa using hd, by simpa using he⟩
  · rintro ⟨hp0, hp1, ha, hc, hd, he⟩
    exact ⟨hp0, hp1, 0, le_rfl, le_rfl, by simpa using ha, by simpa using hc,
      by simpa using hd, by simpa using he⟩

theorem feasible_zero_clipped_iff {a c d e p : ℝ}
    (ha0 : 0 ≤ a) (hc1 : c ≤ 1) (hd0 : 0 ≤ d) (hde : d ≤ e) :
    Feasible 0 a c d e p ↔ a ≤ p ∧ p ≤ c ∧ d = 0 := by
  rw [feasible_zero_iff]
  constructor
  · rintro ⟨_, _, ha, hc, hd, _⟩
    exact ⟨ha, hc, le_antisymm hd hd0⟩
  · rintro ⟨ha, hc, hd⟩
    exact ⟨ha0.trans ha, hc.trans hc1, ha, hc, hd.le, by linarith⟩

theorem exists_feasible_zero_clipped_iff {a c d e : ℝ}
    (ha0 : 0 ≤ a) (hc1 : c ≤ 1) (hd0 : 0 ≤ d) (hde : d ≤ e) :
    (∃ p, Feasible 0 a c d e p) ↔ a ≤ c ∧ d = 0 := by
  constructor
  · rintro ⟨p, hp⟩
    obtain ⟨ha, hc, hd⟩ := (feasible_zero_clipped_iff ha0 hc1 hd0 hde).mp hp
    exact ⟨ha.trans hc, hd⟩
  · rintro ⟨hac, hd⟩
    exact ⟨a, (feasible_zero_clipped_iff ha0 hc1 hd0 hde).mpr ⟨le_rfl, hac, hd⟩⟩

theorem model_ranges {B p b : ℝ}
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hb0 : 0 ≤ b) (hbB : b ≤ B) :
    0 ≤ p+b ∧ p+b ≤ 1+B ∧
      0 ≤ (p+b)^2-p^2 ∧ (p+b)^2-p^2 ≤ B^2+2*B := by
  have hs := square_mono hb0 hbB
  have hp_b := mul_nonneg hp0 hb0
  have hbp := mul_nonneg hb0 (sub_nonneg.mpr hp1)
  exact ⟨add_nonneg hp0 hb0, by linarith, by nlinarith, by nlinarith⟩

/-- Intersecting the two moment intervals with their model ranges preserves
the exact feasible source parameters, including when clipping makes a box empty. -/
theorem feasible_clip_iff (B a c d e p : ℝ) :
    Feasible B (max 0 a) (min (1+B) c) (max 0 d) (min (B^2+2*B) e) p ↔
      Feasible B a c d e p := by
  constructor
  · rintro ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩
    exact ⟨hp0, hp1, b, hb0, hbB, (le_max_right _ _).trans ha,
      hc.trans (min_le_right _ _), (le_max_right _ _).trans hd,
      he.trans (min_le_right _ _)⟩
  · rintro ⟨hp0, hp1, b, hb0, hbB, ha, hc, hd, he⟩
    obtain ⟨hm0, hmB, hf0, hfB⟩ := model_ranges hp0 hp1 hb0 hbB
    exact ⟨hp0, hp1, b, hb0, hbB, max_le hm0 ha, le_min hmB hc,
      max_le hf0 hd, le_min hfB he⟩

theorem empty_of_negative_ceiling {B a c d e : ℝ} (hB : B < 0) :
    ¬∃ p, Feasible B a c d e p := by
  rintro ⟨p, _, _, b, hb0, hbB, _⟩
  linarith

theorem exists_feasible_positive_iff {B a c d e : ℝ}
    (hB : 0 < B) (ha0 : 0 ≤ a) (hd0 : 0 ≤ d) :
    (∃ p, Feasible B a c d e p) ↔
      a ≤ c ∧ d ≤ e ∧ d ≤ c^2 ∧ lower B a d e ≤ upper c d := by
  constructor
  · rintro h
    obtain ⟨p, hp⟩ := h
    have hp' := hp
    obtain ⟨_, _, b, _, _, ha, hc, hd, he⟩ := hp'
    have hac : a ≤ c := ha.trans hc
    have hde : d ≤ e := hd.trans he
    exact ⟨hac, hde, (exists_feasible_iff hB ha0 hd0 hac hde).mp ⟨p, hp⟩⟩
  · rintro ⟨hac, hde, hcd, hLU⟩
    exact (exists_feasible_iff hB ha0 hd0 hac hde).mpr ⟨hcd, hLU⟩

/-- The projected set is the stated closed interval; reversed endpoints
already make `Set.Icc` empty. All preliminary rejection cases are included. -/
theorem projection_positive {B a c d e : ℝ}
    (hB : 0 < B) (ha0 : 0 ≤ a) (hd0 : 0 ≤ d) :
    {p | Feasible B a c d e p} =
      if a ≤ c ∧ d ≤ e ∧ d ≤ c^2
      then Set.Icc (lower B a d e) (upper c d) else ∅ := by
  ext p
  by_cases h : a ≤ c ∧ d ≤ e ∧ d ≤ c^2
  · simp only [ite_eq_left h, Set.mem_ofPred_eq, Set.mem_Icc]
    rw [feasible_iff_closed_bounds hB ha0 hd0 h.1 h.2.1]
    exact and_iff_right h.2.2
  · simp only [ite_eq_right h, Set.mem_ofPred_eq, Set.mem_empty_iff_false, iff_false]
    rintro ⟨hp0, _, b, hb0, _, ha, hc, hd, he⟩
    apply h
    have hsq := square_mono (add_nonneg hp0 hb0) hc
    exact ⟨ha.trans hc, hd.trans he, by nlinarith [sq_nonneg p]⟩

theorem projection_zero {a c d e : ℝ}
    (ha0 : 0 ≤ a) (hc1 : c ≤ 1) (hd0 : 0 ≤ d) :
    {p | Feasible 0 a c d e p} =
      if a ≤ c ∧ d ≤ e ∧ d = 0 then Set.Icc a c else ∅ := by
  ext p
  by_cases h : a ≤ c ∧ d ≤ e ∧ d = 0
  · simp only [ite_eq_left h, Set.mem_ofPred_eq, Set.mem_Icc]
    rw [feasible_zero_clipped_iff ha0 hc1 hd0 h.2.1]
    simp only [h.2.2, and_true]
  · simp only [ite_eq_right h, Set.mem_ofPred_eq, Set.mem_empty_iff_false, iff_false]
    intro hp
    obtain ⟨_, _, ha, hc, hd, he⟩ := (feasible_zero_iff a c d e p).mp hp
    exact h ⟨ha.trans hc, hd.trans he, le_antisymm hd hd0⟩

end CountConfidenceProjection

#print axioms CountConfidenceProjection.feasible_iff_mean
#print axioms CountConfidenceProjection.feasible_iff_polynomialBounds
#print axioms CountConfidenceProjection.feasible_iff_closed_bounds
#print axioms CountConfidenceProjection.exists_feasible_iff
#print axioms CountConfidenceProjection.empty_of_reversed_mean
#print axioms CountConfidenceProjection.empty_of_reversed_second
#print axioms CountConfidenceProjection.empty_of_sq_upper_lt_lower
#print axioms CountConfidenceProjection.feasible_zero_iff
#print axioms CountConfidenceProjection.feasible_zero_clipped_iff
#print axioms CountConfidenceProjection.exists_feasible_zero_clipped_iff
#print axioms CountConfidenceProjection.model_ranges
#print axioms CountConfidenceProjection.feasible_clip_iff
#print axioms CountConfidenceProjection.empty_of_negative_ceiling
#print axioms CountConfidenceProjection.exists_feasible_positive_iff
#print axioms CountConfidenceProjection.projection_positive
#print axioms CountConfidenceProjection.projection_zero
