"""Synthetic emitter simulations and approximate fixed-pair testing calculations.

Parameters (M,p) follow the cited studies; backgrounds and source-off windows
are synthetic additions, not measurements or a reanalysis of published data.
E1 fits a pure binomial on an explicitly bounded integer search. E2 and E3 are
continuous moment estimates with exact count/probability checks. E2 retains an
inferred-background diagnostic; E3 also checks its calibrated background.
Summaries are conditional on successful fits and always give failure denominators.
Cancellation is displayed as median and interquartile range; its mean and RMSE
are unstable tail diagnostics retained in the JSON output.

The testing calculations evaluate explicit candidate alternatives. Numerical
search is not a global-optimum certificate; the reported necessary counts are
high-precision approximations, not achievable sample sizes or certified bounds.
Use CPython 3.13 and the hash-locked requirements-emitters.txt. The full fixed-seed
200-repetition study takes several minutes. See docs/emitter-counting.md for
primary references, equations, assumptions and limitations.
"""

import argparse
from collections import Counter
from fractions import Fraction
import json
import math

import numpy as np
from scipy.special import gammaln, xlog1py, xlogy

from emitter_background_cost import metadata, search_known, search_pair

PUBLISHED = ((40, 0.2), (100, 0.1), (8, 0.1))
SEED = 2026
REPS = 200
PULSES = (10**4, 10**5, 10**6)
BACKGROUNDS = (0.0, 0.1, 0.5, 1.0)
E1_SEARCH_SPAN = 400


def count_summary(y):
    """Exact integer summaries, avoiding overflow in moment-polynomial products."""
    y = np.asarray(y)
    if y.ndim != 1 or len(y) == 0:
        raise ValueError("A count record must be a nonempty vector.")
    if y.dtype.kind not in "iu" or np.any(y < 0):
        raise ValueError("Count records must contain nonnegative integers.")
    # The histogram avoids million-element Python loops; conversion to Python int
    # occurs before powers/products. The configured synthetic counts are small.
    values, counts = np.unique(y, return_counts=True)
    pairs = [(int(value), int(count)) for value, count in zip(values, counts)]
    return {
        "N": len(y),
        "pairs": pairs,
        "s1": sum(value * count for value, count in pairs),
        "s2": sum(value * (value - 1) * count for value, count in pairs),
        "s3": sum(value * (value - 1) * (value - 2) * count for value, count in pairs),
    }


def rejected(status, raw_estimate=None, **diagnostics):
    return dict(status=status, estimate=None, raw_estimate=raw_estimate, **diagnostics)


def moment_result(M, p, b, *, require_nonnegative_background):
    """Exact estimator-specific guards; M remains a continuous moment estimate."""
    raw = float(M)
    parameters = {"M": str(M), "p": str(p), "background": str(b)}
    if not 0 < p <= 1:
        return rejected("probability_out_of_range", raw, parameters=parameters)
    if require_nonnegative_background and b < 0:
        return rejected("negative_background", raw, parameters=parameters)
    if M < 1:
        return rejected("count_below_one", raw, parameters=parameters)
    return dict(status="success", estimate=raw, raw_estimate=raw, parameters=parameters)


