import Mathlib
import CountSeriesCore
import CountIdentification

/-! Finite coefficient perturbation for normalized formal logarithms.
No convergence of a logarithmic series is assumed. -/
noncomputable section
open scoped BigOperators
open PowerSeries

namespace CountQuantitativeJets

theorem ode_coefficient_stability (N : ℕ) (a b u v : ℕ → ℝ)
    (ε C L : ℝ) (hε : 0 ≤ ε) (hC : 0 ≤ C) (hL : 0 ≤ L)
    (hzero : a 0 = b 0)
    (ha : ∀ k < N, ((k : ℝ) + 1) * a (k + 1) =
      ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k, a p.1 * u p.2)
    (hb : ∀ k < N, ((k : ℝ) + 1) * b (k + 1) =
      ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k, b p.1 * v p.2)
    (hbC : ∀ k ≤ N, |b k| ≤ C)
    (huL : ∀ k < N, |u k| ≤ L)
    (huv : ∀ k < N, |u k - v k| ≤ ε) :
    ∀ n ≤ N, |a n - b n| ≤ ε * C * (L + 1) ^ n := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro hn
    cases n with
    | zero => simp only [hzero, sub_self, abs_zero, pow_zero, mul_one]; positivity
    | succ k =>
      have hk : k < N := by omega
      have hK : 1 ≤ L + 1 := by linarith
      have hEC : 0 ≤ ε * C := mul_nonneg hε hC
      have hpow : 1 ≤ (L + 1) ^ k := one_le_pow₀ hK
      have hrec : ((k : ℝ) + 1) * (a (k + 1) - b (k + 1)) =
          ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k,
            ((a p.1 - b p.1) * u p.2 + b p.1 * (u p.2 - v p.2)) := by
        rw [mul_sub, ha k hk, hb k hk, ← Finset.sum_sub_distrib]
        apply Finset.sum_congr rfl
        intro p hp
        ring
      have hterm : ∀ p ∈ Finset.HasAntidiagonal.antidiagonal k,
          |(a p.1 - b p.1) * u p.2 + b p.1 * (u p.2 - v p.2)| ≤
            ε * C * (L + 1) ^ k * L + C * ε := by
        intro p hp
        have hs : p.1 + p.2 = k := Finset.HasAntidiagonal.mem_antidiagonal.mp hp
        have he : |a p.1 - b p.1| ≤ ε * C * (L + 1) ^ k :=
          (ih p.1 (by omega) (by omega)).trans
            (mul_le_mul_of_nonneg_left (pow_le_pow_right₀ hK (by omega)) hEC)
        calc
          |(a p.1 - b p.1) * u p.2 + b p.1 * (u p.2 - v p.2)| ≤
              |(a p.1 - b p.1) * u p.2| + |b p.1 * (u p.2 - v p.2)| := abs_add_le _ _
          _ = |a p.1 - b p.1| * |u p.2| + |b p.1| * |u p.2 - v p.2| := by rw [abs_mul, abs_mul]
          _ ≤ ε * C * (L + 1) ^ k * L + C * ε :=
            add_le_add (mul_le_mul he (huL p.2 (by omega)) (abs_nonneg _) (by positivity))
              (mul_le_mul (hbC p.1 (by omega)) (huv p.2 (by omega)) (abs_nonneg _) hC)
      have hsum : ((k : ℝ) + 1) * |a (k + 1) - b (k + 1)| ≤
          ((k : ℝ) + 1) * (ε * C * (L + 1) ^ k * L + C * ε) := by
        calc
          ((k : ℝ) + 1) * |a (k + 1) - b (k + 1)| =
              |((k : ℝ) + 1) * (a (k + 1) - b (k + 1))| := by
                rw [abs_mul, abs_of_nonneg (by positivity : 0 ≤ (k : ℝ) + 1)]
          _ ≤ ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k,
              |(a p.1 - b p.1) * u p.2 + b p.1 * (u p.2 - v p.2)| := by
                rw [hrec]
                exact Finset.abs_sum_le_sum_abs _ _
          _ ≤ ∑ _p ∈ Finset.HasAntidiagonal.antidiagonal k, (ε * C * (L + 1) ^ k * L + C * ε) :=
                Finset.sum_le_sum hterm
          _ = ((k : ℝ) + 1) * (ε * C * (L + 1) ^ k * L + C * ε) := by
                simp [Finset.Nat.card_antidiagonal, nsmul_eq_mul]
                ring
      have he : |a (k + 1) - b (k + 1)| ≤ ε * C * (L + 1) ^ k * L + C * ε := by
        by_contra hnot
        have hpos := mul_pos (by positivity : 0 < (k : ℝ) + 1)
          (sub_pos.mpr (lt_of_not_ge hnot))
        nlinarith
      calc
        |a (k + 1) - b (k + 1)| ≤ ε * C * (L + 1) ^ k * L + C * ε := he
        _ ≤ ε * C * (L + 1) ^ (k + 1) := by
          rw [pow_succ]
          nlinarith [mul_nonneg hEC (sub_nonneg.mpr hpow)]

