"""Optional numerical-study controls (CPython 3.13 plus locked NumPy/SciPy).

Run directly; these tests are outside the dependency-free core test discovery.
They test implementation invariants and failure reporting, not empirical rates.
"""

from decimal import Decimal, localcontext
from fractions import Fraction
import json
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import warnings

import numpy as np
from scipy.stats import binom, poisson

import emitter_background_cost as cost
import emitter_published_parameters as study


class AffinityControls(unittest.TestCase):
    def test_scalar_refinement_uses_finite_local_bracket_without_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            result = cost.search_known(100, 0.1, 0.1, 101, [0.09, 0.1, 0.11], 70)
        self.assertEqual(result["search"]["refinement_bracket"], [0.09, 0.11])
        self.assertGreater(result["necessary_windows_approximation"], 0)

    def test_identical_laws_have_zero_stable_prefix_distance(self):
        prefix = cost.pmf(100, 0.1, 1.0, 80)
        self.assertEqual(cost.neg_log_bc(prefix, prefix), 0.0)

    def test_near_identical_bernoulli_avoids_affinity_cancellation(self):
        p, q = 0.5, 0.500000001
        actual = cost.neg_log_bc([1 - p, p], [1 - q, q])
        with localcontext() as ctx:
            ctx.prec = 80
            pd, qd = Decimal.from_float(p), Decimal.from_float(q)
            expected = -((pd * qd).sqrt() + ((1 - pd) * (1 - qd)).sqrt()).ln()
        self.assertGreater(actual, 0)
        self.assertLess(abs(actual / float(expected) - 1), 2e-7)

    def test_tail_bound_dominates_direct_probability(self):
        for n, p, b, cutoff in ((0, 0.0, 2.0, 8), (8, 0.2, 1.0, 6), (40, 0.2, 1.0, 14)):
            tail = sum(
                binom.pmf(k, n, p) * poisson.sf(cutoff - k - 1, b) for k in range(n + 1)
            )
            self.assertGreaterEqual(float(cost.tail_upper(n * p + b, cutoff)), tail)
        self.assertEqual(float(cost.tail_upper(0, 3)), 0)
        self.assertEqual(float(cost.tail_upper(5, 3)), 1)

    def test_tail_correction_has_conservative_direction(self):
        # Independent closed form for two full Poisson laws.
        with localcontext() as ctx:
            ctx.prec = 80
            exact_distance = (Decimal(2).sqrt() - Decimal(3).sqrt()) ** 2 / 2
        evaluated = cost.decimal_pair(0, 0, 2, 0, 0, 3, 0, 12)
        corrected = Decimal(evaluated["combined_log_affinity_upper_approximation"])
        self.assertGreaterEqual(corrected, exact_distance)
        self.assertLess(
            evaluated["necessary_windows_approximation"], cost.C / float(exact_distance)
        )

    def test_tail_refinement_records_cutoff_and_precision(self):
        result = cost.pair_diagnostics(3, 0.2, 1, 4, 0.17, 0.92, 0.1, cutoff=8)
        self.assertGreater(result["evaluated_cutoff"], 8)
        self.assertLessEqual(result["tail_upper_to_prefix_ratio"], 1e-8)
        self.assertEqual(result["decimal_precision"], 80)
        self.assertEqual(
            result["numerical_status"], "approximation_not_interval_certified"
        )

    def test_decimal_precision_convergence_at_difficult_witness(self):
        args = (100, 0.1, 1.0, 101, 0.099503845029, 0.950111652, 0.0, 80)
        low = cost.decimal_pair(*args, precision=80)
        high = cost.decimal_pair(*args, precision=110)
        self.assertLess(
            abs(
                low["necessary_windows_approximation"]
                / high["necessary_windows_approximation"]
                - 1
            ),
            1e-12,
        )

    def test_model_and_grid_domain_validation(self):
        for args in (
            (-1, 0.1, 0),
            (1.2, 0.1, 0),
            (1, -0.1, 0),
            (1, 1.1, 0),
            (1, 0.1, -1),
            (1, 0.1, math.inf),
        ):
            with self.assertRaises(ValueError):
                cost.pmf(*args)
        with self.assertRaises(ValueError):
            cost.neg_log_bc([1, -1], [1, 0])
        for grid in ([0.2, 0.1], [0.1], [0.1, math.nan]):
            with self.assertRaises(ValueError):
                cost.validate_grid(grid, 1)

    def test_failed_optimizer_keeps_finite_grid_witness(self):
        failed = SimpleNamespace(
            x=np.array([math.nan, math.nan]),
            fun=math.nan,
            success=False,
            message="injected optimizer failure",
            nit=1,
            nfev=2,
        )
        with patch.object(cost, "minimize", return_value=failed):
            result = cost.search_pair(2, 0.2, 0.1, 3, 0, [0.1, 0.2], [0, 0.2])
        self.assertFalse(result["search"]["optimizer_success"])
        self.assertFalse(result["search"]["optimizer_candidate_valid"])
        self.assertEqual(result["search"]["chosen_from"], "grid")
        self.assertIsNone(result["search"]["optimizer_recomputed_objective"])
        self.assertGreater(result["necessary_windows_approximation"], 0)
        json.dumps(result, allow_nan=False)

    def test_iteration_limit_is_reported_without_global_claim(self):
        result = cost.search_pair(2, 0.2, 0.1, 3, 0, [0.1, 0.2], [0, 0.2], maxiter=1)
        self.assertFalse(result["search"]["optimizer_success"])
        self.assertFalse(result["search"]["global_optimum_certified"])
        self.assertGreater(result["necessary_windows_approximation"], 0)

    def test_scalar_optimizer_failure_keeps_finite_witness(self):
        failed = SimpleNamespace(
            x=math.nan, fun=math.nan, success=False, message="injected failure", nfev=1
        )
        with patch.object(cost, "minimize_scalar", return_value=failed):
            result = cost.search_known(2, 0.2, 0.1, 3, [0.1, 0.2])
        self.assertFalse(result["search"]["optimizer_success"])
        self.assertFalse(result["search"]["optimizer_candidate_valid"])
        json.dumps(result, allow_nan=False)


