theory Count_Endpoints
  imports Complex_Main
begin

text \<open>
An independent algebraic reconstruction of one family of D=1 moment boxes.
All variables denote real population parameters. The moment equations are
assumptions here; this theory does not construct a probability model, verify
measured observations, or certify the Python/Sage implementation.

The square-root arguments used in endpoint formulas are nonnegative under the
stated hypotheses. This matters because Isabelle's real sqrt is signed on
negative arguments.
\<close>

definition pair_box ::
  "real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> bool"
where
  "pair_box B a c d e p b \<longleftrightarrow>
    0 \<le> p \<and> p \<le> 1 \<and> 0 \<le> b \<and> b \<le> B \<and>
    a \<le> p + b \<and> p + b \<le> c \<and>
    d \<le> b^2 + 2*p*b \<and> b^2 + 2*p*b \<le> e"

definition feasible ::
  "real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> real \<Rightarrow> bool"
where
  "feasible B a c d e p \<longleftrightarrow> (\<exists>b. pair_box B a c d e p b)"

lemma second_moment_identity:
  fixes p b :: real
  shows "b^2 + 2*p*b = (p+b)^2 - p^2"
  by (simp add: power2_eq_square algebra_simps)

lemma mean_one_second_moment:
  fixes p :: real
  shows "(1-p)^2 + 2*p*(1-p) = 1-p^2"
  by (simp add: power2_eq_square algebra_simps)

theorem mean_one_polynomial_projection:
  "feasible 1 1 1 u v p \<longleftrightarrow>
    0 \<le> p \<and> p \<le> 1 \<and> u \<le> 1-p^2 \<and> 1-p^2 \<le> v"
proof
  assume "feasible 1 1 1 u v p"
  then obtain b where h: "pair_box 1 1 1 u v p b"
    unfolding feasible_def by blast
  have b: "b = 1-p"
    using h unfolding pair_box_def by linarith
  show "0 \<le> p \<and> p \<le> 1 \<and> u \<le> 1-p^2 \<and> 1-p^2 \<le> v"
    using h unfolding pair_box_def b
    by (simp add: mean_one_second_moment)
next
  assume h: "0 \<le> p \<and> p \<le> 1 \<and> u \<le> 1-p^2 \<and> 1-p^2 \<le> v"
  have b0: "0 \<le> 1-p" and b1: "1-p \<le> 1"
    using h by linarith+
  have "pair_box 1 1 1 u v p (1-p)"
    using h b0 b1 unfolding pair_box_def
    by (simp add: mean_one_second_moment)
  then show "feasible 1 1 1 u v p"
    unfolding feasible_def by blast
qed

theorem mean_one_endpoint_projection:
  assumes u0: "0 \<le> u" and uv: "u \<le> v" and v1: "v \<le> 1"
  shows "feasible 1 1 1 u v p \<longleftrightarrow>
    sqrt (1-v) \<le> p \<and> p \<le> sqrt (1-u)"
proof
  assume "feasible 1 1 1 u v p"
  then have h: "0 \<le> p \<and> p \<le> 1 \<and> u \<le> 1-p^2 \<and> 1-p^2 \<le> v"
    using mean_one_polynomial_projection by blast
  have lo: "sqrt (1-v) \<le> p"
  proof (rule real_le_lsqrt)
    show "0 \<le> p" using h by blast
    show "1-v \<le> p^2" using h by linarith
  qed
  have hi: "p \<le> sqrt (1-u)"
    by (rule real_le_rsqrt) (use h in linarith)
  show "sqrt (1-v) \<le> p \<and> p \<le> sqrt (1-u)"
    using lo hi by blast
next
  assume h: "sqrt (1-v) \<le> p \<and> p \<le> sqrt (1-u)"
  have sl0: "0 \<le> sqrt (1-v)"
    using v1 by simp
  have su1: "sqrt (1-u) \<le> 1"
    using u0 by simp
  have p0: "0 \<le> p" and p1: "p \<le> 1"
    using h sl0 su1 by linarith+
  have low_sq: "1-v \<le> p^2"
    using h sqrt_le_D by blast
  have high_sq: "p^2 \<le> 1-u"
    using h p0 sqrt_ge_absD[of p "1-u"] by simp
  have "0 \<le> p \<and> p \<le> 1 \<and> u \<le> 1-p^2 \<and> 1-p^2 \<le> v"
    using p0 p1 low_sq high_sq by linarith
  then show "feasible 1 1 1 u v p"
    using mean_one_polynomial_projection by blast