theorem log_derivative_coefficient_bound (N : ℕ) (a u : ℕ → ℝ)
    (M K : ℝ) (hM : 0 ≤ M) (hK : 1 ≤ K)
    (hKM : 2 * ((N : ℝ) + 1) * M ≤ K)
    (hzero : a 0 = 1)
    (ha : ∀ k < N, ((k : ℝ) + 1) * a (k + 1) =
      ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k, a p.1 * u p.2)
    (haM : ∀ k ≤ N, |a k| ≤ M) :
    ∀ k < N, |u k| ≤ K ^ (k + 1) := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro hk
    have hK0 : 0 ≤ K := le_trans (by norm_num) hK
    have hpow : 1 ≤ K ^ k := one_le_pow₀ hK
    have hmem : (0, k) ∈ Finset.HasAntidiagonal.antidiagonal k := by simp
    have hsum := Finset.sum_erase_add (Finset.HasAntidiagonal.antidiagonal k)
      (fun p : ℕ × ℕ => a p.1 * u p.2) hmem
    simp only [hzero, one_mul] at hsum
    have hueq : u k = ((k : ℝ) + 1) * a (k + 1) -
        ∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), a p.1 * u p.2 := by
      linarith [ha k hk]
    have hrest : |∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), a p.1 * u p.2| ≤
        ((N : ℝ) + 1) * M * K ^ k := by
      calc
        |∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), a p.1 * u p.2| ≤
            ∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), |a p.1 * u p.2| :=
          Finset.abs_sum_le_sum_abs _ _
        _ ≤ ∑ _p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), M * K ^ k := by
          apply Finset.sum_le_sum
          intro p hp
          have hpne := (Finset.mem_erase.mp hp).1
          have hs : p.1 + p.2 = k := Finset.HasAntidiagonal.mem_antidiagonal.mp (Finset.mem_erase.mp hp).2
          have hp1 : 0 < p.1 := by
            by_contra hnot
            have hz : p.1 = 0 := by omega
            apply hpne
            ext <;> simp <;> omega
          have hi : |u p.2| ≤ K ^ k :=
            (ih p.2 (by omega) (by omega)).trans (pow_le_pow_right₀ hK (by omega))
          rw [abs_mul]
          exact mul_le_mul (haM p.1 (by omega)) hi (abs_nonneg _) hM
        _ ≤ ∑ _p ∈ Finset.HasAntidiagonal.antidiagonal k, M * K ^ k :=
          Finset.sum_le_sum_of_subset_of_nonneg (Finset.erase_subset _ _)
            (fun _ _ _ => mul_nonneg hM (pow_nonneg hK0 k))
        _ = ((k : ℝ) + 1) * M * K ^ k := by
          simp [Finset.Nat.card_antidiagonal, nsmul_eq_mul]
          ring
        _ ≤ ((N : ℝ) + 1) * M * K ^ k := by
          apply mul_le_mul_of_nonneg_right _ (pow_nonneg hK0 k)
          apply mul_le_mul_of_nonneg_right _ hM
          exact_mod_cast Nat.add_le_add_right (Nat.le_of_lt hk) 1
    have hfirst : |((k : ℝ) + 1) * a (k + 1)| ≤ ((N : ℝ) + 1) * M * K ^ k := by
      rw [abs_mul, abs_of_nonneg (by positivity : 0 ≤ (k : ℝ) + 1)]
      calc
        ((k : ℝ) + 1) * |a (k + 1)| ≤ ((k : ℝ) + 1) * M :=
          mul_le_mul_of_nonneg_left (haM (k + 1) (by omega)) (by positivity)
        _ ≤ ((N : ℝ) + 1) * M := by
          apply mul_le_mul_of_nonneg_right _ hM
          exact_mod_cast Nat.add_le_add_right (Nat.le_of_lt hk) 1
        _ ≤ ((N : ℝ) + 1) * M * K ^ k := by
          have ht : 0 ≤ ((N : ℝ) + 1) * M := mul_nonneg (by positivity) hM
          nlinarith [mul_nonneg ht (sub_nonneg.mpr hpow)]
    calc
      |u k| ≤ |((k : ℝ) + 1) * a (k + 1)| +
          |∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), a p.1 * u p.2| := by
        conv_lhs => rw [hueq, sub_eq_add_neg]
        simpa only [abs_neg] using abs_add_le (((k : ℝ) + 1) * a (k + 1))
          (-(∑ p ∈ (Finset.HasAntidiagonal.antidiagonal k).erase (0, k), a p.1 * u p.2))
      _ ≤ 2 * ((N : ℝ) + 1) * M * K ^ k := by linarith
      _ ≤ K ^ (k + 1) := by
        rw [pow_succ]
        nlinarith [mul_nonneg (sub_nonneg.mpr hKM) (pow_nonneg hK0 k)]

theorem normalized_log_recurrence (P : PowerSeries ℝ) (hP : constantCoeff P = 1) (k : ℕ) :
    ((k : ℝ) + 1) * coeff (k + 1) P =
      ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k,
        coeff p.1 P * coeff p.2 (derivative (logOf P)) := by
  have h := congrArg (coeff k) (CountSeriesCore.derivative_logOf_mul P hP)
  rw [mul_comm (derivative (logOf P)) P, coeff_mul, coeff_derivative] at h
  simpa only [mul_comm] using h.symm

theorem normalized_log_bound (N : ℕ) (P : PowerSeries ℝ) (M K : ℝ)
    (hM : 0 ≤ M) (hK : 1 ≤ K) (hKM : 2 * ((N : ℝ) + 1) * M ≤ K)
    (hP : constantCoeff P = 1) (hcoeff : ∀ k ≤ N, |coeff k P| ≤ M) :
    ∀ k < N, |coeff k (derivative (logOf P))| ≤ K ^ N := by
  intro k hk
  have h := log_derivative_coefficient_bound N (fun i => coeff i P)
    (fun i => coeff i (derivative (logOf P))) M K hM hK hKM
    (by simpa only [coeff_zero_eq_constantCoeff_apply] using hP)
    (fun i _ => normalized_log_recurrence P hP i) hcoeff k hk
  exact h.trans (pow_le_pow_right₀ hK (by omega))

