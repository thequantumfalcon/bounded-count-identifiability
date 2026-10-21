"""Bounded synthetic factorial-moment experiment, not physical validation.

Python 3.11+ standard library only. Run with a fresh explicit output directory:
    python examples/count_model_stress.py --output /path/to/new/output
The fixed design is retained below; statistical outcomes never gate success.
"""

import argparse
import csv
import hashlib
import json
import platform
import random
import struct
import sys
import time
from array import array
from datetime import datetime, timezone
from fractions import Fraction as F
from math import comb, exp, factorial, isqrt
from pathlib import Path

PROTOCOL_TEXT = """\
{
  "schema_version": 1,
  "experiment": "Finite synthetic factorial-moment stress experiment",
  "status": "FROZEN_BEFORE_SAMPLING",
  "master_seed": 20261021,
  "seed_derivation": "SHA256 of ASCII 'bounded-count-stress-v1|20261021|MODEL|REPETITION|ROLE', interpreted as one unsigned big-endian integer; ROLE is source, rate, or background",
  "repetitions_per_model": 200,
  "windows_per_repetition": 2000,
  "models": [
    {"id": "fixed_baseline", "p": "3/10", "rates": ["1/2"], "weights": ["1"]},
    {"id": "matched_mixture", "p": "3/10", "rates": ["0", "3/5"], "weights": ["1/2", "1/2"]},
    {"id": "matched_poisson", "p": "0", "rates": ["3/5"], "weights": ["1"]}
  ],
  "sampling": {
    "source": "Bernoulli threshold using random.Random.random, with exact endpoint handling",
    "rate": "Threshold selection from the finite weight vector; fresh rate selection for every window",
    "background": "Knuth product sampler with math.exp(-rate); zero rate returns zero without consuming a background variate",
    "independence": "Distinct domain-separated pseudorandom streams for source, rate and background in every model/repetition; intended ideal law is IID windows and independent models/repetitions",
    "limitations": "Pseudorandom finite-precision samples approximate the specified ideal probability laws; neither RNG independence nor sampler distribution is formally verified"
  },
  "data": {
    "format": "One raw unsigned 16-bit little-endian file per model, repetition-major then window-major; manifest specifies shape and SHA256",
    "expected_count_values": 1200000,
    "expected_raw_bytes": 2400000,
    "overflow_policy": "Abort on counts outside 0..65535; never clip or wrap",
    "replicate_summary": "CSV with model, repetition, count, sum of factorial powers 1..3, and maximum count"
  },
  "primary_contrast": {
    "quantity": "Third factorial moment of matched_mixture minus that of matched_poisson",
    "exact_target": "27/500",
    "reason": "The two models have equal first and second factorial moments; compare unbiased factorial moments, not a biased plug-in cumulant",
    "failure_probability_allocation": "1/40"
  },
  "uncertainty": {
    "total_family_failure_bound": "1/20",
    "nine_individual_means_failure_allocation_each": "1/360",
    "method": "Use exact prescribed-law factorial moments through order 6 and the falling-factorial product identity to derive variance. For each unbiased mean use radius sqrt(variance/(400000*allocated_alpha)); the contrast variance is the sum for the two independent models. Chebyshev and a union bound give ideal-model simultaneous coverage at least 0.95 for these ten preselected targets",
    "square_root_enclosure": "Outward rational enclosure with denominator 10^12, upper endpoint used for confidence radius",
    "replicate_descriptors": "Per-model sample variance, minimum and maximum of the 200 replicate factorial-moment estimates; descriptive checks, not claimed additional coverage guarantees",
    "prohibited_inference": "Do not apply the repository's fixed-rate Bernoulli-Poisson confidence ceilings to the mixture; derive each synthetic-law variance separately"
  },
  "controls": [
    "Deterministic Bernoulli p=0 and p=1 endpoint controls",
    "Deterministic Poisson zero-rate and prescribed uniform-sequence controls for outputs 0, 1 and 2",
    "Rate-selector threshold boundaries, including the half-weight boundary",
    "Exact independent formal-generating-series coefficient calculation against mixture factorial-moment formulas through order 6",
    "Falling-factorial product identities checked as exact polynomial values for orders 1..3 at counts 0..12",
    "Deliberately incorrect mean-rate replacement for mixture second factorial moment must be rejected",
    "Deliberately deterministic rounded-rate Poisson sampler must fail prescribed-sequence controls",
    "Every derived stream seed must be distinct",
    "Independent binary-file readback recomputes all saved integer factorial-moment sums and file hashes"
  ],
  "resource_limits": {
    "counts": 1200000,
    "process_deadline_seconds": 180,
    "memory_plan": "Process one 2000-window repetition at a time; keep only integer sums and 600 summary rows",
    "execution_policy": "Standard-library only, no network, services, hardware access, accelerator or paid resources"
  },
  "reporting": "Retain any technical failure and any statistical noncoverage or nondetection. Do not resample, tune seed, change sample size after observation, or replace an unfavorable result. This is synthetic finite evidence, not physical validation, new mathematics, universal proof or outside independent review"
}
"""
PROTOCOL_SHA256 = "b802bf6367fffda0a7540a6fb68c2bdd6fcd4a8597afbcbfdc338419f4dc683c"
ORIGINAL_PROTOCOL_FREEZE_UTC = "2026-10-21T20:28:21.457253+00:00"
MODEL_KEYS = ("fixed_baseline", "matched_mixture", "matched_poisson")
ROLES = ("source", "rate", "background")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exact(value):
    value = F(value)
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def descending(n, order):
    value = 1
    for i in range(order):
        value *= n - i
    return value


