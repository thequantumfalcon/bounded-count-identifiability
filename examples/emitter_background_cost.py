"""Approximate fixed-pair testing calculations for a synthetic emitter model.

Y = Binomial(n,p) + Poisson(b), independently across signal windows. Optional
source-off windows share the fixed background rate. These are numerical
approximations to necessary-count bounds for explicit candidate alternatives;
no global optimum, achievable sample size, measurement, or certified numerical
inequality is claimed. Use CPython 3.13 and requirements-emitters.txt.
"""

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import binom, poisson

K = 80
C = math.log(1 / 0.19) / 2
RATIOS = [0.0, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
NUMERICAL_SCOPE = (
    "Approximate fixed-pair necessary-count calculations, not certified interval "
    "bounds, global optima, achievable sample sizes, or measurements."
)


def metadata(design):
    directory = Path(__file__).resolve().parent
    names = (
        "emitter_background_cost.py",
        "emitter_published_parameters.py",
        "requirements-emitters.txt",
    )
    return {
        "schema_version": 3,
        "scope": NUMERICAL_SCOPE,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "source_sha256": {
            "examples/" + name: hashlib.sha256(
                (directory / name).read_bytes()
            ).hexdigest()
            for name in names
        },
        "design": design,
    }


def validate_model(n, p, b):
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("The emitter count must be a nonnegative integer.")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("Detection probability must lie in [0,1].")
    if not math.isfinite(b) or b < 0:
        raise ValueError("Background must be finite and nonnegative.")


def pmf(n, p, b, cutoff=K):
    validate_model(n, p, b)
    if not isinstance(cutoff, int) or cutoff < 1:
        raise ValueError("The cutoff must be a positive integer.")
    return np.convolve(
        binom.pmf(np.arange(n + 1), n, p), poisson.pmf(np.arange(cutoff), b)
    )[:cutoff]


def tail_upper(mean, cutoff):
    """Chernoff upper bound for P(Y>=cutoff), using MGF(Y)<=MGF(Pois(mean))."""
    mean = np.asarray(mean, dtype=float)
    if np.any(~np.isfinite(mean)) or np.any(mean < 0) or cutoff < 1:
        raise ValueError("Invalid tail-bound arguments.")
    with np.errstate(divide="ignore", invalid="ignore", under="ignore"):
        bound = np.exp(-cutoff * np.log(cutoff / mean) + cutoff - mean)
    return np.where(mean == 0, 0.0, np.where(mean < cutoff, bound, 1.0))


def neg_log_bc(P, Q, tail_p=0.0, tail_q=0.0):
    """Stable upper distance from prefix Hellinger and explicit tail upper bounds.

    In exact arithmetic, BC >= 1-Hpre-(tail_p+tail_q)/2. Floating arithmetic
    here is approximate; final witnesses also receive a Decimal cross-check.
    Omitting nonzero tails is not justified for a bound on the full count law.
    """
    P, Q = np.asarray(P), np.asarray(Q)
    if P.shape != Q.shape or np.any(P < 0) or np.any(Q < 0):
        raise ValueError("Prefixes must have equal shapes and nonnegative entries.")
    if not np.all(np.isfinite(P)) or not np.all(np.isfinite(Q)):
        raise ValueError("Prefixes must be finite.")
    if not 0 <= tail_p <= 1 or not 0 <= tail_q <= 1:
        raise ValueError("Tail upper bounds must lie in [0,1].")
    delta = float(0.5 * np.sum((np.sqrt(P) - np.sqrt(Q)) ** 2))
    delta += (tail_p + tail_q) / 2
    return -math.log1p(-delta) if delta < 1 else math.inf


def grid_pmfs(n1, ps, bs, cutoff=K):
    weights = binom.pmf(np.arange(n1 + 1)[None, :], n1, ps[:, None])
    pois = poisson.pmf(np.arange(cutoff)[None, :], bs[:, None])
    Q = np.zeros((len(ps), len(bs), cutoff))
    for k in range(min(n1 + 1, cutoff)):
        Q[:, :, k:] += weights[:, k][:, None, None] * pois[None, :, : cutoff - k]
    return Q


def decimal_pmf(n, p, b, cutoff):
    """Positive-term recurrence at the caller's Decimal precision."""
    one = Decimal(1)
    weights = [
        Decimal(math.comb(n, k))
        * (p**k if k else one)
        * ((one - p) ** (n - k) if n != k else one)
        for k in range(n + 1)
    ]
    pois = [(-b).exp()]
    for k in range(1, cutoff):
        pois.append(pois[-1] * b / k)
    return [
        sum((weights[j] * pois[k - j] for j in range(min(n, k) + 1)), Decimal(0))
        for k in range(cutoff)
    ]


def decimal_tail(mean, cutoff):
    if mean == 0:
        return Decimal(0)
    if mean >= cutoff:
        return Decimal(1)
    k = Decimal(cutoff)
    return (-k * (k / mean).ln() + k - mean).exp()


def decimal_pair(n, p, b, n2, q, bb, r, cutoff, precision=80):
    """High-precision approximation; Decimal rounding is not interval certification."""
    with localcontext() as ctx:
        ctx.prec = precision
        p, b, q, bb, r = (Decimal(str(v)) for v in (p, b, q, bb, r))
        P, Q = decimal_pmf(n, p, b, cutoff), decimal_pmf(n2, q, bb, cutoff)
        hpre = sum(((a.sqrt() - c.sqrt()) ** 2 for a, c in zip(P, Q)), Decimal(0)) / 2
        tp, tq = decimal_tail(n * p + b, cutoff), decimal_tail(n2 * q + bb, cutoff)
        delta = hpre + (tp + tq) / 2
        if delta >= 1:
            raise ArithmeticError(
                "Prefix does not give a positive affinity lower estimate."
            )
        signal = -(1 - delta).ln()
        dark = r * (b.sqrt() - bb.sqrt()) ** 2 / 2
        divergence = signal + dark
        count = (
            (1 / Decimal("0.19")).ln() / (2 * divergence) if divergence > 0 else None
        )
        return {
            "decimal_precision": precision,
            "prefix_hellinger_squared": str(hpre),
            "tail_upper_source": str(tp),
            "tail_upper_alternative": str(tq),
            "signal_log_affinity_upper_approximation": str(signal),
            "dark_log_affinity": str(dark),
            "combined_log_affinity_upper_approximation": str(divergence),
            "necessary_windows_approximation": float(count)
            if count is not None
            else None,
        }


def pair_diagnostics(n, p, b, n2, q, bb, r, cutoff=K):
    validate_model(n, p, b)
    validate_model(n2, q, bb)
    if not math.isfinite(r) or r < 0:
        raise ValueError("The source-off ratio must be nonnegative.")
    initial_cutoff = cutoff
    for _ in range(8):
        P, Q = pmf(n, p, b, cutoff), pmf(n2, q, bb, cutoff)
        hpre = float(np.sum((np.sqrt(P) - np.sqrt(Q)) ** 2) / 2)
        tp = float(tail_upper(n * p + b, cutoff))
        tq = float(tail_upper(n2 * q + bb, cutoff))
        if tp + tq <= 1e-8 * max(hpre, 1e-30):
            break
        cutoff *= 2
    else:
        raise ArithmeticError("Tail refinement failed to reach the declared tolerance.")
    floating = neg_log_bc(P, Q, tp, tq)
    high = decimal_pair(n, p, b, n2, q, bb, r, cutoff)
    reference = float(high["signal_log_affinity_upper_approximation"])
    relative = abs(floating - reference) / reference if reference > 0 else None
    doubled = neg_log_bc(
        pmf(n, p, b, cutoff * 2),
        pmf(n2, q, bb, cutoff * 2),
        float(tail_upper(n * p + b, cutoff * 2)),
        float(tail_upper(n2 * q + bb, cutoff * 2)),
    )
    return {
        **high,
        "candidate": {"n": n2, "p": float(q), "background": float(bb)},
        "source_off_ratio": r,
        "initial_cutoff": initial_cutoff,
        "evaluated_cutoff": cutoff,
        "tail_upper_to_prefix_ratio": (tp + tq) / hpre if hpre > 0 else None,
        "float_log_affinity_upper": floating,
        "float_relative_difference_from_decimal": relative,
        "cutoff_doubling_distance_change": abs(doubled - floating),
        "prefix_mass_defects": [float(1 - P.sum()), float(1 - Q.sum())],
        "numerical_status": "approximation_not_interval_certified",
    }


def search_pair(n, p, b, n2, r, ps, bs, cutoff=K, maxiter=3000):
    validate_model(n, p, b)
    validate_model(n2, 0, 0)
    ps, bs = validate_grid(ps, 1), validate_grid(bs)
    if not math.isfinite(r) or r < 0:
        raise ValueError("Use a finite nonnegative source-off ratio.")
    P = pmf(n, p, b, cutoff)
    tp = float(tail_upper(n * p + b, cutoff))
    Q = grid_pmfs(n2, ps, bs, cutoff)
    delta = np.sum((np.sqrt(P)[None, None, :] - np.sqrt(Q)) ** 2, axis=2) / 2
    delta += (tp + tail_upper(n2 * ps[:, None] + bs[None, :], cutoff)) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        grid = -np.log1p(-np.minimum(delta, 1))
    grid += r * (np.sqrt(b) - np.sqrt(bs)[None, :]) ** 2 / 2
    i, j = np.unravel_index(np.argmin(grid), grid.shape)
    if not math.isfinite(grid[i, j]):
        raise ArithmeticError("No finite grid objective; increase the initial cutoff.")
    start = np.array([ps[i], bs[j]])

    def objective(x):
        q, bb = x
        if not 0 <= q <= 1 or bb < 0 or not np.isfinite(x).all():
            return math.inf
        return (
            neg_log_bc(
                P, pmf(n2, q, bb, cutoff), tp, float(tail_upper(n2 * q + bb, cutoff))
            )
            + r * (math.sqrt(b) - math.sqrt(bb)) ** 2 / 2
        )

    res = minimize(
        objective,
        start,
        method="Nelder-Mead",
        bounds=((0, 1), (0, None)),
        options={"xatol": 1e-12, "fatol": 1e-22, "maxiter": maxiter},
    )
    refined = objective(res.x)
    chosen = res.x if refined < grid[i, j] else start
    details = pair_diagnostics(n, p, b, n2, *chosen, r, cutoff)
    details["search"] = {
        "method": "finite_grid_then_bounded_Nelder_Mead",
        "global_optimum_certified": False,
        "grid_p": [float(ps[0]), float(ps[-1]), len(ps)],
        "grid_background": [float(bs[0]), float(bs[-1]), len(bs)],
        "grid_best_on_boundary": bool(i in (0, len(ps) - 1) or j in (0, len(bs) - 1)),
        "physical_domain": {"p": [0, 1], "background": "[0,infinity)"},
        "chosen_from": "refinement" if refined < grid[i, j] else "grid",
        "optimizer_success": bool(res.success),
        "optimizer_message": str(res.message),
        "optimizer_iterations": int(res.nit),
        "optimizer_evaluations": int(res.nfev),
        "optimizer_reported_objective": finite_or_none(res.fun),
        "optimizer_recomputed_objective": finite_or_none(refined),
        "optimizer_candidate_valid": math.isfinite(refined),
        "candidate_on_physical_boundary": bool(chosen[0] in (0, 1) or chosen[1] == 0),
    }
    return details


def search_known(n, p, b, n2, qs, cutoff=K):
    validate_model(n2, 0, 0)
    qs = validate_grid(qs, 1)
    P = pmf(n, p, b, cutoff)
    tp = float(tail_upper(n * p + b, cutoff))

    def objective(q):
        if not math.isfinite(q) or not 0 <= q <= 1:
            return math.inf
        return neg_log_bc(
            P, pmf(n2, q, b, cutoff), tp, float(tail_upper(n2 * q + b, cutoff))
        )

    values = np.array([objective(q) for q in qs])
    index = int(np.argmin(values))
    if not math.isfinite(values[index]):
        raise ArithmeticError("No finite grid objective; increase the initial cutoff.")
    # Refine inside a finite neighboring grid bracket. Distant probabilities can
    # have an uninformative tail bound of one at this cutoff; passing their
    # infinite objective to scalar interpolation causes invalid arithmetic.
    left = max(0, index - 1)
    right = min(len(qs) - 1, index + 1)
    if not math.isfinite(values[left]):
        left = index
    if not math.isfinite(values[right]):
        right = index
    if left == right:
        raise ArithmeticError(
            "No finite refinement bracket; increase the initial cutoff."
        )
    bracket = (float(qs[left]), float(qs[right]))
    result = minimize_scalar(
        objective, bounds=bracket, method="bounded", options={"xatol": 1e-13}
    )
    refined = objective(result.x)
    candidates = [
        (values[index], float(qs[index]), "grid"),
        (refined, float(result.x), "refinement"),
        (objective(0), 0.0, "endpoint"),
        (objective(1), 1.0, "endpoint"),
    ]
    best, q, chosen_from = min(candidates, key=lambda item: item[0])
    if not math.isfinite(best):
        raise ArithmeticError(
            "No finite candidate objective; increase the initial cutoff."
        )
    details = pair_diagnostics(n, p, b, n2, q, b, 0.0, cutoff)
    details["search"] = {
        "method": "finite_grid_then_local_bounded_scalar_search",
        "global_optimum_certified": False,
        "grid_p": [float(qs[0]), float(qs[-1]), len(qs)],
        "grid_best_on_boundary": index in (0, len(qs) - 1),
        "refinement_bracket": list(bracket),
        "physical_domain": {"p": [0, 1], "background": "fixed at source background"},
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "optimizer_evaluations": int(result.nfev),
        "optimizer_reported_objective": finite_or_none(result.fun),
        "optimizer_recomputed_objective": finite_or_none(refined),
        "optimizer_candidate_valid": math.isfinite(refined),
        "chosen_from": chosen_from,
        "candidate_on_physical_boundary": q in (0, 1),
    }
    return details


def validate_grid(values, maximum=math.inf):
    values = np.asarray(values, dtype=float)
    if (
        values.ndim != 1
        or len(values) < 2
        or not np.isfinite(values).all()
        or np.any(values < 0)
        or np.any(values > maximum)
        or np.any(np.diff(values) <= 0)
    ):
        raise ValueError(
            "Use a strictly increasing finite grid within the model domain."
        )
    return values


def finite_or_none(value):
    """Keep failed optimizer diagnostics serializable as strict JSON."""
    return float(value) if math.isfinite(value) else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--json", help="new output path for the full table and diagnostics"
    )
    args = parser.parse_args()
    rows = []
    print(
        "Approximate fixed-pair necessary counts; ratios are not ratios of achievable costs."
    )
    print(" p     b   n | known-b N | " + " ".join(f"r={r:<6}" for r in RATIOS))
    for b in (0.1, 1.0):
        for p in (0.05, 0.1, 0.3):
            for n in (2, 3, 4, 5):
                ps = np.linspace(0.4 * p, p, 241)
                bs = np.linspace(max(0.0, b - 0.3 * p), b + 1.2 * p * n / (n + 1), 241)
                known = search_known(n, p, b, n + 1, np.linspace(1e-4, p, 6001))
                evaluations = [search_pair(n, p, b, n + 1, r, ps, bs) for r in RATIOS]
                count = known["necessary_windows_approximation"]
                ratios = [
                    entry["necessary_windows_approximation"] / count
                    for entry in evaluations
                ]
                rows.append(
                    dict(
                        p=p,
                        b=b,
                        n=n,
                        known_b_windows=count,
                        ratios=ratios,
                        known_b_evaluation=known,
                        evaluations=evaluations,
                    )
                )
                print(
                    f"{p:4} {b:4} {n:3} | {count:9.3g} | "
                    + " ".join(f"{value:7.3g}x" for value in ratios),
                    flush=True,
                )
    output = {
        "metadata": metadata(
            {
                "ratios_r": RATIOS,
                "n": [2, 3, 4, 5],
                "p": [0.05, 0.1, 0.3],
                "b": [0.1, 1.0],
                "initial_cutoff": K,
                "signal_windows": "N",
                "source_off_windows": "r*N (integer allocation required in an actual design)",
            }
        ),
        "ratios_r": RATIOS,
        "rows": rows,
    }
    if args.json:
        with open(args.json, "x", encoding="utf-8") as handle:
            json.dump(output, handle, indent=2, allow_nan=False)
            handle.write("\n")


if __name__ == "__main__":
    main()
