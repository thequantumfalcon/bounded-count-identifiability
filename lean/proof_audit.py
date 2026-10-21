"""Shared root registry and defensive proof-audit policy.

Generated import-only queries run separately from source elaboration. This is
not an untrusted-code sandbox: Lean, imported dependencies and this runner are
trusted. Kernel replay is a separate, complementary check.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Callable, Sequence

CORE = (
    "CountSeriesCore",
    "CountLawEncoding",
    "CountIdentification",
    "CountPoissonChannel",
    "CountObservedIdentification",
    "CountSharpness",
)

CORE_ROOTS = {
    "CountSeriesCore": (
        "CountSeriesCore.derivative_logOf_mul",
        "CountSeriesCore.tilt_jet_of_log_coefficients",
        "CountSeriesCore.bounded_nonnegative_series_identified",
    ),
    "CountLawEncoding": (
        "BoundedCountLaw.factorialPGF_constant",
        "BoundedCountLaw.factorialPGF_coeff_nonneg",
        "BoundedCountLaw.factorialPGF_coeff_above",
        "BoundedCountLaw.factorialPGF_injective_on_support",
    ),
    "CountIdentification": ("BoundedCountLaw.higher_factorial_cumulants_identify",),
    "CountPoissonChannel": (
        "CountPoissonChannel.derivative_logOf_channel",
        "CountPoissonChannel.higher_factorialCumulant_channel",
        "CountPoissonChannel.first_factorialCumulant_channel",
        "CountPoissonChannel.bounded_sources_identified_under_unknown_factors",
    ),
    "CountObservedIdentification": (
        "BoundedCountLaw.first_law_cumulant_eq_mean",
        "BoundedCountLaw.observed_higher_cumulants_identify_source",
        "BoundedCountLaw.observed_cumulants_identify_source_and_background",
    ),
    "CountSharpness": (
        "CountSharpness.truncatedExp_higher_cumulants_zero",
        "CountSharpness.truncatedExp_top_cumulant",
        "CountSharpness.alternatingExpSum_pos",
        "CountSharpness.sharpLaw_isBoundedLaw",
        "CountSharpness.sharpLaw_higher_cumulants_zero",
        "CountSharpness.sharpLaw_top_cumulant",
        "CountSharpness.cutoff_is_sharp",
        "CountSharpness.lower_observed_cumulants_match",
    ),
}

ROOTS = {
    "CountD1Stability": (
        "squared_parameter_error_le",
        "parameter_error_le_sqrt",
        "parameter_error_from_cumulant",
        "background_error_le",
        "bounded_observation_error",
    ),
    "CountD1LawBridge": (
        "sharpLaw_one_eq_bernoulliMass",
        "bernoulliMass_isBoundedLaw",
        "bernoulli_second_cumulant",
        "bernoulli_parameter_stability",
        "observed_bernoulli_cumulants",
        "observed_bernoulli_stability",
    ),
}

RESEARCH_ROOTS = {
    "CountProbabilityBridge": (
        "boundedPMF_mass",
        "boundedMeasure_isProbability",
        "boundedMeasure_singleton",
        "integral_boundedMeasure",
        "factorialPGF_eval_eq_expectation",
        "factorialPGF_coeff_eq_binomial_expectation",
        "higher_factorial_cumulants_identify_measures",
    ),
    "CountD1VarianceCoverage": (
        "factorial_square_identity",
        "first_variance_identity",
        "second_variance_identity",
        "first_variance_ceiling",
        "second_variance_ceiling",
        "variance_ratio_radius",
        "zero_variance_deterministic",
        "simultaneous_chebyshev",
        "conditional_moment_coverage",
    ),
    "CountD1BackgroundUncertainty": (
        "perturbation_difference_le",
        "square_difference_le",
        "parameter_error_le",
        "bounded_observation_error",
        "equal_cumulant_witness",
    ),
    "CountFiniteSampleMean": (
        "sampleMean_memLp",
        "sampleMean_unbiased",
        "sampleMean_variance",
        "sampleMean_variance_ceiling",
        "two_sample_means_coverage",
    ),
    "CountConfidenceZeroAndTransforms": (
        "pairwise_indepFun_measurable_transform",
        "pairwise_indepFun_factorial",
        "nonnegative_ceiling_tail",
        "simultaneous_nonnegative_ceiling_coverage",
        "two_sample_means_coverage_nonnegative",
        "factorial_sample_means_coverage",
    ),
    "PoissonMGFV1": (
        "poisson_exp_integrable",
        "poisson_exp_integral",
    ),
    "CountPoissonObservation": (
        "bounded_exp_integrable",
        "bounded_exp_integral",
        "observed_exp_integrable",
        "observed_exp_integral",
        "observed_factorialPGF_integrable",
        "observed_factorialPGF_integral",
        "independentPairMeasure_isProbability",
        "independentPairMeasure_hasLaws",
        "independentPairMeasure_factorialPGF",
    ),
    "CountTaylorJetFoundation": (
        "coeff_jet0",
        "derivative_jet0",
        "jet0_congr_eventuallyEq",
    ),
    "CountTaylorJetProduct": ("jet0_mul",),
    "CountAnalyticCumulantBridge": (
        "polynomial_contDiff",
        "iteratedDeriv_polynomial",
        "jet0_polynomial",
        "jet0_log_polynomial",
        "factorialCumulant_polynomial_eq_iteratedDeriv_log",
        "factorialCumulant_channel_eq_iteratedDeriv_log",
        "lawFactorialCumulant_eq_iteratedDeriv_log",
        "observedFactorialCumulant_eq_iteratedDeriv_log",
        "lawFactorialCumulant_eq_iteratedDeriv_log_expectation",
        "observedFactorialCumulant_eq_iteratedDeriv_log_expectation",
        "independentPairMeasure_cumulant_eq_iteratedDeriv_log_expectation",
        "observed_log_derivatives_identify_source",
        "observed_log_derivatives_identify_source_and_background",
    ),
    "CountConfidenceProjection": (
        "feasible_iff_mean",
        "feasible_iff_polynomialBounds",
        "feasible_iff_closed_bounds",
        "exists_feasible_iff",
        "empty_of_reversed_mean",
        "empty_of_reversed_second",
        "empty_of_sq_upper_lt_lower",
        "feasible_zero_iff",
        "feasible_zero_clipped_iff",
        "exists_feasible_zero_clipped_iff",
        "model_ranges",
        "feasible_clip_iff",
        "empty_of_negative_ceiling",
        "exists_feasible_positive_iff",
        "projection_positive",
        "projection_zero",
    ),
    "PoissonFactorialMomentsV1": (
        "poisson_descFactorial_integrable",
        "poisson_descFactorial_integral",
        "poisson_memLp",
        "observed_pow_integrable",
        "observed_memLp",
        "observed_factorial_two_memLp",
        "fin_two_poisson_descFactorial",
        "bernoulli_poisson_descFactorial",
    ),
    "BernoulliPoissonStatisticsV1": (
        "count_memLp",
        "factorial_two_memLp",
        "first_four_factorial_moments",
        "means_and_variances",
        "sample_means_coverage",
        "projected_region_coverage",
    ),
    "CountFiniteMixedPoisson": (
        "mixture_isProbability",
        "mixture_factorial",
        "rateVariance_nonneg",
        "rateVariance_eq",
        "mixture_mean",
        "mixture_second",
        "rateVariance_le_range",
        "mixture_stability",
    ),
}

DIRECTORIES = {
    "CountD1Stability": "d1",
    "CountD1LawBridge": "d1-law",
    "CountProbabilityBridge": "probability",
    "CountD1VarianceCoverage": "finite-sample",
    "CountD1BackgroundUncertainty": "background-uncertainty",
    "CountFiniteSampleMean": "sample-mean",
    "CountConfidenceZeroAndTransforms": "confidence-zero",
    "PoissonMGFV1": "poisson-mgf",
    "CountPoissonObservation": "poisson-observation",
    "CountTaylorJetFoundation": "taylor-jet",
    "CountTaylorJetProduct": "taylor-product",
    "CountAnalyticCumulantBridge": "analytic-cumulant",
    "CountConfidenceProjection": "confidence-projection",
    "PoissonFactorialMomentsV1": "poisson-factorial-moments",
    "BernoulliPoissonStatisticsV1": "bernoulli-poisson-statistics",
    "CountFiniteMixedPoisson": "finite-mixture",
}

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def full_roots(module: str) -> list[str]:
    if module in CORE_ROOTS:
        return list(CORE_ROOTS[module])
    return [module + "." + name for name in (ROOTS | RESEARCH_ROOTS)[module]]


def strip_lean_comments_and_strings(text: str) -> str:
    """Small defensive lexer, not a replacement for Lean's parser."""
    output = []
    index = depth = 0
    while index < len(text):
        pair = text[index : index + 2]
        if depth:
            if pair == "/-":
                depth += 1
                index += 2
            elif pair == "-/":
                depth -= 1
                index += 2
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif pair == "/-":
            depth = 1
            output.append(" ")
            index += 2
        elif pair == "--":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            output.append(" ")
        elif text[index] == '"':
            index += 1
            closed = False
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                elif text[index] == '"':
                    index += 1
                    closed = True
                    break
                else:
                    index += 1
            if not closed:
                raise ValueError("Unclosed source string")
            output.append(" ")
        else:
            output.append(text[index])
            index += 1
    if depth:
        raise ValueError("Unclosed source comment")
    return "".join(output)