def moments(model, order=6):
    p = F(model["p"])
    rates, weights = list(map(F, model["rates"])), list(map(F, model["weights"]))
    return [F(1)] + [
        sum((w * (r**k + k * p * r ** (k - 1)) for w, r in zip(weights, rates)), F(0))
        for k in range(1, order + 1)
    ]


def series_moments(model, order=6):
    """Separately multiply factorial-generating series, then read coefficients."""
    polynomial = [F(0)] * (order + 1)
    for weight, rate in zip(map(F, model["weights"]), map(F, model["rates"])):
        exponential = [F(1)]
        for k in range(1, order + 1):
            exponential.append(exponential[-1] * rate / k)
        for source_order, mass in enumerate([F(1), F(model["p"])]):
            for background_order in range(order + 1 - source_order):
                polynomial[source_order + background_order] += (
                    weight * mass * exponential[background_order]
                )
    return [value * factorial(k) for k, value in enumerate(polynomial)]


def statistic_variance(values, order):
    second = sum(
        (
            comb(order, j) ** 2 * factorial(j) * values[2 * order - j]
            for j in range(order + 1)
        ),
        F(0),
    )
    return second - values[order] ** 2


def sqrt_enclosure(value, digits=12):
    value = F(value)
    require(value >= 0, "nonnegative square-root argument")
    scale = 10**digits
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    lower = F(floor, scale)
    upper = lower if lower * lower == value else F(floor + 1, scale)
    require(lower * lower <= value <= upper * upper, "outward square-root enclosure")
    return lower, upper


def sample_bernoulli(p, rng):
    if p == 0:
        return 0
    if p == 1:
        return 1
    return int(rng.random() < p)


def sample_rate(rates, weights, rng):
    if len(rates) == 1:
        return rates[0]
    u = rng.random()
    cumulative = 0.0
    for rate, weight in zip(rates[:-1], weights[:-1]):
        cumulative += weight
        if u < cumulative:
            return rate
    return rates[-1]


def sample_poisson(rate, rng):
    if rate == 0:
        return 0
    limit, product, draws = exp(-rate), 1.0, 0
    while product > limit:
        draws += 1
        require(
            draws <= 65536,
            "Poisson sampler exceeds representable count; abort, not clip",
        )
        product *= rng.random()
    return draws - 1


class FixedUniforms:
    def __init__(self, values):
        self.values = iter(values)

    def random(self):
        return next(self.values)


def poisson_controls(sampler):
    require(sampler(0, FixedUniforms([])) == 0, "zero-rate sampler")
    for uniforms, expected in [([0.2], 0), ([0.9, 0.5], 1), ([0.9, 0.9, 0.5], 2)]:
        require(
            sampler(0.5, FixedUniforms(uniforms)) == expected,
            "prescribed Poisson uniforms",
        )


