import CountTaylorJetFoundation

noncomputable section
open scoped BigOperators Topology
open CountTaylorJetFoundation

namespace CountTaylorJetProduct

/-- Smooth germs at zero have multiplicative normalized formal derivative jets.
This identity does not assert convergence of the resulting formal series. -/
theorem jet0_mul {f g : ℝ → ℝ}
    (hf : ContDiffAt ℝ ⊤ f 0) (hg : ContDiffAt ℝ ⊤ g 0) :
    jet0 (fun x => f x * g x) = jet0 f * jet0 g := by
  ext n
  rw [coeff_jet0, PowerSeries.coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  have hfn : ContDiffAt ℝ n f 0 := hf.of_le le_top
  have hgn : ContDiffAt ℝ n g 0 := hg.of_le le_top
  rw [iteratedDeriv_fun_mul hfn hgn, div_eq_mul_inv, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i hi
  have hin : i ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hi)
  rw [coeff_jet0, coeff_jet0]
  have hchoose : (n.choose i : ℝ) * (i.factorial : ℝ) * ((n-i).factorial : ℝ) =
      (n.factorial : ℝ) := by
    exact_mod_cast Nat.choose_mul_factorial_mul_factorial hin
  have hfi : (i.factorial : ℝ) ≠ 0 := by positivity
  have hfj : ((n-i).factorial : ℝ) ≠ 0 := by positivity
  have hfnz : (n.factorial : ℝ) ≠ 0 := by positivity
  field_simp
  rw [← hchoose]
  ring

end CountTaylorJetProduct

#print axioms CountTaylorJetProduct.jet0_mul