theorem shifted_coefficient_nonnegative (Q : PowerSeries ℝ) (c : ℝ)
    (hq : ∀ j, 0 ≤ coeff j Q) (hc : 0 ≤ c) (n : ℕ) :
    0 ≤ coeff n (Q * CountSeriesCore.expShift c) := by
  rw [coeff_mul]
  apply Finset.sum_nonneg
  intro p hp
  rw [CountSeriesCore.coeff_expShift]
  exact mul_nonneg (hq p.1) (div_nonneg (pow_nonneg hc _) (Nat.cast_nonneg _))

theorem shifted_coefficient_bound (N : ℕ) (Q : PowerSeries ℝ) (c M : ℝ)
    (hM : 0 ≤ M) (hc : 0 ≤ c) (hcM : c ≤ M)
    (hq : ∀ j, 0 ≤ coeff j Q) (hqM : ∀ j ≤ N, coeff j Q ≤ M) :
    ∀ n ≤ N, |coeff n (Q * CountSeriesCore.expShift c)| ≤
      ((N : ℝ) + 1) * M * (M + 1) ^ N := by
  intro n hn
  rw [abs_of_nonneg (shifted_coefficient_nonnegative Q c hq hc n), coeff_mul]
  calc
    (∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
        coeff p.1 Q * coeff p.2 (CountSeriesCore.expShift c)) ≤
        ∑ _p ∈ Finset.HasAntidiagonal.antidiagonal n, M * (M + 1) ^ N := by
      apply Finset.sum_le_sum
      intro p hp
      have hs : p.1 + p.2 = n := Finset.HasAntidiagonal.mem_antidiagonal.mp hp
      rw [CountSeriesCore.coeff_expShift]
      have hpw : c ^ p.2 ≤ (M + 1) ^ N :=
        (pow_le_pow_left₀ hc (by linarith : c ≤ M + 1) _).trans
          (pow_le_pow_right₀ (by linarith : 1 ≤ M + 1) (by omega))
      have hf : (1 : ℝ) ≤ (Nat.factorial p.2 : ℝ) := by exact_mod_cast Nat.factorial_pos p.2
      have hdiv : c ^ p.2 / (Nat.factorial p.2 : ℝ) ≤ (M + 1) ^ N := by
        apply (div_le_iff₀ (by positivity : (0 : ℝ) < (Nat.factorial p.2 : ℝ))).mpr
        nlinarith [mul_nonneg (pow_nonneg (by linarith : 0 ≤ M + 1) N) (sub_nonneg.mpr hf)]
      exact mul_le_mul (hqM p.1 (by omega)) hdiv
        (div_nonneg (pow_nonneg hc _) (Nat.cast_nonneg _)) hM
    _ = ((n : ℝ) + 1) * M * (M + 1) ^ N := by
      simp [Finset.Nat.card_antidiagonal, nsmul_eq_mul]
      ring
    _ ≤ ((N : ℝ) + 1) * M * (M + 1) ^ N := by
      apply mul_le_mul_of_nonneg_right _ (pow_nonneg (by linarith : 0 ≤ M + 1) N)
      apply mul_le_mul_of_nonneg_right _ hM
      exact_mod_cast Nat.add_le_add_right hn 1

theorem shifted_recurrence (Q : PowerSeries ℝ) (hQ : constantCoeff Q = 1) (c : ℝ) (k : ℕ) :
    ((k : ℝ) + 1) * coeff (k + 1) (Q * CountSeriesCore.expShift c) =
      ∑ p ∈ Finset.HasAntidiagonal.antidiagonal k,
        coeff p.1 (Q * CountSeriesCore.expShift c) *
          coeff p.2 (derivative (logOf Q) + C c) := by
  have hQode : derivative Q = Q * derivative (logOf Q) := by
    rw [mul_comm]
    exact (CountSeriesCore.derivative_logOf_mul Q hQ).symm
  have hode : derivative (Q * CountSeriesCore.expShift c) =
      (Q * CountSeriesCore.expShift c) * (derivative (logOf Q) + C c) := by
    rw [Derivation.leibniz, hQode, CountSeriesCore.derivative_expShift]
    simp only [smul_eq_mul]
    ring
  have h := congrArg (coeff k) hode
  rw [coeff_derivative, coeff_mul k] at h
  simpa only [mul_comm] using h

def shiftCap (N : ℕ) (M : ℝ) : ℝ := ((N : ℝ) + 1) * M * (M + 1) ^ N
def logBase (N : ℕ) (M : ℝ) : ℝ := 2 * ((N : ℝ) + 1) * M + 1
def jetConstant (N : ℕ) (M : ℝ) : ℝ :=
  (N : ℝ) * shiftCap N M * ((logBase N M) ^ N + 1) ^ N

