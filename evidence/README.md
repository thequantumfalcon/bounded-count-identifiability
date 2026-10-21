# Verification record and trust limits

The portable public entry point is the pinned [Lean project](../lean/README.md).
Its [local receipt](../lean/verification/local-existing-cache-formatted/result.json)
records fresh compilation of all six modules with `--trust=0`, against existing
dependency artifacts. Source, verifier, lock and output hashes bind that run
to the published files. Selected theorem lists contain only `propext`,
`Classical.choice` and `Quot.sound`. Checking establishes encoded statements
relative to the trusted implementation and axioms.

[Development checker results](development-kernel-checks.json) summarize earlier
checks of selected dependency-closed exports. This is a sanitized extraction of
development evidence, not a new run. Large exports, checker installations and
the development workspace are not bundled, so the record alone does not
reproduce those extra runs. Several checkers share code or ancestry. Accepted
checks do not imply independent human review or independent specifications.
One checker's axiom-report printer warning is distinguished from its zero
type-checking errors in the record.

Python supplies finite exact-arithmetic comparisons; Sage performs a narrow
algebraic projection check. These programs are not formally verified and could
share modeling mistakes. See [reproduction commands](../docs/reproduction.md).

CI results belong to the exact commit checked. Historical receipts must not be
presented as results for changed proof bytes. Proof changes require new checks,
not merely updated hashes. No item proves novelty, physical assumptions,
practical sample size, external peer review or universal software security.
Unresolved obligations remain in the [roadmap](../docs/roadmap.md).