qed

theorem mean_one_constructive_witness:
  assumes "0 \<le> u" "u \<le> v" "v \<le> 1"
    "sqrt (1-v) \<le> p" "p \<le> sqrt (1-u)"
  shows "pair_box 1 1 1 u v p (1-p)"
proof -
  have "feasible 1 1 1 u v p"
    using mean_one_endpoint_projection[OF assms(1-3), of p] assms(4-5) by blast
  then obtain b where h: "pair_box 1 1 1 u v p b"
    unfolding feasible_def by blast
  have "b = 1-p" using h unfolding pair_box_def by linarith
  with h show ?thesis by simp
qed

lemma sqrt_quarter:
  "sqrt (1/4) = (1/2 :: real)"
  by (rule real_sqrt_unique) (simp_all add: power_divide)

lemma sqrt_three_quarters:
  "sqrt (3/4) = sqrt (3::real) / 2"
  by (simp add: real_sqrt_divide)

theorem illustrative_interval:
  "feasible 1 1 1 (1/4) (3/4) p \<longleftrightarrow>
    1/2 \<le> p \<and> p \<le> sqrt 3 / 2"
  using mean_one_endpoint_projection[of "1/4" "3/4" p]
  by (simp add: sqrt_quarter sqrt_three_quarters)

theorem half_singleton:
  "feasible 1 1 1 (1/2) (1/2) p \<longleftrightarrow> p = sqrt (1/2)"
  using mean_one_endpoint_projection[of "1/2" "1/2" p]
  by auto

theorem half_singleton_exists:
  "\<exists>p b. pair_box 1 1 1 (1/2) (1/2) p b"
  using half_singleton[of "sqrt (1/2)"] unfolding feasible_def by blast

theorem full_source_interval:
  "feasible 1 1 1 0 1 p \<longleftrightarrow> 0 \<le> p \<and> p \<le> 1"
  using mean_one_endpoint_projection[of 0 1 p] by simp

theorem zero_second_boundary:
  "feasible 1 1 1 0 0 p \<longleftrightarrow> p = 1"
  using mean_one_endpoint_projection[of 0 0 p] by auto

theorem unit_second_boundary:
  "feasible 1 1 1 1 1 p \<longleftrightarrow> p = 0"
  using mean_one_endpoint_projection[of 1 1 p] by auto

theorem zero_background_projection:
  "feasible 0 a c d e p \<longleftrightarrow>
    0 \<le> p \<and> p \<le> 1 \<and> a \<le> p \<and> p \<le> c \<and> d \<le> 0 \<and> 0 \<le> e"
  unfolding feasible_def pair_box_def by auto

theorem negative_ceiling_empty:
  assumes "B < 0"
  shows "\<not> feasible B a c d e p"
  using assms unfolding feasible_def pair_box_def by (auto; linarith)

theorem reversed_mean_empty:
  assumes "c < a"
  shows "\<not> feasible B a c d e p"
  using assms unfolding feasible_def pair_box_def by (auto; linarith)

theorem reversed_second_empty:
  assumes "e < d"
  shows "\<not> feasible B a c d e p"
  using assms unfolding feasible_def pair_box_def by (auto; linarith)

theorem impossible_mean_one_second:
  assumes "1 < u"
  shows "\<not> feasible 1 1 1 u v p"
  using assms zero_le_power2[of p]
  by (auto simp: mean_one_polynomial_projection; linarith)

theorem swapped_illustrative_box_empty:
  "\<not> feasible 1 1 1 (3/4) (1/4) p"
  by (rule reversed_second_empty) simp