def mle_binomial_M(y, search_span=E1_SEARCH_SPAN, summary=None):
    """E1: best fit within [max(1,max(y)), max(y)+search_span-1].

    A cap hit is reported as an unresolved search, not a finite unrestricted MLE.
    Endpoints p=1 are included. An all-zero record leaves M unidentified at p=0.
    No global-optimum certificate is claimed even for an interior selected fit.
    """
    if not isinstance(search_span, int) or search_span < 2:
        raise ValueError("Use an integer search span of at least two.")
    summary = count_summary(y) if summary is None else summary
    size, s1, pairs = summary["N"], summary["s1"], summary["pairs"]
    if s1 == 0:
        return rejected("unidentified_zero_record")
    mean = s1 / size
    observed_max = pairs[-1][0]
    lower, upper = max(1, observed_max), observed_max + search_span - 1
    candidates = np.arange(lower, upper + 1, dtype=float)
    p = mean / candidates
    k = np.array([value for value, _ in pairs], dtype=float)[None, :]
    frequencies = np.array([count for _, count in pairs])
    m = candidates[:, None]
    log_prob = (
        gammaln(m + 1)
        - gammaln(k + 1)
        - gammaln(m - k + 1)
        + xlogy(k, p[:, None])
        + xlog1py(m - k, -p[:, None])
    )
    log_likelihood = np.sum(log_prob * frequencies, axis=1)
    index = int(np.argmax(log_likelihood))
    chosen = int(candidates[index])
    poisson_limit = float(
        np.sum(frequencies * (xlogy(k[0], mean) - mean - gammaln(k[0] + 1)))
    )
    diagnostics = dict(
        search_lower=lower,
        search_upper=upper,
        selected_M=chosen,
        selected_p=float(p[index]),
        best_on_lower_boundary=chosen == lower,
        best_on_upper_boundary=chosen == upper,
        selected_log_likelihood=float(log_likelihood[index]),
        poisson_limit_log_likelihood=poisson_limit,
        finite_minus_poisson_log_likelihood=float(
            log_likelihood[index] - poisson_limit
        ),
        global_optimum_certified=False,
    )
    if chosen == upper:
        return rejected("search_cap", float(chosen), **diagnostics)
    return dict(
        status="success",
        estimate=float(chosen),
        raw_estimate=float(chosen),
        **diagnostics,
    )


def factorial_cumulant_M(y, summary=None):
    """E2: infer M,p from cumulants 2,3; inferred b is a diagnostic, not a guard."""
    summary = count_summary(y) if summary is None else summary
    n, s1, s2, s3 = (summary[key] for key in ("N", "s1", "s2", "s3"))
    a = n * s2 - s1 * s1
    c = n * n * s3 - 3 * n * s1 * s2 + 2 * s1**3
    if a >= 0 or c <= 0:
        return rejected("moment_sign_invalid")
    p = Fraction(-c, 2 * n * a)
    M = Fraction(-4 * a**3, c**2)
    b = Fraction(s1 * c - 2 * a**2, n * c)
    result = moment_result(M, p, b, require_nonnegative_background=False)
    result["inferred_background_negative"] = b < 0
    return result


def calibrated_M(y, dark, summary=None):
    """E3: exact plug-in first two moments and an independent source-off mean."""
    summary = count_summary(y) if summary is None else summary
    off = count_summary(dark)
    n, s1, s2 = (summary[key] for key in ("N", "s1", "s2"))
    b = Fraction(off["s1"], off["N"])
    mean = Fraction(s1, n)
    source_mean = mean - b
    variance = Fraction(s2 + s1, n) - mean**2
    if source_mean == 0:
        return rejected("zero_source_mean")
    p = 1 - (variance - b) / source_mean
    if p <= 0:
        return rejected("moment_sign_invalid")
    return moment_result(source_mean / p, p, b, require_nonnegative_background=True)


def numeric_summary(values, truth):
    if not values:
        return dict(count=0, median=None, q25=None, q75=None, mean=None, rel_rmse=None)
    values = np.array(values, dtype=float)
    q25, median, q75 = np.quantile(values, [0.25, 0.5, 0.75], method="linear")
    return dict(
        count=len(values),
        median=float(median),
        q25=float(q25),
        q75=float(q75),
        mean=float(values.mean()),
        rel_rmse=float(np.sqrt(np.mean((values - truth) ** 2)) / truth),
    )