PROHIBITED = re.compile(
    r"\b(?:sorry|admit|sorryAx|native_decide|axiom|run_cmd|run_elab|run_meta|"
    r"elab|elab_rules|macro|macro_rules|syntax|initialize|builtin_initialize|"
    r"addDecl|implemented_by|extern|unsafe|opaque|set_option)\b|#\s*eval\b"
)


def validate_source(source: str) -> None:
    code = strip_lean_comments_and_strings(source)
    if PROHIBITED.search(code) or "«" in code or "»" in code:
        raise ValueError("Source violates the project's proof/admission policy")
    if any(ord(c) < 32 and c not in "\t\r\n" for c in code):
        raise ValueError("Control character in proof source")


def audit_source(module: str, roots: Sequence[str]) -> str:
    names = [module, *roots]
    if (
        not roots
        or len(set(roots)) != len(roots)
        or any(
            not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*", n)
            for n in names
        )
    ):
        raise ValueError("Invalid audit module/root names")
    return (
        "import "
        + module
        + "\n\n"
        + "".join("#print axioms " + root + "\n" for root in roots)
    )


AXIOM_RECORD = re.compile(
    r"'([^'\r\n]+)' (?:depends on axioms: \[([^\]]*)\]|"
    r"does not depend on any axioms)"
)