text \<open>
An exact endpoint descriptor contains both a polynomial equation and a
rational isolating interval. The interval selects the positive root; merely
reporting the polynomial would leave a sign ambiguity. No minimal-polynomial
or irreducibility claim is needed here.
\<close>

lemma isolated_positive_square_root:
  fixes a l h x :: real
  assumes l0: "0 \<le> l" and h0: "0 \<le> h"
    and lsq: "l^2 < a" and hsq: "a < h^2"
  shows "(l < x \<and> x < h \<and> x^2 = a) \<longleftrightarrow> x = sqrt a"
proof
  assume hx: "l < x \<and> x < h \<and> x^2 = a"
  have "0 \<le> x" using l0 hx by linarith
  with hx real_sqrt_unique[of x a] show "x = sqrt a" by auto
next
  assume "x = sqrt a"
  moreover have "l < sqrt a" using lsq by (rule real_less_rsqrt)
  moreover have "sqrt a < h" using h0 hsq by (rule real_less_lsqrt)
  moreover have "0 \<le> a" using zero_le_power2[of l] lsq by linarith
  ultimately show "l < x \<and> x < h \<and> x^2 = a" by simp
qed

theorem upper_endpoint_descriptor:
  "(4/5 < x \<and> x < 9/10 \<and> 4*x^2-3 = 0) \<longleftrightarrow>
    x = sqrt 3 / 2"
proof -
  have interval:
    "(4/5 < x \<and> x < 9/10 \<and> x^2 = 3/4) \<longleftrightarrow>
      x = sqrt (3/4)"
    by (rule isolated_positive_square_root) (simp_all add: power_divide)
  have eq: "(4*x^2-3 = 0) \<longleftrightarrow> x^2 = 3/4"
    by linarith
  show ?thesis using interval by (simp only: eq sqrt_three_quarters)
qed

theorem singleton_endpoint_descriptor:
  "(7/10 < x \<and> x < 4/5 \<and> 2*x^2-1 = 0) \<longleftrightarrow>
    x = sqrt (1/2)"
proof -
  have interval:
    "(7/10 < x \<and> x < 4/5 \<and> x^2 = 1/2) \<longleftrightarrow>
      x = sqrt (1/2)"
    by (rule isolated_positive_square_root) (simp_all add: power_divide)
  have eq: "(2*x^2-1 = 0) \<longleftrightarrow> x^2 = 1/2"
    by linarith
  show ?thesis using interval by (simp only: eq)
qed

theorem lower_endpoint_descriptor:
  "(0 < x \<and> x < 1 \<and> 2*x-1 = 0) \<longleftrightarrow> x = (1/2::real)"
  by linarith

theorem upper_endpoint_included:
  "feasible 1 1 1 (1/4) (3/4) (sqrt 3 / 2)"
proof -
  have "4/5 < sqrt (3::real)/2"
    using upper_endpoint_descriptor[of "sqrt 3 / 2"] by blast
  then show ?thesis by (simp add: illustrative_interval; linarith)
qed

theorem lower_endpoint_included:
  "feasible 1 1 1 (1/4) (3/4) (1/2)"
proof -
  have "4/5 < sqrt (3::real)/2"
    using upper_endpoint_descriptor[of "sqrt 3 / 2"] by blast
  then show ?thesis by (simp add: illustrative_interval; linarith)
qed

theorem wrong_lower_rejected:
  "\<not> feasible 1 1 1 (1/4) (3/4) (1/4)"
  by (simp add: illustrative_interval)

theorem wrong_upper_rejected:
  "\<not> feasible 1 1 1 (1/4) (3/4) (9/10)"
  by (simp add: mean_one_polynomial_projection power_divide)

theorem negative_root_not_endpoint:
  "4*(-sqrt (3::real)/2)^2-3 = 0 \<and>
    \<not> (4/5 < -sqrt 3 / 2 \<and> -sqrt 3 / 2 < 9/10)"
proof -
  have root: "4*(-sqrt (3::real)/2)^2-3 = 0"
    by (simp add: power_divide)
  have pos: "0 < sqrt (3::real)" by simp
  show ?thesis using root pos by linarith
qed

end
