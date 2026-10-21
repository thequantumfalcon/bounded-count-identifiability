"""Independent arithmetic/input controls; Lean checks the emitted propositions."""

from fractions import Fraction as F
import hashlib
import importlib.util
import os
from pathlib import Path
import py_compile
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples/d1_count_certificates.py"
RUNNER_SOURCE = ROOT / "lean/check_certificates.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


emitter = load("count_certificate_tests_emitter", SOURCE)
runner = load("count_certificate_tests_runner", RUNNER_SOURCE)


def grid_ceiling_by_bisection(value, digits):
    """Independent oracle: integer bisection, without square-root operations."""
    scale = 10**digits
    low, high = 0, 1
    while F(high, scale) ** 2 < value:
        high *= 2
    while low < high:
        middle = (low + high) // 2
        if F(middle, scale) ** 2 >= value:
            high = middle
        else:
            low = middle + 1
    return F(low, scale)


def emitted_truths(text):
    """Read this fixed numeric template and independently check its seven claims.

    This checks the proposed arithmetic, not Lean parsing, proof objects or laws.
    """
    counts_match = re.search(
        r"def observations : Fin ([0-9]+) → ℕ := !\[([0-9, ]+)\]", text
    )
    if counts_match is None:
        raise AssertionError("missing explicit observations")
    counts = tuple(int(part) for part in counts_match[2].split(","))
    N = int(counts_match[1])
    if N != len(counts) or N < 1:
        raise AssertionError("wrong observation count")
    literal = r"\(\((-?[0-9]+)\) / ([1-9][0-9]*) : ℚ\)"
    values = [F(int(n), int(d)) for n, d in re.findall(literal, text)]
    if len(values) != 14:
        raise AssertionError("unexpected rational literal inventory")
    m1, m2, B, alpha, R1, R2, R1a, a, R1c, c, R2d, d, R2e, e = values
    mean = sum((F(y, N) for y in counts), F(0))
    second = sum((F(y * y - y, N) for y in counts), F(0))
    return (
        mean == m1,
        second == m2,
        B >= 0
        and alpha > 0
        and R1 >= 0
        and R2 >= 0
        and N * alpha * R1**2 >= 2 * B + F(1, 2)
        and N * alpha * R2**2 >= 8 * B**3 + 20 * B**2 + 8 * B,
        mean - R1a == a,
        mean + R1c == c,
        second - R2d == d,
        second + R2e == e,
    )