def parse_axioms(stdout: str, roots: Sequence[str]) -> dict[str, list[str]]:
    """Require complete unique roots, permitted subsets, and no extra output."""
    found: dict[str, list[str]] = {}
    cursor = 0
    for match in AXIOM_RECORD.finditer(stdout):
        if stdout[cursor : match.start()].strip():
            raise ValueError("Unexpected output in generated axiom query")
        name, raw = match.groups()
        if name in found:
            raise ValueError("Duplicate theorem in axiom query")
        axioms = (
            []
            if raw is None or not raw.strip()
            else [item.strip() for item in raw.split(",")]
        )
        if len(set(axioms)) != len(axioms) or not set(axioms) <= ALLOWED_AXIOMS:
            raise ValueError("Unexpected or duplicate axiom")
        found[name] = axioms
        cursor = match.end()
    if stdout[cursor:].strip() or list(found) != list(roots) or not roots:
        raise ValueError("Missing, reordered or unexpected theorem roots/output")
    return found


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_axiom_audit(
    lean: Path,
    module: str,
    roots: Sequence[str],
    output: Path,
    env: dict[str, str],
    sanitize: Callable[[bytes], str],
    timeout: int = 240,
) -> dict:
    query = output / (module + ".audit.lean")
    stdout_path = output / (module + ".audit.stdout.txt")
    stderr_path = output / (module + ".audit.stderr.txt")
    record_path = output / (module + ".audit.json")
    if any(path.exists() for path in (query, stdout_path, stderr_path, record_path)):
        raise ValueError("Axiom audit output must be fresh")
    expected = audit_source(module, roots).encode("utf-8")
    query.write_bytes(expected)
    command = [str(lean), "--trust=0", query.name]
    timed_out = False
    try:
        result = subprocess.run(
            command,
            cwd=output,
            env=env,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        timed_out = True
        result = subprocess.CompletedProcess(
            command, 124, error.stdout or b"", error.stderr or b""
        )
    stdout, stderr = sanitize(result.stdout), sanitize(result.stderr)
    stdout_path.write_bytes(stdout.encode("utf-8"))
    stderr_path.write_bytes(stderr.encode("utf-8"))
    try:
        printed = parse_axioms(stdout, roots)
        parsed = True
    except ValueError:
        printed, parsed = {}, False
    checks = {
        "exit_zero": result.returncode == 0,
        "not_timed_out": not timed_out,
        "query_unchanged": query.is_file() and query.read_bytes() == expected,
        "exact_roots_and_allowed_axioms": parsed,
        "empty_stderr": not stderr.strip(),
    }
    record = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "module": module,
        "roots": list(roots),
        "exit_code": result.returncode,
        "timed_out": timed_out,
        "query_sha256": hashlib.sha256(expected).hexdigest(),
        "stdout_sha256": digest(stdout_path),
        "stderr_sha256": digest(stderr_path),
        "printed_axiom_lists": printed,
        "checks": checks,
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def validate_audit_record(
    output: Path,
    module: str,
    roots: Sequence[str],
    record: dict,
) -> dict[str, Path]:
    if not isinstance(record, dict):
        raise ValueError("Missing axiom audit record")
    paths = {
        "query": output / (module + ".audit.lean"),
        "stdout": output / (module + ".audit.stdout.txt"),
        "stderr": output / (module + ".audit.stderr.txt"),
        "record": output / (module + ".audit.json"),
    }
    if (
        record.get("status") != "PASS"
        or record.get("module") != module
        or record.get("roots") != list(roots)
        or record.get("exit_code") != 0
        or record.get("timed_out") is not False
        or set(record.get("checks", {}))
        != {
            "exit_zero",
            "not_timed_out",
            "query_unchanged",
            "exact_roots_and_allowed_axioms",
            "empty_stderr",
        }
        or not all(value is True for value in record["checks"].values())
        or not all(path.is_file() for path in paths.values())
    ):
        raise ValueError("Failed or incomplete axiom audit record")
    if paths["query"].read_bytes() != audit_source(module, roots).encode("utf-8"):
        raise ValueError("Generated query changed")
    for kind in ("query", "stdout", "stderr"):
        if digest(paths[kind]) != record.get(kind + "_sha256"):
            raise ValueError("Axiom audit evidence changed")
    if paths["stderr"].read_text(encoding="utf-8").strip():
        raise ValueError("Axiom audit stderr is not empty")
    parsed = parse_axioms(paths["stdout"].read_text(encoding="utf-8"), roots)
    if (
        parsed != record.get("printed_axiom_lists")
        or json.loads(paths["record"].read_text(encoding="utf-8")) != record
    ):
        raise ValueError(
            "Stored audit record does not match independently read evidence"
        )
    return paths
