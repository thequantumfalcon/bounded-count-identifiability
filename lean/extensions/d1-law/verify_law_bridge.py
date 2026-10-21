"""Freshly compile the core and a selected suite of proof extensions.

Run from the repository root after retrieving the pinned dependency cache:
    python lean/extensions/d1-law/verify_law_bridge.py --run ci-check
Add --suite research to include probability, conditional coverage and robustness.
No existing project proof artifacts are imported. Dependency caches are reused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXTENSION = Path(__file__).resolve().parent
PROJECT = EXTENSION.parents[1]
REPOSITORY = PROJECT.parent
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
}
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def full_roots(module: str) -> list[str]:
    return [module + "." + name for name in (ROOTS | RESEARCH_ROOTS)[module]]


def selected_roots(suite: str) -> dict[str, tuple[str, ...]]:
    if suite not in {"law", "research"}:
        raise ValueError("Unknown extension suite")
    return ROOTS if suite == "law" else ROOTS | RESEARCH_ROOTS


def source_inputs(suite: str = "law") -> dict[str, Path]:
    paths = {
        "verifier": Path(__file__).resolve(),
        "core_verifier": PROJECT / "verify.py",
        "core_manifest": PROJECT / "source_manifest.json",
        "dependency_lock": PROJECT / "lake-manifest.json",
        "lake_config": PROJECT / "lakefile.toml",
        "toolchain": PROJECT / "lean-toolchain",
    }
    for module in CORE:
        paths[module] = PROJECT / (module + ".lean")
    for module in selected_roots(suite):
        directory = EXTENSION.parent / DIRECTORIES[module]
        paths[module] = directory / (module + ".lean")
        paths[module + "_manifest"] = directory / "source_manifest.json"
    return paths


def check_sources(inputs: dict[str, Path], suite: str = "law") -> None:
    roots = selected_roots(suite)
    groups = [(inputs["core_manifest"], CORE)] + [
        (inputs[module + "_manifest"], (module,)) for module in roots
    ]
    for manifest_file, modules in groups:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1 or set(manifest.get("sources", {})) != {
            module + ".lean" for module in modules
        }:
            raise ValueError("Unexpected source manifest schema or source set")
        for module in modules:
            source = inputs[module]
            entry = manifest["sources"][source.name]
            if digest(source) != entry.get(
                "sha256"
            ) or source.stat().st_size != entry.get("bytes"):
                raise ValueError("Source hash or size differs from its manifest")
            code = source.read_text(encoding="utf-8")
            if re.search(r"\b(sorry|admit|sorryAx|native_decide|axiom)\b", code):
                raise ValueError("Source contains a prohibited proof admission")
            if re.search(r"\bset_option\s+debug\.skipKernelTC\s+true\b", code):
                raise ValueError("Source requests a kernel bypass")
            if module in roots and manifest.get("theorem_roots") != full_roots(module):
                raise ValueError(
                    "Extension theorem roots differ from the expected list"
                )
    if inputs["toolchain"].read_text(encoding="utf-8").strip() != (
        "leanprover/lean4:v4.35.0"
    ):
        raise ValueError("Expected the pinned Lean 4.35.0 toolchain")


def resolve_environment(args: argparse.Namespace) -> tuple[Path, list[Path]]:
    if args.mode == "existing-cache":
        if not args.lean_executable or not args.library:
            raise ValueError("Existing-cache mode requires compiler and libraries")
        lean = Path(
            shutil.which(args.lean_executable) or args.lean_executable
        ).resolve()
        libraries = [Path(item).resolve() for item in args.library]
    else:
        if args.lean_executable or args.library:
            raise ValueError("Custom paths require existing-cache mode")
        probe = (
            "import json,os,shutil; "
            "print(json.dumps({'lean':shutil.which('lean'),"
            "'lean_path':os.environ.get('LEAN_PATH','')}))"
        )
        result = subprocess.run(
            ["lake", "env", sys.executable, "-c", probe],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=180,
            check=True,
        )
        resolved = json.loads(result.stdout)
        if not resolved.get("lean"):
            raise ValueError("Lake did not resolve a Lean compiler")
        lean = Path(resolved["lean"]).resolve()
        candidates = [
            (PROJECT / item).resolve()
            for item in resolved["lean_path"].split(os.pathsep)
            if item
        ]
        # Lake's own project cache is deliberately replaced by a fresh core run.
        project_cache = (PROJECT / ".lake/build/lib/lean").resolve()
        libraries = [
            path for path in candidates if path.is_dir() and path != project_cache
        ]
    if not lean.is_file() or not libraries or any(not p.is_dir() for p in libraries):
        raise ValueError("Compiler or dependency library is missing")
    source_directories = [EXTENSION.parent / name for name in DIRECTORIES.values()]
    for library in [PROJECT, *source_directories, *libraries]:
        for module in (*CORE, *ROOTS, *RESEARCH_ROOTS):
            if any(
                (library / (module + suffix)).exists()
                for suffix in (".olean", ".ilean")
            ):
                raise ValueError("Existing project artifact would shadow a fresh proof")
    return lean, libraries


def check_core_receipt(
    receipt_dir: Path, build_dir: Path, before: dict[str, str]
) -> tuple[bool, dict[str, str]]:
    receipt_file = receipt_dir / "result.json"
    if not receipt_file.is_file():
        return False, {}
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    rows = receipt.get("modules", [])
    passed = (
        receipt.get("status") == "PASS"
        and re.search(r"\bversion 4\.35\.0\b", str(receipt.get("compiler_version", "")))
        and receipt.get("compiler_sha256") == before["compiler"]
        and receipt.get("source_manifest_sha256") == before["core_manifest"]
        and receipt.get("dependency_lock_sha256") == before["dependency_lock"]
        and receipt.get("verifier_sha256") == before["core_verifier"]
        and receipt.get("verifier_unchanged") is True
        and [row.get("module") for row in rows] == list(CORE)
    )
    bound_files = {"receipt": digest(receipt_file)}
    for row in rows:
        module = row.get("module")
        if module not in CORE:
            return False, bound_files
        expected_roots = list(CORE_ROOTS[module])
        axioms = row.get("printed_axiom_lists", {})
        passed = passed and (
            row.get("status") == "PASS"
            and row.get("exit_code") == 0
            and row.get("timed_out") is False
            and row.get("source_sha256") == before[module]
            and row.get("source_unchanged") is True
            and row.get("printed_axioms_checked") is True
            and row.get("no_error_or_warning_diagnostics") is True
            and list(axioms) == expected_roots
            and bool(expected_roots)
            and all(set(items) <= ALLOWED_AXIOMS for items in axioms.values())
        )
        for kind, path in (
            ("olean", build_dir / (module + ".olean")),
            ("stdout", receipt_dir / (module + ".stdout.txt")),
            ("stderr", receipt_dir / (module + ".stderr.txt")),
        ):
            exists = path.is_file() and (kind != "olean" or path.stat().st_size > 0)
            value = digest(path) if exists else None
            passed = passed and exists and value == row.get(kind + "_sha256")
            if exists:
                bound_files[module + "/" + kind] = value
    return bool(passed), bound_files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("lake", "existing-cache"), default="lake")
    parser.add_argument("--suite", choices=("law", "research"), default="law")
    parser.add_argument("--run", default="lake-check")
    parser.add_argument("--lean-executable")
    parser.add_argument("--library", action="append", default=[])
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", args.run):
        parser.error("--run requires 1 to 64 letters, digits, underscores or hyphens")
    roots = selected_roots(args.suite)
    core_run = ("d1-law-" if args.suite == "law" else "d1-law-research-") + args.run
    output_name = "law-bridge" if args.suite == "law" else "research"
    output = (REPOSITORY / "build" / output_name / args.run).resolve()
    core_receipts = (PROJECT / "verification" / core_run).resolve()
    core_build = (PROJECT / ".verification" / core_run).resolve()
    for path in (output, core_receipts, core_build):
        if not path.is_relative_to(REPOSITORY) or path.exists():
            raise ValueError("Every output must be fresh and inside the repository")
    inputs = source_inputs(args.suite)
    # Environment discovery may invoke Lake. Preserve the source/config baseline
    # before that subprocess so changes cannot silently become the new baseline.
    before = {name: digest(path) for name, path in inputs.items()}
    check_sources(inputs, args.suite)
    lean, libraries = resolve_environment(args)
    inputs["compiler"] = lean
    before["compiler"] = digest(lean)
    check_sources(inputs, args.suite)
    if any(
        not path.is_file() or digest(path) != before[name]
        for name, path in inputs.items()
    ):
        raise ValueError("Proof inputs changed during environment discovery")
    output.mkdir(parents=True)
    replacements = [
        (str(REPOSITORY), "<repository>"),
        (str(lean.parent.parent), "<lean>"),
    ]
    replacements.extend((str(p), f"<dependency-{i}>") for i, p in enumerate(libraries))
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    def sanitize(data: bytes) -> str:
        value = data.decode("utf-8", errors="replace")
        for path, label in replacements:
            value = value.replace(path, label).replace(path.replace("\\", "/"), label)
        value = re.sub(r"[A-Za-z]:[\\/][^\s\"<>]*", "<absolute-path>", value)
        return re.sub(
            r"(?<![\w<>])/(?:[^\s/\"<>]+/)+[^\s\"<>]*", "<absolute-path>", value
        )

    def execute(
        command: list[str], cwd: Path, env: dict[str, str], tag: str, timeout: int
    ):
        timed_out = False
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
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
        for kind, text in (("stdout", stdout), ("stderr", stderr)):
            (output / (tag + "." + kind + ".txt")).write_text(text, encoding="utf-8")
        return result.returncode, timed_out, stdout, stderr

    env = os.environ.copy()
    command = [
        sys.executable,
        str(inputs["core_verifier"]),
        "--mode",
        "existing-cache",
        "--run",
        core_run,
        "--lean-executable",
        str(lean),
    ]
    for library in libraries:
        command.extend(["--library", str(library)])
    code, timed_out, _, _ = execute(command, PROJECT, env, "core", 1500)
    core_ok, core_files = check_core_receipt(core_receipts, core_build, before)
    core_ok = core_ok and code == 0 and not timed_out
    records = []
    env["LEAN_PATH"] = os.pathsep.join(str(p) for p in (output, core_build, *libraries))
    if core_ok:
        for module in roots:
            source = output / (module + ".lean")
            source.write_bytes(inputs[module].read_bytes())
            target = output / (module + ".olean")
            command = [str(lean), "--trust=0", "-o", str(target), source.name]
            code, timed_out, stdout, stderr = execute(command, output, env, module, 240)
            printed = [
                {
                    "theorem": theorem,
                    "axioms": [x.strip() for x in raw.split(",") if x.strip()],
                }
                for theorem, raw in re.findall(
                    r"'([^']+)' depends on axioms: \[([^]]*)\]", stdout
                )
            ]
            checks = {
                "exit_zero": code == 0,
                "not_timed_out": not timed_out,
                "exact_roots": [x["theorem"] for x in printed] == full_roots(module),
                "standard_axioms": all(
                    len(x["axioms"]) == 3 and set(x["axioms"]) == ALLOWED_AXIOMS
                    for x in printed
                ),
                "no_diagnostics": not re.search(
                    r"\b(error|warning):|sorryAx", stdout + stderr
                ),
                "fresh_nonempty_olean": target.is_file() and target.stat().st_size > 0,
                "source_snapshot_unchanged": digest(source) == before[module],
            }
            records.append(
                {
                    "module": module,
                    "status": "PASS" if all(checks.values()) else "FAIL",
                    "checks": checks,
                    "printed_axiom_lists": printed,
                    "source_sha256": before[module],
                    "exit_code": code,
                    "timed_out": timed_out,
                    "olean_sha256": digest(target) if target.is_file() else None,
                    "stdout_sha256": digest(output / (module + ".stdout.txt")),
                    "stderr_sha256": digest(output / (module + ".stderr.txt")),
                }
            )
            if not all(checks.values()):
                break
    core_still_ok, core_after = check_core_receipt(core_receipts, core_build, before)
    try:
        check_sources(inputs, args.suite)
        source_manifests_valid = True
    except (OSError, ValueError, KeyError, TypeError):
        source_manifests_valid = False
    checks = {
        "source_manifests_valid": source_manifests_valid,
        "fresh_core_verified": core_ok,
        "core_artifacts_and_receipts_unchanged": core_still_ok
        and core_files == core_after,
        (
            "both_extensions_verified"
            if args.suite == "law"
            else "all_extensions_verified"
        ): len(records) == len(roots) and all(r["status"] == "PASS" for r in records),
        "extension_artifacts_and_snapshots_unchanged": all(
            digest(output / (r["module"] + ".lean")) == before[r["module"]]
            and all(
                (output / (r["module"] + suffix)).is_file()
                and digest(output / (r["module"] + suffix)) == r[kind + "_sha256"]
                for kind, suffix in (
                    ("olean", ".olean"),
                    ("stdout", ".stdout.txt"),
                    ("stderr", ".stderr.txt"),
                )
            )
            for r in records
        ),
        **{
            name + "_unchanged": path.is_file() and digest(path) == before[name]
            for name, path in inputs.items()
        },
    }
    passed = all(checks.values())
    summary = {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verification_mode": args.mode,
        "suite": args.suite,
        "input_sha256": before,
        "checks": checks,
        "core_receipt_directory": "lean/verification/" + core_run,
        "core_output_sha256": core_files,
        "modules": records,
        "uses_preexisting_dependency_artifacts": True,
        "project_artifacts_recompiled_in_dependency_order": True,
        "clean_dependency_rebuild_claimed": False,
        "independent_kernel_recheck_claimed": False,
        "scope": (
            "Fresh trust=0 compilation of the six core modules, D=1 stability and the finite Bernoulli-law bridge. Existing mathlib/Lean dependency caches are reused. No measure-theoretic independence, analytic-log equivalence, finite-sample coverage or physical validation is established."
            if args.suite == "law"
            else "Fresh trust=0 compilation of the six core modules and registered research extensions. The module list and source-bound theorem statements determine the checked scope. Existing mathlib/Lean dependency caches are reused. No analytic-log equivalence, verified confidence projection, physical validity or originality is established."
        ),
    }
    write_json(output / "result.json", summary)
    print(
        f"{args.suite} proof suite: {summary['status']}; build/{output_name}/{args.run}/result.json"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
    ) as error:
        print(
            f"Law-bridge verification failed during setup/execution ({type(error).__name__})"
        )
        raise SystemExit(1) from None
