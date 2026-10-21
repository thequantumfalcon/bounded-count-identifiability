# Verification record and trust limits

The portable public entry point is the pinned [Lean project](../lean/README.md).
Its [local receipt](../lean/verification/local-existing-cache-formatted/result.json)
records fresh compilation of all six modules with `--trust=0`, against existing
dependency artifacts. Source, verifier, lock and output hashes bind that run
to the published files. Selected theorem lists contain only `propext`,
`Classical.choice` and `Quot.sound`. Checking establishes encoded statements
relative to the trusted implementation and axioms.

The separate [initial hosted CI run](https://github.com/thequantumfalcon/bounded-count-identifiability/actions/runs/39552914288)
passed on a fresh Linux runner, including dependency retrieval, the six-module
build and fresh recompilation. Its [Linux receipt](../lean/verification/github-initial-d720227/result.json)
is preserved alongside the logs. Python package and artifact checks also passed
on Linux (3.11 and 3.13) and Windows (3.13). See the
[hosted validation record](hosted-validation.json) for the checked commit and
repository-setting boundaries.

[Development checker results](development-kernel-checks.json) summarize earlier
checks of selected dependency-closed exports. This is a sanitized extraction of
development evidence, not a new run. Large exports, checker installations and
the development workspace are not bundled, so the record alone does not
reproduce those extra runs. Several checkers share code or ancestry. Accepted
checks do not imply independent human review or independent specifications.
One checker's axiom-report printer warning is distinguished from its zero
type-checking errors in the record.

The separately published [D=1 stability extension](../lean/extensions/d1/README.md)
has its own source manifest and portable compilation check. Its
[additional kernel-check record](d1-stability-kernel-checks.json) summarizes six
local executions on the same dependency-closed export, including Lean4Lean.
That historical record does not mean the six checkers run in public CI. It
preserves the same independence limits and nanoda's axiom-printing diagnostic.

The [D=1 finite-law connection](../lean/extensions/d1-law/README.md) has a
separate portable verifier and [historical additional-checker record](d1-law-kernel-checks.json).
The record binds the unchanged source to six earlier checker executions and
retains the axiom-printing diagnostic. Those historical extra checkers do not
run in CI; the public verifier separately recompiles the core and both
extensions. Neither form of checking supplies external human review.

The [research extensions](../docs/probability-extensions.md) have a separate
portable suite that recompiles all twelve project modules. Its receipts belong
to their exact sources and verifier. The
[background-uncertainty checker record](background-uncertainty-kernel-check.json)
binds that source to an additional local Lean4Lean execution accepting five
roots and 10,498 declarations. Lean4Lean shares implementation ancestry with
Lean; the exporter, dependencies and runtime remain trusted. That run included
no fresh invalid-export rejection test, and it does not run in CI. No additional
kernel check is claimed here for the other three new extensions.

Python supplies finite exact-arithmetic comparisons; Sage performs a narrow
algebraic projection check. These programs are not formally verified and could
share modeling mistakes. See [reproduction commands](../docs/reproduction.md).

CI results belong to the exact commit checked. Historical receipts must not be
presented as results for changed proof bytes. Proof changes require new checks,
not merely updated hashes. No item proves novelty, physical assumptions,
practical sample size, external peer review or universal software security.
Unresolved obligations remain in the [roadmap](../docs/roadmap.md).