theorem support_power_bound (N d : ℕ) (P Q : PowerSeries ℝ) (M ε η c : ℝ)
    (hd : d < N) (hM : 0 ≤ M) (hε : 0 ≤ ε) (hη : 0 < η)
    (hP : constantCoeff P = 1) (hQ : constantCoeff Q = 1)
    (hPcoeff : ∀ j ≤ N, |coeff j P| ≤ M)
    (hQcoeff : ∀ j ≤ N, coeff j Q ≤ M) (hQnonneg : ∀ j, 0 ≤ coeff j Q)
    (hPtop : coeff N P = 0) (hηQ : η ≤ coeff d Q)
    (hc : 0 ≤ c) (hcM : c ≤ M)
    (hcdef : c = coeff 1 (logOf P) - coeff 1 (logOf Q))
    (hlog : ∀ r, 2 ≤ r → r ≤ N → |coeff r (logOf P) - coeff r (logOf Q)| ≤ ε) :
    c ^ (N - d) ≤ (Nat.factorial (N - d) : ℝ) * jetConstant N M * ε / η := by
  let K := logBase N M
  let L := K ^ N
  let B := shiftCap N M
  have hK : 1 ≤ K := by
    dsimp [K, logBase]
    have hp : 0 ≤ 2 * ((N : ℝ) + 1) * M := by positivity
    linarith
  have hKM : 2 * ((N : ℝ) + 1) * M ≤ K := by dsimp [K, logBase]; linarith
  have hL : 0 ≤ L := pow_nonneg (le_trans (by norm_num) hK) N
  have hB : 0 ≤ B := by dsimp [B, shiftCap]; positivity
  have hU : ∀ k < N, |coeff k (derivative (logOf P))| ≤ L :=
    normalized_log_bound N P M K hM hK hKM hP hPcoeff
  have hdiff : ∀ k < N, |coeff k (derivative (logOf P)) -
      coeff k (derivative (logOf Q) + C c)| ≤ (N : ℝ) * ε := by
    intro k hk
    by_cases hk0 : k = 0
    · subst k
      simp only [map_add, coeff_derivative, Nat.cast_zero, zero_add, mul_one, coeff_zero_C]
      have he : coeff 1 (logOf P) - (coeff 1 (logOf Q) + c) = 0 := by rw [hcdef]; ring
      rw [he, abs_zero]
      positivity
    · simp only [map_add, coeff_C_of_ne_zero hk0, add_zero, coeff_derivative]
      rw [← sub_mul, abs_mul, abs_of_nonneg (by positivity : 0 ≤ (k : ℝ) + 1)]
      calc
        |coeff (k + 1) (logOf P) - coeff (k + 1) (logOf Q)| * ((k : ℝ) + 1) ≤
            ε * ((k : ℝ) + 1) := mul_le_mul_of_nonneg_right (hlog (k + 1) (by omega) (by omega)) (by positivity)
        _ ≤ ε * (N : ℝ) := by
          apply mul_le_mul_of_nonneg_left _ hε
          exact_mod_cast hk
        _ = (N : ℝ) * ε := by ring
  have herr := ode_coefficient_stability N (fun j => coeff j P)
    (fun j => coeff j (Q * CountSeriesCore.expShift c))
    (fun j => coeff j (derivative (logOf P)))
    (fun j => coeff j (derivative (logOf Q) + C c))
    ((N : ℝ) * ε) B L (mul_nonneg (Nat.cast_nonneg _) hε) hB hL
    (by simp [coeff_zero_eq_constantCoeff_apply, hP, hQ])
    (fun j _ => normalized_log_recurrence P hP j)
    (fun j _ => shifted_recurrence Q hQ c j)
    (shifted_coefficient_bound N Q c M hM hc hcM hQnonneg hQcoeff) hU hdiff N le_rfl
  have hA0 := shifted_coefficient_nonnegative Q c hQnonneg hc N
  have hA : coeff N (Q * CountSeriesCore.expShift c) ≤ (N : ℝ) * ε * B * (L + 1) ^ N := by
    simpa only [hPtop, zero_sub, abs_neg, abs_of_nonneg hA0] using herr
  have hsel : coeff d Q * c ^ (N - d) / (Nat.factorial (N - d) : ℝ) ≤
      coeff N (Q * CountSeriesCore.expShift c) := by
    rw [coeff_mul]
    have hm : (d, N - d) ∈ Finset.HasAntidiagonal.antidiagonal N := by simp; omega
    have ht := Finset.single_le_sum
      (f := fun p : ℕ × ℕ => coeff p.1 Q * coeff p.2 (CountSeriesCore.expShift c))
      (s := Finset.HasAntidiagonal.antidiagonal N) (a := (d, N - d))
      (fun p _ => by
        rw [CountSeriesCore.coeff_expShift]
        exact mul_nonneg (hQnonneg p.1)
          (div_nonneg (pow_nonneg hc p.2) (Nat.cast_nonneg _))) hm
    simpa only [CountSeriesCore.coeff_expShift, mul_div_assoc] using ht
  have hf : (0 : ℝ) < (Nat.factorial (N - d) : ℝ) := by positivity
  have ht := (div_le_iff₀ hf).mp hsel
  apply (le_div_iff₀ hη).mpr
  calc
    c ^ (N - d) * η ≤ coeff d Q * c ^ (N - d) := by
      nlinarith [mul_nonneg (sub_nonneg.mpr hηQ) (pow_nonneg hc (N - d))]
    _ ≤ coeff N (Q * CountSeriesCore.expShift c) * (Nat.factorial (N - d) : ℝ) := ht
    _ ≤ ((N : ℝ) * ε * B * (L + 1) ^ N) * (Nat.factorial (N - d) : ℝ) :=
      mul_le_mul_of_nonneg_right hA (le_of_lt hf)
    _ = (Nat.factorial (N - d) : ℝ) * jetConstant N M * ε := by
      dsimp [B, L, K, jetConstant]
      ring

def lawSeries (D : ℕ) (p : ℕ → ℝ) : PowerSeries ℝ :=
  (BoundedCountLaw.factorialPGF D p : PowerSeries ℝ)
def lawMean (D : ℕ) (p : ℕ → ℝ) : ℝ :=
  ∑ n ∈ Finset.range (D + 1), p n * (n : ℝ)
def lawMoment (D : ℕ) (p : ℕ → ℝ) (r : ℕ) : ℝ :=
  ∑ n ∈ Finset.range (D + 1), p n * (n.choose r : ℝ)

theorem law_coefficient_eq_moment (D r : ℕ) (p : ℕ → ℝ) :
    coeff r (lawSeries D p) = lawMoment D p r := by
  simp only [lawSeries, lawMoment, Polynomial.coeff_coe, BoundedCountLaw.factorialPGF_coeff]

