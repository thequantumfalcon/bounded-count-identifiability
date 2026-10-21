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

This is finite deterministic differential fuzzing, not coverage-guided fuzzing,
a universal mathematical proof, physical validation, or outside human review.
It does not establish that Scorecard will recognize a fuzzing integration.
[Atheris](https://github.com/google/atheris) is a possible future coverage-guided
engine; its documented Linux/macOS support does not include this project's local
Windows environment. No Atheris execution or integration is claimed here.