def summarize_estimates(results, truth):
    """Keep failed fits in the denominator and retain pre-domain finite diagnostics."""
    if truth <= 0:
        raise ValueError("The reference count must be positive.")
    success = [entry["estimate"] for entry in results if entry["status"] == "success"]
    failures = Counter(
        entry["status"] for entry in results if entry["status"] != "success"
    )
    raw = [
        entry["raw_estimate"]
        for entry in results
        if entry.get("raw_estimate") is not None
        and math.isfinite(entry["raw_estimate"])
    ]
    values = numeric_summary(success, truth)
    search_results = [entry for entry in results if "search_upper" in entry]
    inferred_backgrounds = [
        entry for entry in results if "inferred_background_negative" in entry
    ]
    return {
        "status": "not_run" if not results else "reported",
        "attempted": len(results),
        "successful": len(success),
        "failed": sum(failures.values()),
        "failure_reasons": dict(sorted(failures.items())),
        "success_fraction": len(success) / len(results) if results else None,
        "conditional_median": values["median"],
        "conditional_q25": values["q25"],
        "conditional_q75": values["q75"],
        "conditional_mean": values["mean"],
        "conditional_rel_rmse": values["rel_rmse"],
        "raw_finite_summary": numeric_summary(raw, truth),
        "inferred_background_diagnostics": {
            "evaluated": len(inferred_backgrounds),
            "negative": sum(
                entry["inferred_background_negative"] for entry in inferred_backgrounds
            ),
            "negative_among_successful": sum(
                entry["inferred_background_negative"] and entry["status"] == "success"
                for entry in inferred_backgrounds
            ),
        }
        if inferred_backgrounds
        else None,
        "search_diagnostics": {
            "cap_hits": failures.get("search_cap", 0),
            "lower_boundary_selections": sum(
                entry["best_on_lower_boundary"] for entry in search_results
            ),
            "upper_cap_range": [
                min(entry["search_upper"] for entry in search_results),
                max(entry["search_upper"] for entry in search_results),
            ]
            if search_results
            else None,
        }
        if search_results
        else None,
    }