theorem law_constant (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) :
    constantCoeff (lawSeries D p) = 1 := by
  simpa only [lawSeries, Polynomial.constantCoeff_coe] using
    BoundedCountLaw.factorialPGF_constant D p hp.2.1

theorem law_mean_eq_coefficient (D : ℕ) (p : ℕ → ℝ) :
    coeff 1 (lawSeries D p) = lawMean D p := by
  simp [law_coefficient_eq_moment, lawMoment, lawMean, Nat.choose_one_right]

theorem law_log_mean (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) :
    coeff 1 (logOf (lawSeries D p)) = lawMean D p := by
  rw [CountSeriesCore.coeff_one_logOf _ (law_constant D p hp), law_mean_eq_coefficient]

theorem law_coefficient_bounds (D : ℕ) (p : ℕ → ℝ) (hp : BoundedCountLaw.IsBoundedLaw D p) (r : ℕ) :
    0 ≤ coeff r (lawSeries D p) ∧ coeff r (lawSeries D p) ≤ (2 : ℝ) ^ D := by
  constructor
  · simpa only [lawSeries, Polynomial.coeff_coe] using
      BoundedCountLaw.factorialPGF_coeff_nonneg D r p (fun j _ => hp.1 j)
  · rw [law_coefficient_eq_moment, lawMoment]
    calc
      (∑ n ∈ Finset.range (D + 1), p n * (n.choose r : ℝ)) ≤
          ∑ n ∈ Finset.range (D + 1), p n * (2 : ℝ) ^ D := by
        apply Finset.sum_le_sum
        intro n hn
        apply mul_le_mul_of_nonneg_left _ (hp.1 n)
        have hnD : n ≤ D := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hn
        have hchoose : n.choose r ≤ 2 ^ D := (Nat.choose_le_two_pow n r).trans
          (pow_le_pow_right₀ (by norm_num : (1 : ℕ) ≤ 2) hnD)
        exact_mod_cast hchoose
      _ = (2 : ℝ) ^ D := by rw [← Finset.sum_mul, hp.2.1, one_mul]

theorem cumulant_controls_log (P Q : PowerSeries ℝ) (r : ℕ) (ε : ℝ)
    (h : |CountSeriesCore.factorialCumulant P r - CountSeriesCore.factorialCumulant Q r| ≤ ε) :
    |coeff r (logOf P) - coeff r (logOf Q)| ≤ ε := by
  have hf : (1 : ℝ) ≤ (Nat.factorial r : ℝ) := by exact_mod_cast Nat.factorial_pos r
  have hh : (Nat.factorial r : ℝ) * |coeff r (logOf P) - coeff r (logOf Q)| ≤ ε := by
    simpa only [CountSeriesCore.factorialCumulant, ← mul_sub, abs_mul,
      abs_of_nonneg (by positivity : (0 : ℝ) ≤ (Nat.factorial r : ℝ))] using h
  nlinarith [mul_nonneg (sub_nonneg.mpr hf) (abs_nonneg (coeff r (logOf P) - coeff r (logOf Q)))]

theorem ordered_law_mean_power_bound (D d : ℕ) (p q : ℕ → ℝ) (ε η : ℝ)
    (hd : d ≤ D) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (hq : BoundedCountLaw.IsBoundedLaw D q) (hε : 0 ≤ ε) (hη : 0 < η)
    (hηq : η ≤ lawMoment D q d) (horder : lawMean D q ≤ lawMean D p)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    (lawMean D p - lawMean D q) ^ (D + 1 - d) ≤
      (Nat.factorial (D + 1 - d) : ℝ) * jetConstant (D + 1) ((2 : ℝ) ^ D) * ε / η := by
  apply support_power_bound (D + 1) d (lawSeries D p) (lawSeries D q)
    ((2 : ℝ) ^ D) ε η (lawMean D p - lawMean D q)
  · omega
  · positivity
  · exact hε
  · exact hη
  · exact law_constant D p hp
  · exact law_constant D q hq
  · intro j hj
    rw [abs_of_nonneg (law_coefficient_bounds D p hp j).1]
    exact (law_coefficient_bounds D p hp j).2
  · intro j hj
    exact (law_coefficient_bounds D q hq j).2
  · intro j
    exact (law_coefficient_bounds D q hq j).1
  · simpa only [lawSeries, Polynomial.coeff_coe] using
      BoundedCountLaw.factorialPGF_coeff_above D (D + 1) p (by omega)
  · simpa only [law_coefficient_eq_moment] using hηq
  · exact sub_nonneg.mpr horder
  · have hpm := (law_coefficient_bounds D p hp 1).2
    have hqm := (law_coefficient_bounds D q hq 1).1
    rw [law_mean_eq_coefficient] at hpm hqm
    linarith
  · rw [law_log_mean D p hp, law_log_mean D q hq]
  · intro r hr hD
    exact cumulant_controls_log (lawSeries D p) (lawSeries D q) r ε (hκ r hr hD)

theorem law_mean_power_bound (D d : ℕ) (p q : ℕ → ℝ) (ε η : ℝ)
    (hd : d ≤ D) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (hq : BoundedCountLaw.IsBoundedLaw D q) (hε : 0 ≤ ε) (hη : 0 < η)
    (hηp : η ≤ lawMoment D p d) (hηq : η ≤ lawMoment D q d)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    |lawMean D p - lawMean D q| ^ (D + 1 - d) ≤
      (Nat.factorial (D + 1 - d) : ℝ) * jetConstant (D + 1) ((2 : ℝ) ^ D) * ε / η := by
  rcases le_total (lawMean D q) (lawMean D p) with horder | horder
  · rw [abs_of_nonneg (sub_nonneg.mpr horder)]
    exact ordered_law_mean_power_bound D d p q ε η hd hp hq hε hη hηq horder hκ
  · rw [abs_sub_comm, abs_of_nonneg (sub_nonneg.mpr horder)]
    apply ordered_law_mean_power_bound D d q p ε η hd hq hp hε hη hηp horder
    intro r hr hD
    rw [abs_sub_comm]
    exact hκ r hr hD

