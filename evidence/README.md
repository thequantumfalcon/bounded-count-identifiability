# Verification record and trust limits

Start with the [dated verification index](verification-index-2026-10-21.json).
It links the completed 21-module, 124-root milestone at commit `68e644a`, its
hosted receipts and a fresh repository-settings readback. CodeQL was configured
and both open CodeQL and Dependabot alert counts were zero at that readback.
The maintainer's earlier confirmations of account 2FA and Copilot Autofix are
listed separately; the API capture did not verify them. Settings and alerts can
change, and a successful Scorecard workflow does not mean a perfect score.

The index records a completed earlier milestone, not the later repair commit
that contains it. It cannot certify its own future commit hash. For that commit,
inspect its [Actions runs](https://github.com/thequantumfalcon/bounded-count-identifiability/actions)
and uploaded receipts. The original records below remain unchanged.

The [red-team follow-up](../docs/red-team-followup.md) documents a confirmed
weakness in the older verifier: compilation output could forge an allowed
axiom message, and core theorem coverage was incomplete. Those historical
receipts do not prove resistance to that attack. The repair separates the
generated axiom query from proof compilation and checks an exact root registry;
stored-proof replay adds a different check. Neither is a hostile-code sandbox.

The portable public entry point is the pinned [Lean project](../lean/README.md).
Its [local receipt](../lean/verification/local-existing-cache-formatted/result.json)
records fresh compilation of all six modules with `--trust=0`, against existing
dependency artifacts. Source, verifier, lock and output hashes bind that run
to their historical bytes, including the earlier verifier. Selected theorem
lists reported only `propext`,
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
portable suite that recompiles all twenty-one project modules. Its receipts belong
to their exact sources and verifier. The
[background-uncertainty checker record](background-uncertainty-kernel-check.json)
binds that source to an additional local Lean4Lean execution accepting five
roots and 10,498 declarations. Lean4Lean shares implementation ancestry with
Lean; the exporter, dependencies and runtime remain trusted. That run included
no fresh invalid-export rejection test, and it does not run in CI.

A subsequent [probability and sampling checker record](probability-sampling-kernel-checks.json)
covers 26 roots across the four probability, variance, sample-mean and uncertainty
extensions. Lean4Lean accepted 35,290 declarations; nanoda checked 37,053 with
no typechecker errors and one retained axiom-printing diagnostic. Both rejected
a wrong-type export fixture, with abnormal exits and raw diagnostics preserved
locally. This is limited additional checking, with shared exporter, dependencies
and host; one negative fixture does not prove checker correctness. The record
is not a hosted CI run. A separate [confidence-zero checker record](confidence-zero-kernel-checks.json)
covers the six newer confidence roots. Lean4Lean accepted 33,492 declarations;
nanoda checked 35,233 with no typechecker errors and one retained error,
"Unable to print axioms", from its pretty-printer. Both checkers rejected the
wrong-type control via abnormal exits. This is checker diversity within the
same campaign, with shared exporter, dependencies and host; it supplies neither
independent human review nor hosted CI evidence.

A separate [Poisson-observation checker record](poisson-observation-kernel-checks.json)
covers the eleven new exponential-moment and independent-observation roots.
Lean4Lean accepted 34,256 declarations; nanoda checked 35,999 with no typechecker
errors and the retained "Unable to print axioms" pretty-printer diagnostic.
Both checkers reran and rejected the earlier coefficient wrong-type fixture
through abnormal exits; this was not a mutation of the new Poisson proofs.
The same shared-component and reproduction limits apply. These extra checks
do not run in hosted CI or supply outside human review.

A further [analytic, moment and projection checker record](analytic-moments-projection-kernel-checks.json)
covers the 47 roots in the six new modules. Lean4Lean accepted 41,902
declarations; nanoda checked 43,749 with no typechecker errors and the retained
axiom-printing diagnostic. Both reran the earlier wrong-type control and
exited abnormally, so this is not evidence of clean semantic rejection or
exhaustive checker testing. The record binds the exact public sources and
documents a historical, noncompiler documentation input excluded from the
new import check. All compiler and proof inputs remained bound. The shared
exporter, implementation ancestry, dependencies and host limit independence;
these additional checkers do not run in CI or constitute outside human review.

Python supplies finite exact-arithmetic comparisons. A fresh local
[Sage 10.8 projection check](projection-sage-check.json) passed seven boundary
fixtures, 3,375 exact membership comparisons and 1,038 checks of witnesses
against the original constraints. Its source hash and limitations are recorded.
The initial launcher lacked the runtime's Singular environment; the recorded
environment run passed, and both local attempts are retained. This particular
record is local and predates the hosted Sage job. That job has its own
`sage-ci-receipt` artifact, binding the source and container image to its output;
inspect the result for the commit being reviewed. These programs are not
formally verified and could share modeling mistakes. See
[reproduction commands](../docs/reproduction.md).

CI results belong to the exact commit checked. Historical receipts must not be
presented as results for changed proof bytes. Proof changes require new checks,
not merely updated hashes. No item proves novelty, physical assumptions,
practical sample size, external peer review or universal software security.
Unresolved obligations remain in the [roadmap](../docs/roadmap.md).
