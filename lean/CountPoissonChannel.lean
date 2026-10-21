import CountSeriesCore

/-!
Algebraic cancellation of a fixed Poisson factorial-PGF factor exp(b*t).
The identities hold for all real b. For b >= 0 this is the usual Poisson
factorial generating series. This file does not formalize a probability-space
construction, distributional independence, or a measurement process.
-/

noncomputable section
open PowerSeries

namespace CountPoissonChannel
open CountSeriesCore

def channel (P : PowerSeries ℝ) (b : ℝ) : PowerSeries ℝ :=
  P * expShift b

theorem channel_constant (P : PowerSeries ℝ) (b : ℝ)
    (hP : constantCoeff P = 1) : constantCoeff (channel P b) = 1 := by
  simp [channel, hP]

theorem derivative_logOf_channel (P : PowerSeries ℝ) (b : ℝ)
    (hP : constantCoeff P = 1) :
    derivative (logOf (channel P b)) = derivative (logOf P) + C b := by
  have hY := channel_constant P b hP
  have hYne : channel P b ≠ 0 := by
    intro hz
    have h := congrArg (constantCoeff (R := ℝ)) hz
    rw [hY, map_zero] at h
    exact one_ne_zero h
  have hmul : derivative (logOf (channel P b)) * channel P b =
      (derivative (logOf P) + C b) * channel P b := by
    rw [derivative_logOf_mul (channel P b) hY]
    unfold channel
    rw [Derivation.leibniz, derivative_expShift, ← derivative_logOf_mul P hP]
    simp only [smul_eq_mul]
    ring
  exact mul_right_cancel₀ hYne hmul

theorem higher_factorialCumulant_channel (P : PowerSeries ℝ) (b : ℝ) (r : ℕ)
    (hP : constantCoeff P = 1) (hr : 2 ≤ r) :
    factorialCumulant (channel P b) r = factorialCumulant P r := by
  cases r with
  | zero => omega
  | succ n =>
    have hn : n ≠ 0 := by omega
    have h := congrArg (coeff n) (derivative_logOf_channel P b hP)
    rw [map_add, coeff_C_of_ne_zero hn, add_zero,
      coeff_derivative, coeff_derivative] at h
    have hcoeff := mul_right_cancel₀ (by positivity : (n : ℝ) + 1 ≠ 0) h
    unfold factorialCumulant
    rw [hcoeff]

theorem first_factorialCumulant_channel (P : PowerSeries ℝ) (b : ℝ)
    (hP : constantCoeff P = 1) :
    factorialCumulant (channel P b) 1 = factorialCumulant P 1 + b := by
  have h := congrArg (coeff 0) (derivative_logOf_channel P b hP)
  rw [map_add, coeff_derivative, coeff_derivative, coeff_zero_C] at h
  simpa [factorialCumulant] using h

theorem bounded_sources_identified_under_unknown_factors
    (D : ℕ) (P Q : PowerSeries ℝ) (bP bQ : ℝ)
    (hP0 : constantCoeff P = 1) (hQ0 : constantCoeff Q = 1)
    (hP : ∀ j, 0 ≤ coeff j P) (hQ : ∀ j, 0 ≤ coeff j Q)
    (hPdegree : ∀ n, D < n → coeff n P = 0)
    (hQdegree : ∀ n, D < n → coeff n Q = 0)
    (hobserved : ∀ r, 2 ≤ r → r ≤ D + 1 →
      factorialCumulant (channel P bP) r = factorialCumulant (channel Q bQ) r) :
    P = Q := by
  apply bounded_nonnegative_series_identified D P Q hP0 hQ0 hP hQ hPdegree hQdegree
  intro r hr hD
  have h := hobserved r hr hD
  rw [higher_factorialCumulant_channel P bP r hP0 hr,
      higher_factorialCumulant_channel Q bQ r hQ0 hr] at h
  exact h

end CountPoissonChannel

#print axioms CountPoissonChannel.derivative_logOf_channel
#print axioms CountPoissonChannel.higher_factorialCumulant_channel
#print axioms CountPoissonChannel.first_factorialCumulant_channel
#print axioms CountPoissonChannel.bounded_sources_identified_under_unknown_factors
