theory Count_Endpoint_Descriptors
  imports Count_Endpoints
begin

text \<open>
Exact descriptor and assumption controls. The dyadic numbers below are explicit mathematical
constants; proving their isolation property does not verify a parser or prove
that every run of an external program prints these values faithfully.
\<close>

theorem upper_radicand_guard_needed:
  "(sqrt (1-(2::real)) \<le> -1 \<and> -1 \<le> sqrt (1-2)) \<and>
    \<not> feasible 1 1 1 2 2 (-1)"
  by (simp add: real_sqrt_minus mean_one_polynomial_projection)

theorem lower_radicand_guard_needed:
  "(sqrt (1-(-1::real)) \<le> sqrt 2 \<and> sqrt 2 \<le> sqrt (1-(-1))) \<and>
    \<not> feasible 1 1 1 (-1) (-1) (sqrt 2)"
  by (simp add: mean_one_polynomial_projection)

lemma isolated_positive_square_root_closed:
  fixes a l h x :: real
  assumes l0: "0 \<le> l" and h0: "0 \<le> h"
    and lsq: "l^2 < a" and hsq: "a < h^2"
  shows "(l \<le> x \<and> x \<le> h \<and> x^2 = a) \<longleftrightarrow> x = sqrt a"
proof
  assume hx: "l \<le> x \<and> x \<le> h \<and> x^2 = a"
  have "0 \<le> x" using l0 hx by linarith
  with hx real_sqrt_unique[of x a] show "x = sqrt a" by auto
next
  assume "x = sqrt a"
  then have "l < x \<and> x < h \<and> x^2 = a"
    using isolated_positive_square_root[OF assms, of x] by blast
  then show "l \<le> x \<and> x \<le> h \<and> x^2 = a" by auto
qed

theorem dyadic_upper_endpoint_descriptor:
  "(1859775393/2147483648 \<le> x \<and>
      x \<le> 3719550787/4294967296 \<and> x^2 = 3/4) \<longleftrightarrow>
    x = sqrt 3 / 2"
proof -
  have eq:
    "(1859775393/2147483648 \<le> x \<and>
        x \<le> 3719550787/4294967296 \<and> x^2 = 3/4) \<longleftrightarrow>
      x = sqrt (3/4)"
    by (rule isolated_positive_square_root_closed) (simp_all add: power_divide)
  then show ?thesis by (simp add: sqrt_three_quarters)
qed

theorem dyadic_upper_endpoint_unique:
  "\<exists>!x::real. 1859775393/2147483648 \<le> x \<and>
    x \<le> 3719550787/4294967296 \<and> x^2 = 3/4"
  by (simp only: dyadic_upper_endpoint_descriptor; blast)

theorem dyadic_background_descriptor:
  "(575416509/4294967296 \<le> x \<and>
      x \<le> 287708255/2147483648 \<and> x^2-2*x+1/4 = 0) \<longleftrightarrow>
    x = 1 - sqrt 3 / 2"
proof -
  have bounds:
    "(575416509/4294967296 \<le> x \<and> x \<le> 287708255/2147483648) \<longleftrightarrow>
      (1859775393/2147483648 \<le> 1-x \<and> 1-x \<le> 3719550787/4294967296)"
    by linarith
  have equation:
    "(x^2-2*x+1/4 = 0) \<longleftrightarrow> (1-x)^2 = 3/4"
    by (simp add: power2_eq_square algebra_simps; linarith)
  show ?thesis
  proof
    assume h: "575416509/4294967296 \<le> x \<and>
      x \<le> 287708255/2147483648 \<and> x^2-2*x+1/4 = 0"
    have "1-x = sqrt 3 / 2"
      using h bounds equation dyadic_upper_endpoint_descriptor[of "1-x"] by blast
    then show "x = 1 - sqrt 3 / 2" by linarith
  next
    assume "x = 1 - sqrt 3 / 2"
    then have "1-x = sqrt 3 / 2" by linarith
    then show "575416509/4294967296 \<le> x \<and>
      x \<le> 287708255/2147483648 \<and> x^2-2*x+1/4 = 0"
      using bounds equation dyadic_upper_endpoint_descriptor[of "1-x"] by blast
  qed
qed

theorem dyadic_background_unique:
  "\<exists>!x::real. 575416509/4294967296 \<le> x \<and>
    x \<le> 287708255/2147483648 \<and> x^2-2*x+1/4 = 0"
  by (simp only: dyadic_background_descriptor; simp)

theorem descriptor_pair_is_feasible:
  assumes "1859775393/2147483648 \<le> p" "p \<le> 3719550787/4294967296"
    "p^2 = 3/4"
    "575416509/4294967296 \<le> b" "b \<le> 287708255/2147483648"
    "b^2-2*b+1/4 = 0"
  shows "pair_box 1 1 1 (1/4) (3/4) p b"
proof -
  have p: "p = sqrt 3 / 2"
    using assms(1-3) dyadic_upper_endpoint_descriptor[of p] by blast
  have b: "b = 1 - sqrt 3 / 2"
    using assms(4-6) dyadic_background_descriptor[of b] by blast
  have h: "feasible 1 1 1 (1/4) (3/4) p"
    using upper_endpoint_included by (simp only: p)
  then obtain t where ht: "pair_box 1 1 1 (1/4) (3/4) p t"
    unfolding feasible_def by blast
  have "t = b" using ht p b unfolding pair_box_def by linarith
  with ht show ?thesis by simp
qed

theorem degenerate_lower_descriptor:
  "(1/2 \<le> x \<and> x \<le> 1/2 \<and> x-1/2 = 0) \<longleftrightarrow> x = (1/2::real)"
  by linarith

end
