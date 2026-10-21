import CountIdentification
import CountPoissonChannel

/-!
Bounded-law identification under a formal exponential background factor.
For a fixed nonnegative b, exp(b*t) is the Poisson factorial-PGF factor.
The product models independent addition. The probability-space derivation
of that product and validation of an experimental count model are outside
this formalization. All identities below are algebraic and hold for real b.
-/

noncomputable section
open scoped BigOperators
open Polynomial

namespace BoundedCountLaw

def observedFactorialCumulant (D : ℕ) (p : ℕ → ℝ) (b : ℝ) (r : ℕ) : ℝ :=
  CountSeriesCore.factorialCumulant
    (CountPoissonChannel.channel (factorialPGF D p : PowerSeries ℝ) b) r

theorem first_law_cumulant_eq_mean (D : ℕ) (p : ℕ → ℝ)
    (hp : IsBoundedLaw D p) :
    lawFactorialCumulant D p 1 = ∑ n ∈ Finset.range (D+1), p n * n := by
  have hzero : PowerSeries.constantCoeff (factorialPGF D p : PowerSeries ℝ) = 1 := by
    simpa only [Polynomial.constantCoeff_coe] using factorialPGF_constant D p hp.2.1
  unfold lawFactorialCumulant CountSeriesCore.factorialCumulant
  rw [CountSeriesCore.coeff_one_logOf _ hzero, Polynomial.coeff_coe,
    factorialPGF_coeff]
  simp

theorem observed_higher_cumulant_eq (D : ℕ) (p : ℕ → ℝ) (b : ℝ) (r : ℕ)
    (hp : IsBoundedLaw D p) (hr : 2 ≤ r) :
    observedFactorialCumulant D p b r = lawFactorialCumulant D p r := by
  apply CountPoissonChannel.higher_factorialCumulant_channel
  · simpa only [Polynomial.constantCoeff_coe] using factorialPGF_constant D p hp.2.1
  · exact hr

theorem observed_higher_cumulants_identify_source (D : ℕ) (p q : ℕ → ℝ)
    (bP bQ : ℝ) (hp : IsBoundedLaw D p) (hq : IsBoundedLaw D q)
    (hc : ∀ r, 2 ≤ r → r ≤ D+1 →
      observedFactorialCumulant D p bP r = observedFactorialCumulant D q bQ r) :
    p = q := by
  apply higher_factorial_cumulants_identify D p q hp hq
  intro r hr hD
  have h := hc r hr hD
  rw [observed_higher_cumulant_eq D p bP r hp hr,
    observed_higher_cumulant_eq D q bQ r hq hr] at h
  exact h

theorem observed_first_cumulant_eq (D : ℕ) (p : ℕ → ℝ) (b : ℝ)
    (hp : IsBoundedLaw D p) :
    observedFactorialCumulant D p b 1 = lawFactorialCumulant D p 1 + b := by
  apply CountPoissonChannel.first_factorialCumulant_channel
  simpa only [Polynomial.constantCoeff_coe] using factorialPGF_constant D p hp.2.1

theorem observed_cumulants_identify_source_and_background (D : ℕ) (p q : ℕ → ℝ)
    (bP bQ : ℝ) (hp : IsBoundedLaw D p) (hq : IsBoundedLaw D q)
    (hc : ∀ r, 1 ≤ r → r ≤ D+1 →
      observedFactorialCumulant D p bP r = observedFactorialCumulant D q bQ r) :
    p = q ∧ bP = bQ := by
  have hpq : p = q := observed_higher_cumulants_identify_source D p q bP bQ hp hq
    (fun r hr hD => hc r (by omega) hD)
  refine ⟨hpq, ?_⟩
  have h := hc 1 (by omega) (by omega)
  rw [observed_first_cumulant_eq D p bP hp,
    observed_first_cumulant_eq D q bQ hq, hpq] at h
  exact add_left_cancel h

end BoundedCountLaw

#print axioms BoundedCountLaw.first_law_cumulant_eq_mean
#print axioms BoundedCountLaw.observed_higher_cumulants_identify_source
#print axioms BoundedCountLaw.observed_cumulants_identify_source_and_background
