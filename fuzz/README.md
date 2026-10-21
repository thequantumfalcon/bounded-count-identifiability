# Bounded differential fuzzing

With the package installed, run:

```sh
python fuzz/exact_counts.py --seed 20261021 --iterations 1000
python -m unittest discover -s tests -p test_fuzz.py -v
```

The runner always checks the eight named boundary cases in `corpus.json`, then
derives additional 17-byte inputs from SHA-256 of the unsigned 64-bit seed and
case index (both big-endian eight-byte integers). A failure prints the exact hex
input for `python fuzz/exact_counts.py --replay HEX`. Generation is reproducible
without reliance on a particular random-number-generator implementation.

Each input generates an exact rational probability law, a nonnegative Poisson
background, a matching-distribution parameter and invalid controls. The target
compares the installed package against polynomial multiplication and the
moment/cumulant set-partition identity grouped by integer partitions. The
matching-law oracle counts permutations using derangement counts and then
independently thins fixed points. Neither oracle calls package arithmetic
functions; they do share Python's exact `Fraction` arithmetic. The tests confirm
that five deliberately faulty injected implementations are detected. These
controls measure selected fault detection, not detection of every possible bug.

Bounds: degree and moment order at most 8, at most 9 probability weights of
0 through 255, background numerator at most 255 and denominator at most 16,
and at most 10,000 generated cases per invocation. Nonzero probability
normalization denominators are at most 2,295. Zero weights become a point mass.
These bounds limit rational arithmetic and combinatorial work; use a CI timeout
as a separate wall-clock bound. The harness performs no networking or file writes.
Checks remain enabled under `python -O`.

The JSON result binds the target, corpus and installed package's core source by
SHA-256. This is a record of the files examined, not a signature or a guarantee
that the execution environment is trustworthy.

This runner is finite deterministic differential fuzzing. The separate Atheris
integration below adds coverage-guided generation using the same exact oracles.
Neither approach establishes a universal mathematical proof, physical validity,
or outside human review.

## Coverage-guided Linux check

With the package installed, use CPython 3.12, 3.13 or 3.14 on Linux x86_64:

```sh
python -m pip install --require-hashes --only-binary=:all: --no-deps -r fuzz/requirements.txt
python fuzz/run_atheris.py --output build/atheris-local --seconds 60
```

Use a new output directory for each run. The dependency file pins the official
[Atheris 3.1.0 wheels](https://pypi.org/project/atheris/3.1.0/) by SHA256. Atheris
is a development-only dependency; the library still has no runtime dependencies.
The target imports both the installed package and the differential harness under
[Atheris bytecode instrumentation](https://github.com/google/atheris#python-coverage).
The engine mutates the eight seed cases in `corpus.json` and uses observed
coverage to select further inputs.

The default run requests a 60-second engine budget or 10,000 engine executions,
with input length at most 17 bytes, a five-second per-input timeout and a 512 MB
RSS limit. Engine timing is approximate; the driver additionally enforces a
105-second process deadline for this run and 30 seconds for each control.
These limits supplement the
degree, moment-order and rational-arithmetic bounds described above. The
callback performs no networking or file writes; Atheris saves new corpus inputs
and failure artifacts inside the requested output directory.

After the genuine API run, a separate process injects an incorrect zeroth
factorial moment into a proxy API. The installed package and the exact oracle
remain unchanged. The driver requires Atheris to report the named injected
failure, exit with its failure code and save a reproducing input. A final process
must accept that same input against the genuine API. The five existing
deterministic fault controls remain in `tests/test_fuzz.py`; this extra control
checks the engine-to-oracle failure path.

`result.json` records observed engine execution statistics, source hashes,
process outcomes and hashes of the logs, corpus and control artifact. A positive
coverage count and observed package instrumentation are required. These counts
do not give a percentage of code coverage or exhaustive input coverage. Hashes
bind evidence to files; they do not establish a trustworthy execution host.

The same seed need not produce an identical campaign across machines or engine
versions, especially with a wall-clock cutoff. Preserve the recorded corpus and
logs. Replay a saved input without the injected fault using:

```sh
python fuzz/atheris_target.py PATH_TO_INPUT -runs=1 -max_len=17 -timeout=5 -rss_limit_mb=512
```

The CI job retains the corpus and receipts as an artifact. Its actual run result,
rather than the presence of the configuration, establishes execution evidence.
CI uses the ordinary unprivileged hosted runner with read-only repository
permissions. It does not enforce a separate network namespace. Local validation
also exercised the driver in a Linux namespace without network interfaces;
that additional isolation is not claimed for hosted CI.
The existing cross-platform deterministic runner remains part of regular tests
and release checks. Atheris changes input generation and instrumentation; it
shares the mathematical oracle and exact `Fraction` arithmetic, so it is not an
independent reimplementation. Scorecard's [Python detector](https://github.com/ossf/scorecard/blob/v5.6.0/checks/raw/fuzzing.go)
recognizes Atheris; inspect the actual report rather than treating detection as
evidence of comprehensive testing.
