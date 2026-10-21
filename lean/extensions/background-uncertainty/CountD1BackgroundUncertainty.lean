import CountD1Stability

/-!
Deterministic stability with an additive second-cumulant perturbation.
The interpretation as a mixing-rate variance is a separate probability argument.
No finite-sample coverage or physical calibration is asserted here.
-/

noncomputable section
namespace CountD1BackgroundUncertainty

def perturbedSecond (p v : ℝ) : ℝ := -(p ^ 2) + v

theorem perturbation_difference_le (v w η : ℝ)
    (hv0 : 0 ≤ v) (hv : v ≤ η) (hw0 : 0 ≤ w) (hw : w ≤ η) :
    |v - w| ≤ η := by
  rw [abs_le]
  constructor <;> linarith

theorem square_difference_le (p q v w η : ℝ)
    (hv0 : 0 ≤ v) (hv : v ≤ η) (hw0 : 0 ≤ w) (hw : w ≤ η) :
    |p ^ 2 - q ^ 2| ≤ |perturbedSecond p v - perturbedSecond q w| + η := by
  have hid : p ^ 2 - q ^ 2 =
      (v - w) - (perturbedSecond p v - perturbedSecond q w) := by
    unfold perturbedSecond
    ring
  rw [hid]
  have h := abs_sub (v - w) (perturbedSecond p v - perturbedSecond q w)
  have hb := perturbation_difference_le v w η hv0 hv hw0 hw
  linarith

theorem parameter_error_le (p q v w η : ℝ)
    (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hv0 : 0 ≤ v) (hv : v ≤ η) (hw0 : 0 ≤ w) (hw : w ≤ η) :
    |p - q| ≤ Real.sqrt (|perturbedSecond p v - perturbedSecond q w| + η) := by
  exact (CountD1Stability.parameter_error_le_sqrt p q hp hq).trans
    (Real.sqrt_le_sqrt (square_difference_le p q v w η hv0 hv hw0 hw))

theorem bounded_observation_error (μ ν p q v w η ε δ : ℝ)
    (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hv0 : 0 ≤ v) (hv : v ≤ η) (hw0 : 0 ≤ w) (hw : w ≤ η)
    (hκ : |perturbedSecond p v - perturbedSecond q w| ≤ ε)
    (hμ : |μ - ν| ≤ δ) :
    |p - q| ≤ Real.sqrt (ε + η) ∧
    |CountD1Stability.backgroundFromMean μ p -
      CountD1Stability.backgroundFromMean ν q| ≤ δ + Real.sqrt (ε + η) := by
  have hparam : |p - q| ≤ Real.sqrt (ε + η) :=
    (parameter_error_le p q v w η hp hq hv0 hv hw0 hw).trans
      (Real.sqrt_le_sqrt (add_le_add hκ (le_refl η)))
  constructor
  · exact hparam
  · calc
      |CountD1Stability.backgroundFromMean μ p -
        CountD1Stability.backgroundFromMean ν q| = |(μ - ν) - (p - q)| := by
          unfold CountD1Stability.backgroundFromMean
          congr 1
          ring
      _ ≤ |μ - ν| + |p - q| := abs_sub _ _
      _ ≤ δ + Real.sqrt (ε + η) := add_le_add hμ hparam

theorem equal_cumulant_witness (h : ℝ) (hh : 0 ≤ h) :
    perturbedSecond h (h ^ 2) = perturbedSecond 0 0 ∧
    h + h = 0 + (2 * h) ∧ |h - 0| = h ∧ Real.sqrt (h ^ 2) = h := by
  constructor
  · simp [perturbedSecond]
  constructor
  · ring
  · simp [Real.sqrt_sq_eq_abs, abs_of_nonneg hh]

end CountD1BackgroundUncertainty

#print axioms CountD1BackgroundUncertainty.perturbation_difference_le
#print axioms CountD1BackgroundUncertainty.square_difference_le
#print axioms CountD1BackgroundUncertainty.parameter_error_le
#print axioms CountD1BackgroundUncertainty.bounded_observation_error
#print axioms CountD1BackgroundUncertainty.equal_cumulant_witness