theorem root_of_power_bound (m : ℕ) (x B : ℝ) (hm : 0 < m)
    (hx : 0 ≤ x) (hbound : x ^ m ≤ B) : x ≤ B ^ (1 / (m : ℝ)) := by
  have hmR : (0 : ℝ) < (m : ℝ) := by exact_mod_cast hm
  have hr := Real.rpow_le_rpow (pow_nonneg hx m) hbound
    (by positivity : (0 : ℝ) ≤ 1 / (m : ℝ))
  have he : (m : ℝ) * (1 / (m : ℝ)) = 1 := by field_simp
  rw [← Real.rpow_natCast, ← Real.rpow_mul hx, he, Real.rpow_one] at hr
  exact hr

theorem law_mean_holder_bound (D d : ℕ) (p q : ℕ → ℝ) (ε η : ℝ)
    (hd : d ≤ D) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (hq : BoundedCountLaw.IsBoundedLaw D q) (hε : 0 ≤ ε) (hη : 0 < η)
    (hηp : η ≤ lawMoment D p d) (hηq : η ≤ lawMoment D q d)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    |lawMean D p - lawMean D q| ≤
      ((Nat.factorial (D + 1 - d) : ℝ) * jetConstant (D + 1) ((2 : ℝ) ^ D) * ε / η) ^
        (1 / ((D + 1 - d : ℕ) : ℝ)) :=
  root_of_power_bound (D + 1 - d) _ _ (by omega) (abs_nonneg _)
    (law_mean_power_bound D d p q ε η hd hp hq hε hη hηp hηq hκ)

theorem binomial_inverse_stability (D : ℕ) (p q : ℕ → ℝ) (E : ℝ)
    (hE : 0 ≤ E) (hMom : ∀ j ≤ D, |lawMoment D p j - lawMoment D q j| ≤ E) :
    ∀ j ≤ D, |p j - q j| ≤ E * (1 + ((D : ℝ) + 1) * (2 : ℝ) ^ D) ^ (D + 1 - j) := by
  let S : ℝ := 1 + ((D : ℝ) + 1) * (2 : ℝ) ^ D
  have hS : 1 ≤ S := by
    dsimp [S]
    have hh : 0 ≤ ((D : ℝ) + 1) * (2 : ℝ) ^ D := by positivity
    linarith
  have hS0 : 0 ≤ S := le_trans (by norm_num) hS
  suffices hall : ∀ t : ℕ, ∀ j ≤ D, D - j = t → |p j - q j| ≤ E * S ^ (t + 1) by
    intro j hj
    have h := hall (D - j) j hj rfl
    have he : D - j + 1 = D + 1 - j := by omega
    simpa only [he, S] using h
  intro t
  induction t using Nat.strong_induction_on with
  | h t ih =>
    intro j hj ht
    have hmem : j ∈ Finset.range (D + 1) := Finset.mem_range.mpr (by omega)
    have hsum := Finset.sum_erase_add (Finset.range (D + 1))
      (fun n => (p n - q n) * (n.choose j : ℝ)) hmem
    simp only [Nat.choose_self, Nat.cast_one, mul_one] at hsum
    have hdiff : lawMoment D p j - lawMoment D q j =
        ∑ n ∈ Finset.range (D + 1), (p n - q n) * (n.choose j : ℝ) := by
      simp only [lawMoment, ← Finset.sum_sub_distrib]
      apply Finset.sum_congr rfl
      intro n hn
      ring
    have heq : p j - q j = lawMoment D p j - lawMoment D q j -
        ∑ n ∈ (Finset.range (D + 1)).erase j, (p n - q n) * (n.choose j : ℝ) := by
      rw [hdiff]
      linarith
    have hrest : |∑ n ∈ (Finset.range (D + 1)).erase j, (p n - q n) * (n.choose j : ℝ)| ≤
        ((D : ℝ) + 1) * (E * S ^ t * (2 : ℝ) ^ D) := by
      calc
        |∑ n ∈ (Finset.range (D + 1)).erase j, (p n - q n) * (n.choose j : ℝ)| ≤
            ∑ n ∈ (Finset.range (D + 1)).erase j, |(p n - q n) * (n.choose j : ℝ)| :=
          Finset.abs_sum_le_sum_abs _ _
        _ ≤ ∑ _n ∈ (Finset.range (D + 1)).erase j, E * S ^ t * (2 : ℝ) ^ D := by
          apply Finset.sum_le_sum
          intro n hn
          have hnj := (Finset.mem_erase.mp hn).1
          have hnD : n ≤ D := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using (Finset.mem_erase.mp hn).2
          by_cases hnjlt : n < j
          · simp only [Nat.choose_eq_zero_of_lt hnjlt, Nat.cast_zero, mul_zero, abs_zero]
            positivity
          · have hjn : j < n := by omega
            have hnlt : D - n < t := by omega
            have hpq : |p n - q n| ≤ E * S ^ t :=
              (ih (D - n) hnlt n hnD rfl).trans
                (mul_le_mul_of_nonneg_left (pow_le_pow_right₀ hS (by omega)) hE)
            have hchoose : (n.choose j : ℝ) ≤ (2 : ℝ) ^ D := by
              exact_mod_cast (Nat.choose_le_two_pow n j).trans
                (pow_le_pow_right₀ (by norm_num : (1 : ℕ) ≤ 2) hnD)
            rw [abs_mul, abs_of_nonneg (by positivity : (0 : ℝ) ≤ (n.choose j : ℝ))]
            exact mul_le_mul hpq hchoose (by positivity) (mul_nonneg hE (pow_nonneg hS0 t))
        _ ≤ ∑ _n ∈ Finset.range (D + 1), E * S ^ t * (2 : ℝ) ^ D :=
          Finset.sum_le_sum_of_subset_of_nonneg (Finset.erase_subset _ _) (fun _ _ _ => by positivity)
        _ = ((D : ℝ) + 1) * (E * S ^ t * (2 : ℝ) ^ D) := by simp [nsmul_eq_mul]
    have hpw : 1 ≤ S ^ t := one_le_pow₀ hS
    calc
      |p j - q j| ≤ |lawMoment D p j - lawMoment D q j| +
          |∑ n ∈ (Finset.range (D + 1)).erase j, (p n - q n) * (n.choose j : ℝ)| := by
        conv_lhs => rw [heq, sub_eq_add_neg]
        simpa only [abs_neg] using abs_add_le (lawMoment D p j - lawMoment D q j)
          (-(∑ n ∈ (Finset.range (D + 1)).erase j, (p n - q n) * (n.choose j : ℝ)))
      _ ≤ E + ((D : ℝ) + 1) * (E * S ^ t * (2 : ℝ) ^ D) := add_le_add (hMom j hj) hrest
      _ ≤ E * S ^ (t + 1) := by
        rw [pow_succ]
        have hES : E ≤ E * S ^ t := by nlinarith [mul_nonneg hE (sub_nonneg.mpr hpw)]
        dsimp [S] at *
        nlinarith