def preflight(models):
    require(sample_bernoulli(0, FixedUniforms([])) == 0, "Bernoulli zero endpoint")
    require(sample_bernoulli(1, FixedUniforms([])) == 1, "Bernoulli one endpoint")
    require(sample_bernoulli(0.5, FixedUniforms([0.49])) == 1, "Bernoulli lower side")
    require(sample_bernoulli(0.5, FixedUniforms([0.5])) == 0, "Bernoulli threshold")
    poisson_controls(sample_poisson)
    for u, expected in [(0, 0), (0.49, 0), (0.5, 0.6), (0.999, 0.6)]:
        require(
            sample_rate([0, 0.6], [0.5, 0.5], FixedUniforms([u])) == expected,
            "mixture threshold",
        )
    exact_moments = {}
    for model in models:
        require(sum(map(F, model["weights"])) == 1, "normalized weights")
        require(all(F(w) >= 0 for w in model["weights"]), "nonnegative weights")
        require(all(F(r) >= 0 for r in model["rates"]), "nonnegative rates")
        require(0 <= F(model["p"]) <= 1, "valid source parameter")
        values = moments(model)
        require(
            values == series_moments(model), "separate exact generating-series control"
        )
        require(
            all(statistic_variance(values, k) >= 0 for k in (1, 2, 3)),
            "nonnegative statistic variances",
        )
        exact_moments[model["id"]] = values
    require(
        exact_moments["fixed_baseline"][1:4] == [F(4, 5), F(11, 20), F(7, 20)],
        "known baseline moments",
    )
    require(
        exact_moments["matched_mixture"][1:3]
        == exact_moments["matched_poisson"][1:3]
        == [F(3, 5), F(9, 25)],
        "matched population moments",
    )
    require(
        exact_moments["matched_mixture"][3] - exact_moments["matched_poisson"][3]
        == F(27, 500),
        "known third-order gap",
    )
    for r in (1, 2, 3):
        for s in (1, 2, 3):
            for n in range(13):
                right = sum(
                    comb(r, j) * comb(s, j) * factorial(j) * descending(n, r + s - j)
                    for j in range(min(r, s) + 1)
                )
                require(
                    descending(n, r) * descending(n, s) == right,
                    "factorial product identity control",
                )
    # Expected deterministic rejection: neither control depends on a favorable draw.
    rejected_sampler = False
    try:
        poisson_controls(lambda rate, rng: round(rate))
    except AssertionError:
        rejected_sampler = True
    require(rejected_sampler, "faulty rounded-rate sampler must be detected")
    wrong_mixture_second = F(3, 10) ** 2 + 2 * F(3, 10) * F(3, 10)
    rejected_formula = False
    try:
        require(
            wrong_mixture_second == exact_moments["matched_mixture"][2],
            "missing mixture-rate variance",
        )
    except AssertionError:
        rejected_formula = True
    require(rejected_formula, "faulty fixed-rate formula must be detected")
    return exact_moments, {
        "status": "PASS",
        "factorial_product_value_checks": 117,
        "generating_series_comparisons": 21,
        "faulty_sampler_detected": True,
        "faulty_mean_rate_replacement_detected": True,
        "scope": "Deterministic selected controls, not exhaustive sampler verification",
    }


def stream_seed(master, model, repetition, role):
    text = f"bounded-count-stress-v1|{master}|{model}|{repetition}|{role}"
    return int.from_bytes(hashlib.sha256(text.encode("ascii")).digest(), "big")


def interval_record(estimate, population, variance_of_estimate, alpha):
    low_radius, radius = sqrt_enclosure(variance_of_estimate / alpha)
    lower, upper = estimate - radius, estimate + radius
    return {
        "estimate": exact(estimate),
        "population_target": exact(population),
        "ideal_iid_estimator_variance": exact(variance_of_estimate),
        "allocated_failure_probability": exact(alpha),
        "radius_enclosure": [exact(low_radius), exact(radius)],
        "interval": [exact(lower), exact(upper)],
        "population_target_inside": lower <= population <= upper,
        "zero_inside": lower <= 0 <= upper,
    }


