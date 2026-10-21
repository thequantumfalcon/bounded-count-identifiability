"""Acceptance controls for the law-bridge verifier, with mocked subprocesses.

Disposable source trees and receipts exercise rejection of altered sources,
stale imports, false success records and missing compiler outputs. These tests
do not establish Lean proof validity; formal CI runs the actual compiler.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
VERIFIER = "lean/extensions/d1-law/verify_law_bridge.py"
CORE = (
    "CountSeriesCore",
    "CountLawEncoding",
    "CountIdentification",
    "CountPoissonChannel",
    "CountObservedIdentification",
    "CountSharpness",
)
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
INPUTS = (
    VERIFIER,
    "lean/verify.py",
    "lean/source_manifest.json",
    "lean/lake-manifest.json",
    "lean/lakefile.toml",
    "lean/lean-toolchain",
    "lean/extensions/d1/CountD1Stability.lean",
    "lean/extensions/d1/source_manifest.json",
    "lean/extensions/d1-law/CountD1LawBridge.lean",
    "lean/extensions/d1-law/source_manifest.json",
    *("lean/" + name + ".lean" for name in CORE),
)
RESEARCH_INPUTS = tuple(
    f"lean/extensions/{directory}/{filename}"
    for directory, name in (
        ("probability", "CountProbabilityBridge"),
        ("finite-sample", "CountD1VarianceCoverage"),
        ("background-uncertainty", "CountD1BackgroundUncertainty"),
        ("sample-mean", "CountFiniteSampleMean"),
    )
    for filename in (name + ".lean", "source_manifest.json")
)


class LawBridgeVerifierTests(unittest.TestCase):
    def run_case(self, variant, suite="law"):
        with tempfile.TemporaryDirectory(prefix="law-bridge-test-") as temporary:
            root = Path(temporary).resolve()
            for relative in INPUTS + (RESEARCH_INPUTS if suite == "research" else ()):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPOSITORY / relative, target)
            verifier = root / VERIFIER
            spec = importlib.util.spec_from_file_location(
                "law_bridge_fixture", verifier
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            inputs = module.source_inputs(suite)
            roots_for_suite = module.selected_roots(suite)
            focus = "CountD1LawBridge" if suite == "law" else "CountFiniteSampleMean"
            compiler = root / "mock-compiler.bin"
            compiler.write_bytes(b"never executed")
            library = root / "library"
            library.mkdir()
            core_run = "d1-law-test" if suite == "law" else "d1-law-research-test"
            output = root / (
                "build/law-bridge/test" if suite == "law" else "build/research/test"
            )
            core_build = root / "lean/.verification" / core_run
            core_receipts = root / "lean/verification" / core_run
            source = inputs[focus]
            manifest = inputs[focus + "_manifest"]
            if variant.startswith("tamper_"):
                changed = inputs[variant.removeprefix("tamper_")]
                changed.write_bytes(changed.read_bytes() + b"\n")
            elif variant in {
                "source_tamper",
                "core_source_tamper",
                "stability_source_tamper",
            }:
                changed = {
                    "source_tamper": source,
                    "core_source_tamper": inputs[CORE[0]],
                    "stability_source_tamper": inputs["CountD1Stability"],
                }[variant]
                changed.write_bytes(changed.read_bytes() + b"\n")
            elif variant in {
                "schema",
                "manifest_roots",
                "source_size",
                "admission",
                "kernel_bypass",
            }:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                if variant == "schema":
                    data["schema_version"] = 2
                elif variant == "manifest_roots":
                    data["theorem_roots"].pop()
                elif variant == "source_size":
                    data["sources"][source.name]["bytes"] += 1
                else:
                    code = (
                        "\ntheorem bad : False := by sorry\n"
                        if variant == "admission"
                        else "\nset_option debug.skipKernelTC true\n"
                    )
                    source.write_bytes(source.read_bytes() + code.encode())
                    data["sources"][source.name] = {
                        "sha256": module.digest(source),
                        "bytes": source.stat().st_size,
                    }
                manifest.write_text(json.dumps(data), encoding="utf-8")
            elif variant in {"reused_run", "reused_core_run"}:
                reused = output if variant == "reused_run" else core_build
                reused.mkdir(parents=True)
                (reused / "sentinel").write_bytes(b"keep")
            elif variant == "wrong_toolchain":
                inputs["toolchain"].write_text(
                    "leanprover/lean4:v0.0.0", encoding="utf-8"
                )
            elif variant in {
                "shadow_core",
                "shadow_stability",
                "shadow_bridge",
                "lake_shadow",
            }:
                name = {
                    "shadow_core": CORE[0],
                    "shadow_stability": "CountD1Stability",
                    "shadow_bridge": focus,
                    "lake_shadow": focus,
                }[variant]
                (library / (name + ".olean")).write_bytes(b"stale")
            elif variant.startswith("shadow_"):
                name = variant.removeprefix("shadow_")
                (library / (name + ".olean")).write_bytes(b"stale")

            def emit_core(command):
                self.assertEqual(command[1], str(inputs["core_verifier"]))
                self.assertEqual(command[command.index("--mode") + 1], "existing-cache")
                self.assertEqual(command[command.index("--run") + 1], core_run)
                self.assertIn(str(library), command)
                if variant == "core_timeout":
                    raise subprocess.TimeoutExpired(command, 1500)
                core_build.mkdir(parents=True)
                core_receipts.mkdir(parents=True)
                rows = []
                for name in CORE:
                    roots = re.findall(
                        r"^#print axioms ([\w.]+)\s*$",
                        inputs[name].read_text(encoding="utf-8"),
                        re.MULTILINE,
                    )
                    # These frozen modules print from within their namespaces.
                    if name in {"CountSeriesCore", "CountSharpness"}:
                        roots = [name + "." + r for r in roots]
                    axioms = {
                        r: ["propext", "Classical.choice", "Quot.sound"] for r in roots
                    }
                    paths = {
                        "olean": core_build / (name + ".olean"),
                        "stdout": core_receipts / (name + ".stdout.txt"),
                        "stderr": core_receipts / (name + ".stderr.txt"),
                    }
                    for kind, path in paths.items():
                        path.write_bytes(b"mock" if kind == "olean" else b"")
                    rows.append(
                        {
                            "module": name,
                            "status": "PASS",
                            "exit_code": 0,
                            "timed_out": False,
                            "source_sha256": module.digest(inputs[name]),
                            "source_unchanged": True,
                            "printed_axioms_checked": True,
                            "no_error_or_warning_diagnostics": True,
                            "printed_axiom_lists": axioms,
                            **{
                                kind + "_sha256": module.digest(path)
                                for kind, path in paths.items()
                            },
                        }
                    )
                receipt = {
                    "status": "PASS",
                    "compiler_version": "Lean (version 4.35.0, fixture)",
                    "compiler_sha256": module.digest(compiler),
                    "source_manifest_sha256": module.digest(inputs["core_manifest"]),
                    "dependency_lock_sha256": module.digest(inputs["dependency_lock"]),
                    "verifier_sha256": module.digest(inputs["core_verifier"]),
                    "verifier_unchanged": True,
                    "modules": rows,
                }
                if variant == "core_missing_module":
                    receipt["modules"].pop()
                elif variant == "core_wrong_root":
                    rows[0]["printed_axiom_lists"] = {"Unrelated.theorem": ["propext"]}
                elif variant == "core_extra_axiom":
                    rows[0]["printed_axiom_lists"][
                        next(iter(rows[0]["printed_axiom_lists"]))
                    ].append("Untrusted.custom")
                elif variant == "core_wrong_compiler":
                    receipt["compiler_sha256"] = "0" * 64
                elif variant == "core_wrong_version":
                    receipt["compiler_version"] = "Lean (version 0.0.0)"
                elif variant == "core_wrong_artifact":
                    (core_build / (CORE[0] + ".olean")).write_bytes(b"changed")
                elif variant == "core_missing_artifact":
                    (core_build / (CORE[0] + ".olean")).unlink()
                elif variant == "core_empty_artifact":
                    (core_build / (CORE[0] + ".olean")).write_bytes(b"")
                module.write_json(core_receipts / "result.json", receipt)
                return subprocess.CompletedProcess(
                    command, 1 if variant == "core_nonzero" else 0, b"", b""
                )

            def fake_run(command, **kwargs):
                if command[0] == "lake":
                    if variant.startswith("lake_probe_"):
                        changed = (
                            inputs["lake_config"]
                            if variant == "lake_probe_config_changed"
                            else source
                        )
                        changed.write_bytes(changed.read_bytes() + b"\n")
                        if variant == "lake_probe_source_manifest_changed":
                            data = json.loads(manifest.read_text(encoding="utf-8"))
                            data["sources"][source.name] = {
                                "sha256": module.digest(source),
                                "bytes": source.stat().st_size,
                            }
                            manifest.write_text(json.dumps(data), encoding="utf-8")
                    cache = root / "lean/.lake/build/lib/lean"
                    cache.mkdir(parents=True)
                    (cache / (CORE[0] + ".olean")).write_bytes(b"ignored project cache")
                    return subprocess.CompletedProcess(
                        command,
                        0,
                        json.dumps(
                            {
                                "lean": str(compiler),
                                "lean_path": os.pathsep.join(
                                    [str(library), str(cache)]
                                ),
                            }
                        ),
                        "",
                    )
                if command[0] == sys.executable:
                    return emit_core(command)
                name = Path(command[-1]).stem
                self.assertIn(name, roots_for_suite)
                self.assertIn("--trust=0", command)
                self.assertEqual(kwargs["cwd"], output)
                self.assertEqual(
                    kwargs["env"]["LEAN_PATH"].split(os.pathsep),
                    [str(output), str(core_build), str(library)],
                )
                target = Path(command[command.index("-o") + 1])
                if variant != "no_output" or name != focus:
                    target.write_bytes(
                        b"" if variant == "empty_output" else b"mock artifact"
                    )
                roots = [name + "." + r for r in roots_for_suite[name]]
                axioms = "propext, Classical.choice, Quot.sound"
                if name == focus:
                    if variant == "missing_root":
                        roots.pop()
                    elif variant == "duplicate_root":
                        roots.append(roots[0])
                    elif variant == "unexpected_root":
                        roots[-1] = "Unrelated.theorem"
                    elif variant == "missing_axiom":
                        axioms = "propext, Quot.sound"
                    elif variant == "duplicate_axiom":
                        axioms += ", propext"
                    elif variant == "unexpected_axiom":
                        axioms += ", Untrusted.custom"
                    elif variant == "core_changed_after":
                        (core_build / (CORE[0] + ".olean")).write_bytes(
                            b"later mutation"
                        )
                    elif variant == "stability_changed_after":
                        (output / "CountD1Stability.olean").write_bytes(
                            b"later mutation"
                        )
                    elif variant == "snapshot_changed":
                        (output / (name + ".lean")).write_bytes(b"changed")
                    elif variant == "manifest_drift_after_compile":
                        data = json.loads(manifest.read_text(encoding="utf-8"))
                        data["sources"][source.name]["sha256"] = "0" * 64
                        manifest.write_text(json.dumps(data), encoding="utf-8")
                    elif variant.endswith("_changed") and not variant.startswith(
                        "lake_probe_"
                    ):
                        key = variant.removesuffix("_changed")
                        changed = compiler if key == "compiler" else inputs[key]
                        changed.write_bytes(changed.read_bytes() + b"\n")
                stdout = "\n".join(
                    f"'{r}' depends on axioms: [{axioms}]" for r in roots
                ).encode()
                if variant == "warning":
                    stdout += b"\nwarning: test warning"
                if variant == "timeout":
                    raise subprocess.TimeoutExpired(command, 240, output=stdout)
                return subprocess.CompletedProcess(
                    command, 1 if variant == "nonzero" else 0, stdout, b""
                )

            argv = [
                str(verifier),
                "--run",
                "../escape" if variant == "path_escape" else "test",
            ]
            if suite != "law":
                argv.extend(["--suite", suite])
            if variant not in {
                "positive_lake",
                "lake_shadow",
            } and not variant.startswith("lake_probe_"):
                argv.extend(
                    [
                        "--mode",
                        "existing-cache",
                        "--lean-executable",
                        str(compiler),
                        "--library",
                        str(library),
                    ]
                )
            with (
                patch.object(sys, "argv", argv),
                patch.object(module.subprocess, "run", side_effect=fake_run),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                try:
                    code = module.main()
                except SystemExit as error:
                    code = error.code
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    subprocess.SubprocessError,
                ):
                    code = 1
            if variant in {"reused_run", "reused_core_run"}:
                self.assertEqual((reused / "sentinel").read_bytes(), b"keep")
            receipt_file = output / "result.json"
            receipt = (
                json.loads(receipt_file.read_text(encoding="utf-8"))
                if receipt_file.is_file()
                else None
            )
            if variant.startswith("positive"):
                self.assertEqual(code, 0)
                self.assertEqual(receipt["status"], "PASS")
                self.assertTrue(all(receipt["checks"].values()))
                self.assertEqual(receipt["suite"], suite)
                self.assertEqual(
                    [r["module"] for r in receipt["modules"]], list(roots_for_suite)
                )
            else:
                self.assertNotEqual(code, 0)
                if receipt is not None:
                    self.assertEqual(receipt["status"], "FAIL")
                if variant.startswith("lake_probe_"):
                    self.assertFalse(output.exists())
                    self.assertFalse(core_build.exists())
                if variant == "manifest_drift_after_compile":
                    self.assertFalse(receipt["checks"]["source_manifests_valid"])
            return receipt

    def test_mock_positive_controls(self):
        for case in ("positive", "positive_lake"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_source_and_manifest_validation(self):
        for case in (
            "source_tamper",
            "core_source_tamper",
            "stability_source_tamper",
            "schema",
            "manifest_roots",
            "source_size",
            "admission",
            "kernel_bypass",
            "wrong_toolchain",
        ):
            with self.subTest(case=case):
                self.run_case(case)

    def test_fresh_directories_required(self):
        for case in ("reused_run", "reused_core_run", "path_escape"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_shadowed_project_artifacts_rejected(self):
        for case in ("shadow_core", "shadow_stability", "shadow_bridge", "lake_shadow"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_core_receipt_and_artifact_validation(self):
        for case in (
            "core_missing_module",
            "core_wrong_root",
            "core_extra_axiom",
            "core_wrong_compiler",
            "core_wrong_version",
            "core_wrong_artifact",
            "core_missing_artifact",
            "core_empty_artifact",
            "core_timeout",
            "core_nonzero",
        ):
            with self.subTest(case=case):
                self.run_case(case)

    def test_exact_roots_and_axioms_required(self):
        for case in (
            "missing_root",
            "duplicate_root",
            "unexpected_root",
            "missing_axiom",
            "duplicate_axiom",
            "unexpected_axiom",
        ):
            with self.subTest(case=case):
                self.run_case(case)

    def test_process_and_artifact_controls(self):
        for case in ("no_output", "empty_output", "warning", "nonzero", "timeout"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_inputs_and_imports_must_remain_unchanged(self):
        cases = ["core_changed_after", "stability_changed_after", "snapshot_changed"]
        cases += [
            key + "_changed"
            for key in (
                "verifier",
                "core_verifier",
                "core_manifest",
                "dependency_lock",
                "lake_config",
                "toolchain",
                "compiler",
                "CountD1LawBridge",
                "CountD1Stability",
                "CountSharpness",
            )
        ]
        for case in cases:
            with self.subTest(case=case):
                self.run_case(case)

    def test_research_suite_acceptance_and_new_source_bindings(self):
        for case in (
            "positive",
            "positive_lake",
            "schema",
            "manifest_roots",
            "source_size",
            "admission",
            "kernel_bypass",
        ):
            with self.subTest(case=case):
                self.run_case(case, "research")
        for name in (
            "CountProbabilityBridge",
            "CountD1VarianceCoverage",
            "CountD1BackgroundUncertainty",
            "CountFiniteSampleMean",
        ):
            for prefix in ("tamper_", "shadow_"):
                with self.subTest(module=name, prefix=prefix):
                    self.run_case(prefix + name, "research")

    def test_research_suite_rejects_incomplete_or_changed_proofs(self):
        for case in (
            "missing_root",
            "unexpected_axiom",
            "missing_axiom",
            "no_output",
            "empty_output",
            "warning",
            "nonzero",
            "timeout",
            "core_missing_module",
            "core_changed_after",
            "stability_changed_after",
            "snapshot_changed",
            "CountProbabilityBridge_changed",
            "CountD1VarianceCoverage_changed",
            "CountD1BackgroundUncertainty_changed",
            "CountFiniteSampleMean_changed",
            "reused_run",
            "reused_core_run",
            "path_escape",
        ):
            with self.subTest(case=case):
                self.run_case(case, "research")

    def test_environment_resolution_cannot_rebaseline_changed_inputs(self):
        for suite in ("law", "research"):
            for case in (
                "lake_probe_source_changed",
                "lake_probe_source_manifest_changed",
                "lake_probe_config_changed",
            ):
                with self.subTest(suite=suite, case=case):
                    self.run_case(case, suite)

    def test_manifest_binding_rechecked_after_compilation(self):
        for suite in ("law", "research"):
            with self.subTest(suite=suite):
                self.run_case("manifest_drift_after_compile", suite)


if __name__ == "__main__":
    unittest.main()