def jetScale (D : ℕ) : ℝ :=
  (2 : ℝ) ^ D * ((logBase (D + 1) ((2 : ℝ) ^ D)) ^ (D + 1) + 1) ^ (D + 1)
def tvScale (D : ℕ) : ℝ :=
  ((D : ℝ) + 1) * jetScale D * (1 + ((D : ℝ) + 1) * (2 : ℝ) ^ D) ^ (D + 1) / 2
def lawTV (D : ℕ) (p q : ℕ → ℝ) : ℝ :=
  (∑ j ∈ Finset.range (D + 1), |p j - q j|) / 2

theorem law_moment_difference_bound (D : ℕ) (p q : ℕ → ℝ) (ε : ℝ)
    (hp : BoundedCountLaw.IsBoundedLaw D p) (hq : BoundedCountLaw.IsBoundedLaw D q)
    (hε : 0 ≤ ε)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    ∀ j ≤ D + 1, |lawMoment D p j - lawMoment D q j| ≤
      (|lawMean D p - lawMean D q| + ((D : ℝ) + 1) * ε) * jetScale D := by
  let N := D + 1
  let M : ℝ := (2 : ℝ) ^ D
  let K := logBase N M
  let L := K ^ N
  let δ := |lawMean D p - lawMean D q| + ((D : ℝ) + 1) * ε
  have hM : 0 ≤ M := by dsimp [M]; positivity
  have hK : 1 ≤ K := by
    dsimp [K, logBase]
    have hh : 0 ≤ 2 * ((N : ℝ) + 1) * M := by positivity
    linarith
  have hKM : 2 * ((N : ℝ) + 1) * M ≤ K := by dsimp [K, logBase]; linarith
  have hL : 0 ≤ L := pow_nonneg (le_trans (by norm_num) hK) N
  have hδ : 0 ≤ δ := by dsimp [δ]; positivity
  have hU := normalized_log_bound N (lawSeries D p) M K hM hK hKM (law_constant D p hp)
    (fun j _ => by rw [abs_of_nonneg (law_coefficient_bounds D p hp j).1]; exact (law_coefficient_bounds D p hp j).2)
  have hdiff : ∀ k < N, |coeff k (derivative (logOf (lawSeries D p))) -
      coeff k (derivative (logOf (lawSeries D q)))| ≤ δ := by
    intro k hk
    by_cases hk0 : k = 0
    · subst k
      simp only [coeff_derivative, Nat.cast_zero, zero_add, mul_one, law_log_mean D p hp, law_log_mean D q hq]
      dsimp [δ]
      have hnε : 0 ≤ ((D : ℝ) + 1) * ε := by positivity
      linarith
    · simp only [coeff_derivative]
      rw [← sub_mul, abs_mul, abs_of_nonneg (by positivity : 0 ≤ (k : ℝ) + 1)]
      have hh := cumulant_controls_log (lawSeries D p) (lawSeries D q) (k + 1) ε
        (hκ (k + 1) (by omega) (by dsimp [N] at hk; omega))
      calc
        |coeff (k + 1) (logOf (lawSeries D p)) - coeff (k + 1) (logOf (lawSeries D q))| * ((k : ℝ) + 1) ≤
            ε * ((k : ℝ) + 1) := mul_le_mul_of_nonneg_right hh (by positivity)
        _ ≤ ε * ((D : ℝ) + 1) := by
          apply mul_le_mul_of_nonneg_left _ hε
          have hkD : k ≤ D := by dsimp [N] at hk; omega
          exact_mod_cast Nat.add_le_add_right hkD 1
        _ ≤ δ := by dsimp [δ]; nlinarith [abs_nonneg (lawMean D p - lawMean D q)]
  have herr := ode_coefficient_stability N (fun j => coeff j (lawSeries D p))
    (fun j => coeff j (lawSeries D q))
    (fun j => coeff j (derivative (logOf (lawSeries D p))))
    (fun j => coeff j (derivative (logOf (lawSeries D q)))) δ M L hδ hM hL
    (by simp [coeff_zero_eq_constantCoeff_apply, law_constant D p hp, law_constant D q hq])
    (fun j _ => normalized_log_recurrence _ (law_constant D p hp) j)
    (fun j _ => normalized_log_recurrence _ (law_constant D q hq) j)
    (fun j _ => by rw [abs_of_nonneg (law_coefficient_bounds D q hq j).1]; exact (law_coefficient_bounds D q hq j).2)
    hU hdiff
  intro j hj
  have h := (herr j hj).trans
    (mul_le_mul_of_nonneg_left (pow_le_pow_right₀ (by linarith : 1 ≤ L + 1) hj) (mul_nonneg hδ hM))
  rw [law_coefficient_eq_moment, law_coefficient_eq_moment] at h
  dsimp [δ, M, L, K, N, jetScale] at *
  nlinarith

