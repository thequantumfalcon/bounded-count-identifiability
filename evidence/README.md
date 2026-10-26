# Verification record and trust limits

The [written theorem](../docs/theorem.md) and [claim map](../docs/claims.md)
state what each proof and calculation establishes. Build records below tie
checks to particular source versions; they do not establish originality,
independent human review or physical validation.

## Recorded hosted build

Checked on 23 October 2026: commit
`45ad4511725bf5f77be34197dad6208f7a9b9b63` passed
[CI run 40049548994](https://github.com/thequantumfalcon/bounded-count-identifiability/actions/runs/40049548994)
and the separate
[Isabelle run 40049548989](https://github.com/thequantumfalcon/bounded-count-identifiability/actions/runs/40049548989).
The CI run includes the pinned Lean build, fresh compilation, axiom audits,
kernel replay, certificate controls, Python package/artifact checks on Linux
and Windows, fuzzing, FLINT, Sage, the browser demo, the synthetic count-model
experiment and synthetic emitter-counting comparisons. GitHub reports all 12
CI jobs and the Isabelle job as successful. These results apply to that commit,
not to subsequent edits; inspect the exact commit's
[Actions results](https://github.com/thequantumfalcon/bounded-count-identifiability/actions)
when reproducing a later version.

The current Lean research suite has 28 modules and 173 registered theorem roots.
The 21 modules and 124 roots in the earlier index describe an older milestone;
four later modules added 34 roots and the reconstruction extensions add another
three modules and 15 roots. Isabelle's 31 roots are counted separately.

Saved execution records include source hashes and outputs, identifying the
files checked. They do not imply independent review. Earlier records retain
their original scope.

## Earlier checks and their limits

The [internal tooling cross-checks](../docs/red-team-followup.md) document a confirmed
weakness in the older verifier: compilation output could forge an allowed
axiom message, and core theorem coverage was incomplete. Those historical
verification records do not prove resistance to that attack. The repair separates
the generated axiom query from proof compilation and checks an exact root registry;
stored-proof replay adds a different check. Neither is a hostile-code sandbox.

The portable public entry point is the pinned [Lean project](../lean/README.md).
Its [local verification record](../lean/verification/local-existing-cache-formatted/result.json)
records fresh compilation of all six modules with `--trust=0`, against existing
dependency artifacts. Source, verifier, lock and output hashes bind that run
to their historical bytes, including the earlier verifier. Selected theorem
lists reported only `propext`,
`Classical.choice` and `Quot.sound`. Checking establishes encoded statements
relative to the trusted implementation and axioms.

The separate [initial hosted CI run](https://github.com/thequantumfalcon/bounded-count-identifiability/actions/runs/39552914288)
passed on a fresh Linux runner, including dependency retrieval, the six-module
build and fresh recompilation. Its [Linux verification record](../lean/verification/github-initial-d720227/result.json)
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
portable suite that recompiles all twenty-eight project modules. Its verification
records belong to their exact sources and verifier. The
[background-uncertainty checker record](background-uncertainty-kernel-check.json)
binds that source to an additional local Lean4Lean execution accepting five
roots and 10,498 declarations. Lean4Lean shares implementation ancestry with
Lean; the exporter, dependencies and runtime remain trusted. That run included
no fresh invalid-export rejection test, and it does not run in CI.

The [reconstruction checker record](reconstruction-kernel-checks.json) binds the
three added reconstruction sources and their three core imports to a fresh
development compilation. All 17 non-internal theorem declarations, including
two generated equation theorems, were exported and checked by Nanoda and the
related con-leche/con-ron family. Positive, altered-proof and unpermitted-axiom
controls were run in the same audit. Nanoda's axiom-printer diagnostic and the
con checkers' declaration-order diagnostics are retained. This record establishes
the encoded series/law, derivative and conditional admissibility lemmas, not the
complete arbitrary-cumulant inverse or a physical model. The record does not
bundle the checker installations or large proof export; the standard Lean
verification and replay commands above are the portable public reproduction.

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

CI results belong to the exact commit checked. Historical verification records
must not be presented as results for changed proof bytes. Proof changes require new checks,
not merely updated hashes. No item proves novelty, physical assumptions,
practical sample size, external peer review or universal software security.
Unresolved obligations remain in the [roadmap](../docs/roadmap.md).

The finite-mixture extension adds eight registered roots to the research suite.
Its fresh compilation, separate axiom audit and bundled-kernel replay are part
of the current CI, not retroactively part of the earlier 21-module records.
The separate `flint-ci-receipt` records exact finite calculations with a different
arithmetic implementation. The `atheris-ci-receipt` records bounded
coverage-guided software tests and their deliberate-fault control. Neither
artifact is an external mathematical review or a physical measurement.

The finite-mixture sampling extension adds eight further roots for actual
square integrability, total variance, conservative variance ceilings and
simultaneous moment coverage. They are included in the current 28-module,
173-root research suite and its CI compilation, separate axiom audits and
kernel replay. Earlier 21- and 22-module records retain their original scope.
The expanded FLINT calculation checks total-variance identities and ceilings,
rejects applying the fixed-rate ceilings to mixtures, and checks the arithmetic
of the written shared-rate dependence counterexample. These finite controls
do not certify a sampler or measured independence.

The [local synthetic execution record](count-stress-check.json) binds its
reported parameters, results and raw-data hashes to the public script. The
separate `count-stress-ci-receipt` artifact retains the synthetic experiment's
executed source, protocol, raw counts and analysis for 14 days. The
[experiment guide](../docs/stress-test.md) explains the known-law variance
benchmark, deterministic controls and retention limits. Statistical inclusion
and separation are reported outcomes, not CI acceptance criteria, empirical
coverage-rate estimates or physical measurements.

A separate [local additional-checker record](finite-mixture-sampling-kernel-check.json)
binds the eight finite-mixture sampling roots to fresh compilation, a separate
axiom audit and Lean4Lean acceptance of 34,903 declarations. The existing
wrong-type control exited 1 with an explicit kernel type-mismatch diagnosis;
error-printer panics and a fallback printer remain, so its diagnostics were not
clean. Twenty-two compiled project dependencies were reused, with their hashes
checked against the earlier verification record.
Lean4Lean shares Lean kernel ancestry; this local record offers limited
implementation independence and is not a CI run, outside mathematical review
or validation of the model's physical assumptions.

The exact rational decision extension adds eight roots for point, pair and global
real-region decisions. Its concrete certificate runner checks 19 correct queries
and three deliberately wrong answers, with separate axiom audits and verification
records identifying the source hashes inside the required formal CI job.
Historical records retain their original module lists. See the
[query guide](../lean/extensions/confidence-executable/README.md).

The [local executable-decision checker record](confidence-executable-kernel-check.json)
binds all eight universal roots to fresh compilation, a separate axiom audit
and Lean4Lean acceptance of 10,613 declarations. The earlier wrong-type
control was explicitly rejected; its known error-printer panics and fallback
remain disclosed. The run reused 21 compiled project objects tied to their
source hashes and the upstream runtime. It checks the decision theorems,
not the Python frontend,
Sage execution or model calibration. Lean4Lean's shared kernel ancestry and
the common exporter limit implementation independence.

The count-confidence extension adds ten roots for natural-count aggregation,
outward rational radii and conditional coverage, including the probability of
an empty Boolean verdict. Its concrete count suite checks six correct records
and five isolated wrong calculations. See the
[count-to-box guide](../lean/extensions/counts-confidence/README.md).

The [local count-confidence checker record](counts-confidence-kernel-check.json)
binds all ten universal roots to fresh compilation, a separate axiom audit
and Lean4Lean acceptance of 34,779 declarations. The earlier wrong-type
control was explicitly rejected; its known error-printer panics and fallback
remain disclosed. The run reused 24 compiled project objects tied to their
source hashes and the upstream runtime. It checks the count-confidence theorems,
not the Python frontend,
Sage execution or model calibration. Lean4Lean's shared kernel ancestry and
the common exporter limit implementation independence.

## Isabelle endpoint reconstruction

[The local record](isabelle-endpoints-check.json) binds the final Isabelle
proof and audit sources to a successful 31-root run, two reviewed conservative
definitions, zero transitive oracle dependencies and four expected rejections.
[Reproduction instructions](../isabelle/README.md) explain the exact family,
explicit report export and separate hosted Linux workflow. This is a distinct
proof implementation with shared project provenance, not outside human review
or verification of the entire Sage program.

## Historical repository settings

The [dated verification index](verification-index-2026-10-21.json) links the
completed 21-module, 124-root milestone at commit `68e644a`, its hosted records
and a repository-settings readback. CodeQL was configured and both open CodeQL
and Dependabot alert counts were zero at that readback. The maintainer's earlier
confirmations of account 2FA and Copilot Autofix are listed separately; the API
capture did not verify them. Settings and alerts can change, and a successful
Scorecard workflow does not mean a perfect score. These settings are maintenance
evidence, not evidence for the mathematical claims.
