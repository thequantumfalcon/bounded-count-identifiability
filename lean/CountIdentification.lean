import CountLawEncoding
import CountSeriesCore

/-!
Identification of bounded nonnegative integer probability laws by their
factorial cumulants of orders 2 through D+1. Cumulants are defined by the
formal logarithm of the factorial probability generating polynomial.
No sampling, detector calibration, or physical hypothesis is asserted here.
-/

noncomputable section
open scoped BigOperators
open Polynomial

namespace BoundedCountLaw

def IsBoundedLaw (D : ℕ) (p : ℕ → ℝ) : Prop :=
  (∀ n, 0 ≤ p n) ∧
  (∑ n ∈ Finset.range (D+1), p n = 1) ∧
  (∀ n, D < n → p n = 0)

def lawFactorialCumulant (D : ℕ) (p : ℕ → ℝ) (r : ℕ) : ℝ :=
  CountSeriesCore.factorialCumulant (factorialPGF D p : PowerSeries ℝ) r

theorem higher_factorial_cumulants_identify (D : ℕ) (p q : ℕ → ℝ)
    (hp : IsBoundedLaw D p) (hq : IsBoundedLaw D q)
    (hc : ∀ r, 2 ≤ r → r ≤ D+1 →
      lawFactorialCumulant D p r = lawFactorialCumulant D q r) :
    p = q := by
  have hseries : (factorialPGF D p : PowerSeries ℝ) =
      (factorialPGF D q : PowerSeries ℝ) := by
    apply CountSeriesCore.bounded_nonnegative_series_identified D
    · simpa only [Polynomial.constantCoeff_coe] using factorialPGF_constant D p hp.2.1
    · simpa only [Polynomial.constantCoeff_coe] using factorialPGF_constant D q hq.2.1
    · intro n
      simpa only [Polynomial.coeff_coe] using
        factorialPGF_coeff_nonneg D n p (fun k _ => hp.1 k)
    · intro n
      simpa only [Polynomial.coeff_coe] using
        factorialPGF_coeff_nonneg D n q (fun k _ => hq.1 k)
    · intro n hn
      simpa only [Polynomial.coeff_coe] using factorialPGF_coeff_above D n p hn
    · intro n hn
      simpa only [Polynomial.coeff_coe] using factorialPGF_coeff_above D n q hn
    · exact hc
  have hpoly : factorialPGF D p = factorialPGF D q :=
    Polynomial.coe_injective ℝ hseries
  funext n
  by_cases hn : n ≤ D
  · exact factorialPGF_injective_on_support D p q hpoly n hn
  · rw [hp.2.2 n (Nat.lt_of_not_ge hn), hq.2.2 n (Nat.lt_of_not_ge hn)]

end BoundedCountLaw

#print axioms BoundedCountLaw.higher_factorial_cumulants_identify