theorem law_tv_mean_bound (D : ℕ) (p q : ℕ → ℝ) (ε : ℝ)
    (hp : BoundedCountLaw.IsBoundedLaw D p) (hq : BoundedCountLaw.IsBoundedLaw D q)
    (hε : 0 ≤ ε)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    lawTV D p q ≤ tvScale D * (|lawMean D p - lawMean D q| + ((D : ℝ) + 1) * ε) := by
  let E := (|lawMean D p - lawMean D q| + ((D : ℝ) + 1) * ε) * jetScale D
  let S : ℝ := 1 + ((D : ℝ) + 1) * (2 : ℝ) ^ D
  have hE : 0 ≤ E := by dsimp [E, jetScale, logBase]; positivity
  have hS : 1 ≤ S := by
    dsimp [S]
    have hh : 0 ≤ ((D : ℝ) + 1) * (2 : ℝ) ^ D := by positivity
    linarith
  have hm := law_moment_difference_bound D p q ε hp hq hε hκ
  have hi := binomial_inverse_stability D p q E hE (fun j hj => hm j (by omega))
  have hs : (∑ j ∈ Finset.range (D + 1), |p j - q j|) ≤ ((D : ℝ) + 1) * (E * S ^ (D + 1)) := by
    calc
      (∑ j ∈ Finset.range (D + 1), |p j - q j|) ≤ ∑ _j ∈ Finset.range (D + 1), E * S ^ (D + 1) := by
        apply Finset.sum_le_sum
        intro j hj
        have hjD : j ≤ D := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hj
        exact (hi j hjD).trans (mul_le_mul_of_nonneg_left (pow_le_pow_right₀ hS (by omega)) hE)
      _ = ((D : ℝ) + 1) * (E * S ^ (D + 1)) := by simp [nsmul_eq_mul]
  unfold lawTV
  calc
    (∑ j ∈ Finset.range (D + 1), |p j - q j|) / 2 ≤ (((D : ℝ) + 1) * (E * S ^ (D + 1))) / 2 :=
      div_le_div_of_nonneg_right hs (by norm_num)
    _ = tvScale D * (|lawMean D p - lawMean D q| + ((D : ℝ) + 1) * ε) := by
      dsimp [E, S, tvScale]
      ring

theorem law_tv_holder_bound (D d : ℕ) (p q : ℕ → ℝ) (ε η : ℝ)
    (hd : d ≤ D) (hp : BoundedCountLaw.IsBoundedLaw D p)
    (hq : BoundedCountLaw.IsBoundedLaw D q) (hε : 0 ≤ ε) (hη : 0 < η)
    (hηp : η ≤ lawMoment D p d) (hηq : η ≤ lawMoment D q d)
    (hκ : ∀ r, 2 ≤ r → r ≤ D + 1 →
      |BoundedCountLaw.lawFactorialCumulant D p r - BoundedCountLaw.lawFactorialCumulant D q r| ≤ ε) :
    lawTV D p q ≤ tvScale D *
      (((Nat.factorial (D + 1 - d) : ℝ) * jetConstant (D + 1) ((2 : ℝ) ^ D) * ε / η) ^
        (1 / ((D + 1 - d : ℕ) : ℝ)) + ((D : ℝ) + 1) * ε) := by
  apply (law_tv_mean_bound D p q ε hp hq hε hκ).trans
  apply mul_le_mul_of_nonneg_left _ (by dsimp [tvScale, jetScale, logBase]; positivity)
  exact add_le_add (law_mean_holder_bound D d p q ε η hd hp hq hε hη hηp hηq hκ) (le_refl _)

end CountQuantitativeJets

#print axioms CountQuantitativeJets.ode_coefficient_stability
#print axioms CountQuantitativeJets.log_derivative_coefficient_bound
#print axioms CountQuantitativeJets.normalized_log_recurrence
#print axioms CountQuantitativeJets.normalized_log_bound
#print axioms CountQuantitativeJets.shifted_coefficient_bound
#print axioms CountQuantitativeJets.shifted_recurrence
#print axioms CountQuantitativeJets.support_power_bound
#print axioms CountQuantitativeJets.law_coefficient_bounds
#print axioms CountQuantitativeJets.ordered_law_mean_power_bound
#print axioms CountQuantitativeJets.law_mean_power_bound
#print axioms CountQuantitativeJets.law_mean_holder_bound
#print axioms CountQuantitativeJets.binomial_inverse_stability
#print axioms CountQuantitativeJets.law_moment_difference_bound
#print axioms CountQuantitativeJets.law_tv_mean_bound
#print axioms CountQuantitativeJets.law_tv_holder_bound