class EstimatorControls(unittest.TestCase):
    def test_records_reject_empty_negative_or_noninteger_counts(self):
        for record in ([], [-1, 0], [0.5, 1.0], [[0, 1]]):
            with self.assertRaises(ValueError):
                study.count_summary(record)

    def test_all_zero_record_does_not_identify_emitter_count(self):
        self.assertEqual(
            study.mle_binomial_M(np.zeros(4, dtype=int))["status"],
            "unidentified_zero_record",
        )

    def test_binomial_endpoint_is_included(self):
        result = study.mle_binomial_M(np.ones(4, dtype=int))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["estimate"], 1)
        self.assertEqual(result["selected_p"], 1)

    def test_search_cap_is_not_reported_as_unrestricted_fit(self):
        result = study.mle_binomial_M(np.array([0, 0, 0, 3]), search_span=10)
        self.assertEqual(result["status"], "search_cap")
        self.assertIsNone(result["estimate"])
        self.assertEqual(result["raw_estimate"], 12)
        self.assertLess(result["finite_minus_poisson_log_likelihood"], 0)
        self.assertFalse(result["global_optimum_certified"])

    def test_e2_retains_cancellation_estimate_with_negative_inferred_background(self):
        negative = study.factorial_cumulant_M(np.array([0, 0, 1, 1, 2]))
        self.assertEqual(negative["status"], "success")
        self.assertEqual(negative["estimate"], 13.5)
        self.assertEqual(negative["raw_estimate"], 13.5)
        self.assertEqual(
            negative["parameters"], {"M": "27/2", "p": "2/15", "background": "-1"}
        )
        self.assertTrue(negative["inferred_background_negative"])

    def test_e2_still_rejects_invalid_probability_count_and_cumulant_signs(self):
        invalid_p = study.factorial_cumulant_M(np.array([1, 1, 1, 1, 3]))
        self.assertEqual(invalid_p["status"], "probability_out_of_range")
        self.assertIsNone(invalid_p["estimate"])
        self.assertEqual(invalid_p["parameters"]["p"], "103/95")
        invalid_count = study.factorial_cumulant_M(np.array([1, 1, 1, 3]))
        self.assertEqual(invalid_count["status"], "count_below_one")
        self.assertIsNone(invalid_count["estimate"])
        self.assertEqual(invalid_count["raw_estimate"], 0.75)
        for record in ([0, 0, 0, 3], [0, 0, 1, 2]):
            with self.subTest(record=record):
                result = study.factorial_cumulant_M(np.array(record))
                self.assertEqual(result["status"], "moment_sign_invalid")
                self.assertIsNone(result["estimate"])

    def test_exact_moment_guards_accept_boundary_without_integer_overflow(self):
        # N^3 exceeds int64. The same empirical Bernoulli law has M=1,b=0.
        record = np.tile(np.array([0, 0, 0, 1]), 1_000_000)
        result = study.factorial_cumulant_M(record)
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["parameters"], {"M": "1", "p": "1/4", "background": "0"}
        )

    def test_e3_rejects_negative_count_and_impossible_probability(self):
        result = study.calibrated_M(np.array([0, 0, 0, 2]), np.ones(4, dtype=int))
        self.assertEqual(result["status"], "count_below_one")
        self.assertEqual(result["raw_estimate"], -1)
        result = study.calibrated_M(np.array([1, 1]), np.array([0, 1]))
        self.assertEqual(result["status"], "probability_out_of_range")

    def test_e3_requires_nonnegative_calibration_background(self):
        with self.assertRaises(ValueError):
            study.calibrated_M(np.array([0, 1]), np.array([-1, 0]))
        result = study.moment_result(
            Fraction(27, 2),
            Fraction(2, 15),
            Fraction(-1),
            require_nonnegative_background=True,
        )
        self.assertEqual(result["status"], "negative_background")
        self.assertIsNone(result["estimate"])
        self.assertEqual(result["raw_estimate"], 13.5)

    def test_continuous_count_domain_and_zero_source_mean(self):
        result = study.moment_result(
            Fraction(3, 2),
            Fraction(1, 4),
            Fraction(1, 2),
            require_nonnegative_background=True,
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["estimate"], 1.5)
        result = study.calibrated_M(np.array([0, 1]), np.array([0, 1]))
        self.assertEqual(result["status"], "zero_source_mean")

    def test_failure_denominators_preserve_raw_negative_findings(self):
        success = study.factorial_cumulant_M(np.array([0, 0, 1, 1, 2]))
        # Inject a failed result to check diagnostic aggregation independently
        # of the count/probability failure status and conditional summaries.
        failure = study.rejected(
            "probability_out_of_range", 100, inferred_background_negative=True
        )
        result = study.summarize_estimates([success, failure], 2)
        self.assertEqual(
            (result["attempted"], result["successful"], result["failed"]), (2, 1, 1)
        )
        self.assertEqual(result["conditional_mean"], 13.5)
        self.assertEqual(result["raw_finite_summary"]["mean"], 56.75)
        self.assertEqual(result["failure_reasons"], {"probability_out_of_range": 1})
        self.assertEqual(
            result["inferred_background_diagnostics"],
            {"evaluated": 2, "negative": 2, "negative_among_successful": 1},
        )
        json.dumps(result, allow_nan=False)

    def test_e2_raw_summaries_retain_genuine_domain_failures(self):
        records = ([0, 0, 1, 1, 2], [1, 1, 1, 1, 3], [1, 1, 1, 3], [0, 0, 1, 2])
        result = study.summarize_estimates(
            [study.factorial_cumulant_M(np.array(record)) for record in records], 2
        )
        self.assertEqual(
            (result["attempted"], result["successful"], result["failed"]), (4, 1, 3)
        )
        self.assertEqual(
            result["failure_reasons"],
            {
                "count_below_one": 1,
                "moment_sign_invalid": 1,
                "probability_out_of_range": 1,
            },
        )
        self.assertEqual(result["raw_finite_summary"]["count"], 3)
        self.assertAlmostEqual(
            result["raw_finite_summary"]["mean"], (13.5 + 6859 / 10609 + 0.75) / 3
        )
        self.assertEqual(
            result["inferred_background_diagnostics"],
            {"evaluated": 3, "negative": 1, "negative_among_successful": 1},
        )

    def test_all_failed_and_not_run_are_distinct(self):
        failure = study.summarize_estimates([study.rejected("moment_sign_invalid")], 2)
        absent = study.summarize_estimates([], 2)
        self.assertEqual(failure["failed"], 1)
        self.assertEqual(failure["status"], "reported")
        self.assertEqual(absent["status"], "not_run")
        self.assertIsNone(failure["conditional_mean"])
        self.assertIsNone(absent["conditional_mean"])
        json.dumps([failure, absent], allow_nan=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