def monte_carlo(reps=REPS):
    if not isinstance(reps, int) or reps < 1:
        raise ValueError("Use a positive number of repetitions.")
    rng = np.random.default_rng(SEED)
    rows = []
    print(
        "Synthetic conditional summaries: E2 median [Q25, Q75]; E1/E3 mean (relative RMSE); all give failed/attempted."
    )
    print(
        "E2 mean and RMSE are unstable tail diagnostics retained in JSON; outcomes are not CI gates."
    )
    print(
        f"{'M':>4} {'p':>5} {'b':>5} {'pulses':>8} | {'E1 bounded binomial':>26} | {'E2 cumulants':>26} | {'E3 10% source-off':>26}"
    )
    for M, p in PUBLISHED:
        for b in BACKGROUNDS:
            for nu in PULSES:
                estimates = {"E1": [], "E2": [], "E3": []}
                for _ in range(reps):
                    y = rng.binomial(M, p, nu) + rng.poisson(b, nu)
                    dark = rng.poisson(b, nu // 10)
                    summary = count_summary(y)
                    if nu <= 10**5:
                        estimates["E1"].append(mle_binomial_M(y, summary=summary))
                    estimates["E2"].append(factorial_cumulant_M(y, summary=summary))
                    estimates["E3"].append(calibrated_M(y, dark, summary=summary))
                row = dict(M=M, p=p, b=b, pulses=nu)
                cells = []
                for key in ("E1", "E2", "E3"):
                    result = summarize_estimates(estimates[key], M)
                    row[key] = result
                    if result["attempted"] == 0:
                        cells.append(f"{'not run':>26}")
                    elif result["successful"] == 0:
                        cells.append(
                            f"{'no successful fits':>18} {result['failed']:3}/{result['attempted']}"
                        )
                    elif key == "E2":
                        cells.append(
                            f"{result['conditional_median']:.3g} [{result['conditional_q25']:.3g}, {result['conditional_q75']:.3g}] {result['failed']:3}/{result['attempted']}"
                        )
                    else:
                        cells.append(
                            f"{result['conditional_mean']:8.2f} {result['conditional_rel_rmse']:8.1%} {result['failed']:3}/{result['attempted']}"
                        )
                rows.append(row)
                print(
                    f"{M:>4} {p:>5} {b:>5} {nu:>8} | " + " | ".join(cells), flush=True
                )
    return rows


def bounds():
    rows = []
    print(
        "Approximate fixed-pair necessary counts, not achievable costs or certified global optima."
    )
    print(
        f"{'M':>4} {'p':>5} {'b':>4} {'alt':>5} | {'known b':>10} {'r=0.1':>10} {'r=0':>10} | r=0 / known"
    )
    for M, p in PUBLISHED:
        cutoff = int(M * p + 1 + 12 * np.sqrt(M * p + 1) + 20)
        for b in (0.1, 1.0):
            for M2 in sorted({M + 1, int(round(1.1 * M))}):
                qs = np.linspace(1e-4, min(1.0, 2 * p), 4001)
                ps = np.linspace(0.5 * p * M / M2, min(1.0, 1.5 * p * M / M2), 61)
                bs = np.linspace(0.0, b + 0.3 * p * M + 0.5, 61)
                evaluations = {
                    "known_b": search_known(M, p, b, M2, qs, cutoff),
                    "dark_r_0_1": search_pair(
                        M, p, b, M2, 0.1, ps, bs, cutoff, maxiter=4000
                    ),
                    "unknown_b": search_pair(
                        M, p, b, M2, 0.0, ps, bs, cutoff, maxiter=4000
                    ),
                }
                counts = {
                    key: entry["necessary_windows_approximation"]
                    for key, entry in evaluations.items()
                }
                rows.append(
                    dict(
                        M=M, p=p, b=b, alternative=M2, **counts, evaluations=evaluations
                    )
                )
                known, dark, unknown = (
                    counts[key] for key in ("known_b", "dark_r_0_1", "unknown_b")
                )
                print(
                    f"{M:>4} {p:>5} {b:>4} {M2:>5} | {known:10.3g} {dark:10.3g} {unknown:10.3g} | {unknown / known:8.1f}x",
                    flush=True,
                )
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--part", choices=("mc", "bounds", "all"), default="all")
    parser.add_argument(
        "--json", help="new output path for full results and diagnostics"
    )
    args = parser.parse_args()
    output = {
        "metadata": metadata(
            {
                "part": args.part,
                "seed": SEED,
                "rng": "numpy.random.default_rng/PCG64",
                "repetitions": REPS,
                "published_M_p": PUBLISHED,
                "backgrounds": BACKGROUNDS,
                "signal_pulses": PULSES,
                "source_off_pulses": "signal_pulses//10",
                "cell_loop_order": [
                    "published_M_p",
                    "backgrounds",
                    "signal_pulses",
                    "repetitions",
                ],
                "draw_order": [
                    "binomial_signal",
                    "poisson_signal_background",
                    "poisson_source_off",
                ],
                "E1_search_span": E1_SEARCH_SPAN,
                "E1_max_signal_pulses": 10**5,
                "E1_scope": "bounded integer search, global optimum not certified; cap hits excluded",
                "E2_domain": "continuous M>=1, 0<p<=1; exact rational sign and domain guards; inferred background is diagnostic only",
                "E3_domain": "continuous M>=1, 0<p<=1, background>=0; exact rational guards",
                "E2_background_diagnostics": "evaluated whenever cumulant signs permit; negative includes p/M failures; negative_among_successful counts retained estimates",
                "summary_scope": "conditional on success; raw finite summaries also retained; no empirical thresholds gate CI",
                "quantiles": "Q25, median, Q75; numpy.quantile method=linear; conditional on the same successes as the mean/RMSE",
                "E2_reporting": "median and interquartile range are primary; mean and RMSE are unstable tail diagnostics, not reliable typical-error summaries",
            }
        )
    }
    if args.part in ("bounds", "all"):
        output["bounds"] = bounds()
    if args.part in ("mc", "all"):
        output["monte_carlo"] = monte_carlo()
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(output, handle, indent=2, allow_nan=False)
            handle.write("\n")


if __name__ == "__main__":
    main()