class CountCertificateTests(unittest.TestCase):
    def test_square_root_ceiling_matches_independent_bisection(self):
        for digits in (0, 1, 3, 6, 12):
            scale = 10**digits
            cases = {F(0), F(1, 3), F(2), F(7, 13), F(10**40 + 1, 17)}
            for k in (1, 2, 9, 10, 101):
                square = F(k, scale) ** 2
                cases.update(
                    (square, square - F(1, 3 * scale**2), square + F(1, 3 * scale**2))
                )
            for value in cases:
                with self.subTest(digits=digits, value=value):
                    result = emitter.sqrt_upper(value, digits)
                    self.assertEqual(result, grid_ceiling_by_bisection(value, digits))
                    self.assertGreaterEqual(result**2, value)
                    if result > 0:
                        self.assertLess((result - F(1, scale)) ** 2, value)

    def test_zero_and_falling_factorial_averages(self):
        counts, values = emitter.prepare(["0", "1", "2", "4"], "1", "1/20")
        self.assertEqual(counts, (0, 1, 2, 4))
        self.assertEqual(values["m1"], F(7, 4))
        self.assertEqual(values["m2"], F(7, 2))
        for key, value in (
            ("a", values["m1"] - values["R1"]),
            ("c", values["m1"] + values["R1"]),
            ("d", values["m2"] - values["R2"]),
            ("e", values["m2"] + values["R2"]),
        ):
            self.assertEqual(values[key], value)
        _, zero = emitter.prepare(["0"], "0", "1/2")
        self.assertEqual((zero["m1"], zero["m2"], zero["R1"], zero["R2"]), (0, 0, 1, 0))
        _, binary = emitter.prepare(["1", "0", "1", "0"], "0", "1/2")
        self.assertEqual(binary["m2"], 0)
        self.assertEqual(binary["R2"], 0)

    def test_preserves_large_counts_and_moment_invariances(self):
        counts = ["999999999999", "0", "2"]
        _, values = emitter.prepare(counts, "1/7", "1/3", 12)
        self.assertEqual(values["m1"], F(1000000000001, 3))
        self.assertEqual(values["m2"], F(999999999999 * 999999999998 + 2, 3))
        _, reversed_values = emitter.prepare(list(reversed(counts)), "1/7", "1/3", 12)
        self.assertEqual(values, reversed_values)
        _, duplicated = emitter.prepare(counts * 2, "1/7", "1/3", 12)
        self.assertEqual(
            (values["m1"], values["m2"]), (duplicated["m1"], duplicated["m2"])
        )
        self.assertLessEqual(duplicated["R1"], values["R1"])
        self.assertLessEqual(duplicated["R2"], values["R2"])
        self.assertEqual(emitter.parse_counts(["0"] * 64), (0,) * 64)

    def test_rejects_ambiguous_or_malicious_counts(self):
        for counts in (
            [],
            ["0"] * 65,
            ("1",),
            "1",
            None,
            [True],
            [1],
            [1.0],
            ["-1"],
            ["+1"],
            ["01"],
            ["1/1"],
            ["1e2"],
            ["1.0"],
            [" 1"],
            ["1 "],
            ["1\n"],
            ["１"],
            ["1000000000000"],
            ["1]; axiom bad : False"],
        ):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                emitter.parse_counts(counts)

    def test_rejects_invalid_scalars_and_rounding_options(self):
        for value in (
            True,
            1,
            F(1),
            0.5,
            "0.5",
            "1/0",
            "1/-2",
            "01",
            "1\n",
            "９",
            "9" * 65,
            "1/" + "9" * 65,
            "1); axiom bad : False",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                emitter.rational(value)
        self.assertEqual(emitter.rational("+2/4"), F(1, 2))
        for B, alpha in (
            ("-1", "1/2"),
            ("0", "0"),
            ("0", "-1/2"),
            ("0", "1"),
            ("0", "3/2"),
        ):
            with self.subTest(B=B, alpha=alpha), self.assertRaises(ValueError):
                emitter.prepare(["0"], B, alpha)
        for digits in (True, 1.0, "6", -1, 13):
            with self.subTest(digits=digits), self.assertRaises(ValueError):
                emitter.sqrt_upper(F(2), digits)
        for value in (-F(1), 0, True, 2.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                emitter.sqrt_upper(value, 6)

    def test_render_only_accepts_bounded_numeric_proposals(self):
        counts, values = emitter.prepare(["0", "1"], "1", "1/20")
        for bad_counts in ([0, 1], (), (True,), (-1,), (10**12,)):
            with self.subTest(counts=bad_counts), self.assertRaises(ValueError):
                emitter.render(bad_counts, values)
        for bad_values in (
            list(values.values()),
            values | {"injected": F(1)},
            {key: value for key, value in values.items() if key != "a"},
            values | {"m1": 0.5},
            values | {"m1": True},
            values | {"m1": F(10**512)},
            values | {"m1": F(1, 10**512)},
        ):
            with self.subTest(values=bad_values), self.assertRaises(ValueError):
                emitter.render(counts, bad_values)

    def test_actual_fixtures_and_controls_have_intended_exact_truth_values(self):
        for fixture in runner.COUNT_FIXTURES:
            with self.subTest(fixture=fixture):
                self.assertTrue(all(emitted_truths(emitter.certificate(*fixture))))
        expected_failures = {
            "WrongMean": (0,),
            "WrongMoment": (1,),
            "WrongRadius": (2,),
            "WrongSign": (2,),
            "WrongEndpoint": (6,),
        }
        controls = runner.count_controls()
        self.assertEqual({name for name, _ in controls}, set(expected_failures))
        for name, text in controls:
            with self.subTest(control=name):
                failed = tuple(
                    i for i, value in enumerate(emitted_truths(text)) if not value
                )
                self.assertEqual(failed, expected_failures[name])

    def test_snapshot_loader_bypasses_a_demonstrably_stale_bytecode_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.py"
            path.write_bytes(b"answer = 1\n")
            timestamp = path.stat().st_mtime_ns
            py_compile.compile(
                str(path),
                doraise=True,
                invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
            )
            path.write_bytes(b"answer = 2\n")
            os.utime(path, ns=(timestamp, timestamp))
            # Same length and timestamp make a normal import reuse the old code.
            self.assertEqual(load("stale_bytecode_control", path).answer, 1)
            loaded, digest = runner.load_emitter("fresh_snapshot_control", path)
            self.assertEqual(loaded.answer, 2)
            self.assertEqual(digest, hashlib.sha256(b"answer = 2\n").hexdigest())

    def test_snapshot_binding_rejects_source_changed_after_loading(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.py"
            path.write_bytes(b"answer = 1\n")
            _, digest = runner.load_emitter("snapshot_control", path)
            with mock.patch.multiple(
                runner,
                EMITTER_PATH=path,
                COUNT_EMITTER_PATH=path,
                EMITTER_LOADED_HASH=digest,
                COUNT_EMITTER_LOADED_HASH=digest,
            ):
                runner.check_emitter_snapshots()
                path.write_bytes(b"answer = 2\n")
                with self.assertRaisesRegex(ValueError, "emitter changed"):
                    runner.check_emitter_snapshots()

    def invoke(self, arguments, source=SOURCE):
        return subprocess.run(
            [sys.executable, str(source), *arguments],
            capture_output=True,
            timeout=10,
            check=False,
        )

    def test_cli_emits_utf8_lf_and_preserves_existing_output(self):
        arguments = ["--counts=0,1,2,4", "--background=1", "--alpha=1/20"]
        expected = emitter.certificate(["0", "1", "2", "4"], "1", "1/20").encode(
            "utf-8"
        )
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "Counts.lean"
            result = self.invoke([*arguments, "--output", str(output)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), expected)
            result = self.invoke([*arguments, "--counts=0", "--output", str(output)])
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), expected)

    def test_cli_invalid_inputs_never_create_partial_output(self):
        base = ["--counts=0,1", "--background=1", "--alpha=1/20"]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "Invalid.lean"
            for extra in (
                ["--counts="],
                ["--counts=0,,1"],
                ["--counts=-1"],
                ["--background=-1/2"],
                ["--alpha=1"],
                ["--digits=-1"],
                ["--digits=13"],
                ["--unknown-option"],
            ):
                with self.subTest(extra=extra):
                    result = self.invoke([*base, *extra, "--output", str(output)])
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertFalse(output.exists())
            wrong_suffix = Path(temporary) / "Invalid.txt"
            result = self.invoke([*base, "--output", str(wrong_suffix)])
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(wrong_suffix.exists())

    def test_runner_rejects_mixed_or_incomplete_queries_before_environment(self):
        base = ["--proof-run=unused", "--run=unused"]
        for extra, expected in (
            (["--counts=0"], "require --suite counts"),
            (["--suite=counts", "--kind=source"], "require the feasibility suite"),
            (
                ["--suite=counts", "--counts=0"],
                "requires --counts, --background and --alpha",
            ),
            (["--suite=counts", "--digits=2"], "applies only to a custom count record"),
            (
                [
                    "--suite=counts",
                    "--counts=0",
                    "--background=1",
                    "--alpha=1",
                    "--digits=6",
                ],
                "require background ceiling >= 0 and 0 < alpha < 1",
            ),
        ):
            with self.subTest(extra=extra):
                result = self.invoke([*base, *extra], RUNNER_SOURCE)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertIn(expected, result.stderr.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
