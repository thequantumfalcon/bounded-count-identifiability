import CountSeriesCore
import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas

noncomputable section
open scoped Topology

namespace CountTaylorJetFoundation

/-- The formal series of normalized, totalized iterated derivatives at zero.
This definition alone makes no convergence or analyticity assertion. -/
def jet0 (f : ℝ → ℝ) : PowerSeries ℝ :=
  PowerSeries.mk (fun n => iteratedDeriv n f 0 / (Nat.factorial n : ℝ))

@[simp] theorem coeff_jet0 (f : ℝ → ℝ) (n : ℕ) :
    PowerSeries.coeff n (jet0 f) = iteratedDeriv n f 0 / (Nat.factorial n : ℝ) := by
  simp [jet0]

theorem derivative_jet0 (f : ℝ → ℝ) :
    PowerSeries.derivative (jet0 f) = jet0 (deriv f) := by
  ext n
  rw [PowerSeries.coeff_derivative, coeff_jet0, coeff_jet0]
  rw [iteratedDeriv_succ', Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  have hn : (n : ℝ) + 1 ≠ 0 := by positivity
  have hf : (Nat.factorial n : ℝ) ≠ 0 := by positivity
  field_simp

theorem jet0_congr_eventuallyEq {f g : ℝ → ℝ} (h : f =ᶠ[𝓝 0] g) :
    jet0 f = jet0 g := by
  ext n
  rw [coeff_jet0, coeff_jet0, h.iteratedDeriv_eq n]

end CountTaylorJetFoundation

#print axioms CountTaylorJetFoundation.coeff_jet0
#print axioms CountTaylorJetFoundation.derivative_jet0
#print axioms CountTaylorJetFoundation.jet0_congr_eventuallyEq