def run(destination):
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    protocol_bytes = PROTOCOL_TEXT.encode("utf-8")
    protocol = json.loads(PROTOCOL_TEXT)
    require(sha(protocol_bytes) == PROTOCOL_SHA256, "embedded frozen protocol changed")
    freeze = {
        "design_sha256": PROTOCOL_SHA256,
        "originally_frozen_utc": ORIGINAL_PROTOCOL_FREEZE_UTC,
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "sampling_started": False,
    }
    deadline = wall_start + protocol["resource_limits"]["process_deadline_seconds"]

    def check_deadline():
        if time.perf_counter() > deadline:
            raise TimeoutError("180-second cooperative process deadline exceeded")

    require(
        tuple(model["id"] for model in protocol["models"]) == MODEL_KEYS, "model order"
    )
    repetitions, windows = (
        protocol["repetitions_per_model"],
        protocol["windows_per_repetition"],
    )
    require(
        (repetitions, windows) == (200, 2000), "frozen repetition and window budget"
    )
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "executed-program.py").write_bytes(Path(__file__).read_bytes())
    (destination / "design.json").write_bytes(protocol_bytes)
    (destination / "design-freeze.json").write_text(
        json.dumps(freeze, indent=2) + "\n", encoding="utf-8"
    )
    report = {
        "status": "TECHNICAL_FAILURE",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "design_sha256": freeze["design_sha256"],
        "program_sha256": sha(Path(__file__).read_bytes()),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "actual_sampled_counts": 0,
    }
    (destination / "execution-start.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    try:
        population, control_report = preflight(protocol["models"])
        report["controls"] = control_report
        seeds = [
            stream_seed(protocol["master_seed"], model, r, role)
            for model in MODEL_KEYS
            for r in range(repetitions)
            for role in ROLES
        ]
        require(
            len(set(seeds)) == len(seeds) == 1800,
            "unique domain-separated stream seeds",
        )
        rows, files, summaries = [], [], {}
        with (destination / "stream-seeds.csv").open(
            "w", newline="", encoding="utf-8"
        ) as stream:
            writer = csv.writer(stream)
            writer.writerow(["model", "repetition", "role", "seed_hex"])
            for model in MODEL_KEYS:
                for rep in range(repetitions):
                    for role in ROLES:
                        writer.writerow(
                            [
                                model,
                                rep,
                                role,
                                f"{stream_seed(protocol['master_seed'], model, rep, role):064x}",
                            ]
                        )
        report["sampling_started_utc"] = datetime.now(timezone.utc).isoformat()
        for model in protocol["models"]:
            key = model["id"]
            p = float(F(model["p"]))
            rates, weights = (
                [float(F(s)) for s in model["rates"]],
                [float(F(s)) for s in model["weights"]],
            )
            model_rows, totals, maximum = [], [0, 0, 0], 0
            counts_path = destination / (key + ".counts.u16le")
            with counts_path.open("wb") as stream:
                for rep in range(repetitions):
                    check_deadline()
                    rng = {
                        role: random.Random(
                            stream_seed(protocol["master_seed"], key, rep, role)
                        )
                        for role in ROLES
                    }
                    block, sums, largest = array("H"), [0, 0, 0], 0
                    require(block.itemsize == 2, "native unsigned short width")
                    for _ in range(windows):
                        rate = sample_rate(rates, weights, rng["rate"])
                        count = sample_bernoulli(p, rng["source"]) + sample_poisson(
                            rate, rng["background"]
                        )
                        require(
                            0 <= count <= 65535,
                            "count overflow; abort without clipping",
                        )
                        block.append(count)
                        first, second, third = (
                            count,
                            count * (count - 1),
                            count * (count - 1) * (count - 2),
                        )
                        for i, value in enumerate((first, second, third)):
                            sums[i] += value
                        largest = max(largest, count)
                    if sys.byteorder != "little":
                        block.byteswap()
                    stream.write(block.tobytes())
                    row = {
                        "model": key,
                        "repetition": rep,
                        "count": windows,
                        "sum_factorial_1": sums[0],
                        "sum_factorial_2": sums[1],
                        "sum_factorial_3": sums[2],
                        "maximum": largest,
                    }
                    rows.append(row)
                    model_rows.append(row)
                    totals = [a + b for a, b in zip(totals, sums)]
                    maximum = max(maximum, largest)
                    report["actual_sampled_counts"] += windows
            files.append(
                {
                    "path": counts_path.name,
                    "sha256": sha(counts_path.read_bytes()),
                    "bytes": counts_path.stat().st_size,
                    "shape": [repetitions, windows],
                    "dtype": "unsigned 16-bit little-endian",
                    "maximum": maximum,
                }
            )
            # Independent struct-based block readback, not array conversion.
            with counts_path.open("rb") as stream:
                for row in model_rows:
                    check_deadline()
                    block = stream.read(2 * windows)
                    require(len(block) == 2 * windows, "complete binary repetition")
                    values = [item[0] for item in struct.iter_unpack("<H", block)]
                    for order in (1, 2, 3):
                        require(
                            sum(descending(value, order) for value in values)
                            == row[f"sum_factorial_{order}"],
                            "binary readback factorial sums",
                        )
                    require(max(values) == row["maximum"], "binary readback maximum")
                require(stream.read(1) == b"", "no trailing binary data")
            require(
                sha(counts_path.read_bytes()) == files[-1]["sha256"],
                "independent readback file hash",
            )
            estimates = [F(total, repetitions * windows) for total in totals]
            target_values = population[key]
            summary = {
                "model": model,
                "count": repetitions * windows,
                "population_factorial_moments_0_to_6": [
                    exact(x) for x in target_values
                ],
                "factorial_moments": [],
            }
            for order in (1, 2, 3):
                variance = statistic_variance(target_values, order)
                rep_estimates = [
                    F(row[f"sum_factorial_{order}"], windows) for row in model_rows
                ]
                observed_rep_variance = sum(
                    ((x - estimates[order - 1]) ** 2 for x in rep_estimates), F(0)
                ) / (repetitions - 1)
                entry = interval_record(
                    estimates[order - 1],
                    target_values[order],
                    variance / (repetitions * windows),
                    F(1, 360),
                )
                entry.update(
                    {
                        "order": order,
                        "ideal_single_window_variance": exact(variance),
                        "replicate_descriptors": {
                            "sample_variance": exact(observed_rep_variance),
                            "ideal_rep_mean_variance": exact(variance / windows),
                            "minimum": exact(min(rep_estimates)),
                            "maximum": exact(max(rep_estimates)),
                        },
                    }
                )
                summary["factorial_moments"].append(entry)
            summaries[key] = summary
        with (destination / "replicate-statistics.csv").open(
            "w", newline="", encoding="utf-8"
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

        def estimate_for(key):
            q = summaries[key]["factorial_moments"][2]["estimate"]
            return F(q["numerator"], q["denominator"])

        gap = estimate_for("matched_mixture") - estimate_for("matched_poisson")
        contrast_variance = sum(
            (
                statistic_variance(population[key], 3)
                for key in ("matched_mixture", "matched_poisson")
            ),
            F(0),
        ) / (repetitions * windows)
        contrast = interval_record(gap, F(27, 500), contrast_variance, F(1, 40))
        all_covered = (
            all(
                item["population_target_inside"]
                for summary in summaries.values()
                for item in summary["factorial_moments"]
            )
            and contrast["population_target_inside"]
        )
        require(
            report["actual_sampled_counts"] == 1200000, "complete frozen data budget"
        )
        require(sum(item["bytes"] for item in files) == 2400000, "frozen data size")
        require(
            sha((destination / "design.json").read_bytes()) == freeze["design_sha256"],
            "protocol unchanged after execution",
        )
        require(
            sha(Path(__file__).read_bytes()) == report["program_sha256"],
            "program unchanged after execution",
        )
        report.update(
            {
                "status": "COMPLETE",
                "models": summaries,
                "data_files": files,
                "primary_contrast": contrast,
                "all_ten_population_targets_inside_benchmark_intervals": all_covered,
                "primary_contrast_interval_excludes_zero": not contrast["zero_inside"],
                "ideal_iid_total_failure_probability_allocation": exact(
                    F(1, 40) + 9 * F(1, 360)
                ),
                "replicate_rows": len(rows),
                "binary_readback_passed": True,
                "deadline_policy": "Cooperative 180-second check between bounded sampling/readback blocks; CI also applies an external job timeout.",
                "limitations": [
                    "Synthetic counts only; no instrument, external dataset or measured physical validation.",
                    "Ideal-IID Chebyshev benchmark bounds use exact prescribed-law variances, not fixed-rate ceilings for mixtures.",
                    "These benchmarks know the generating-law variances; they are not data-derived variance bounds or an unknown-law confidence procedure.",
                    "The union bound does not require independence among the ten interval events; variance calculations use the prescribed independent-window/model benchmark.",
                    "Deterministic PRNG seeds and distinct streams do not prove independence; float Knuth draws approximate the ideal probability law.",
                    "No empirical plug-in cumulants are computed. The primary statistic is an unbiased factorial-moment difference under the ideal model.",
                    "Finite testing and selected deterministic fault controls are not universal proof, optimality, outside independent review or formal executable verification.",
                ],
            }
        )
    except Exception as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["wall_seconds"] = time.perf_counter() - wall_start
        report["cpu_seconds"] = time.process_time() - cpu_start
        report["artifact_files"] = [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha(path.read_bytes()),
            }
            for path in sorted(destination.iterdir())
            if path.is_file() and path.name != "result.json"
        ]
        (destination / "result.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Fresh output directory; existing directories are rejected.",
    )
    args = parser.parse_args()
    result = run(args.output.resolve())
    print(
        json.dumps(
            {
                "status": result["status"],
                "counts": result["actual_sampled_counts"],
                "wall_seconds": result["wall_seconds"],
                "primary_contrast": result["primary_contrast"],
                "all_targets_covered": result[
                    "all_ten_population_targets_inside_benchmark_intervals"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
