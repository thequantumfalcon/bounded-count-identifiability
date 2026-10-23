# 2. Preserve useful checks without overstating repository health

Status: accepted for maintenance after the red-team repairs.

This is a solo-maintained research repository. A successful workflow means its
configured checks completed; it does not establish a perfect security score,
independent mathematical review or physical validity.

## Changes and dependencies

Development dependencies remain version-pinned with download hashes. Updates
are reviewed against upstream releases and tested together, including installed
wheels and a rebuilt source distribution. The library has no runtime
dependencies. A version-update pull request is not itself a vulnerability report.

Publication uses a locally signed commit under the maintainer's public name,
Thomas Albrecht.
That exact commit must pass the pull request checks before `main` advances to it.
Create one final signed commit atop current `main` on the PR branch before
validation, then advance `main` by a local fast-forward to that same commit.
Any subsequent squash, amendment or source change creates a different commit
that needs its own checks. The non-bypassable rules require signed linear
history, prevent deletion and force pushes, and require `ci` and
`dependency-review` from GitHub Actions. The pull-request ruleset also has no
administrator bypass. PR 16's single-commit promotion passed every applicable
rule without using the former exception; the exception was then removed.
If `main` advances during review, rebuild the final commit and repeat checks.
Do not restore a bypass to avoid a rejected push.

An additional native code-scanning ruleset requires CodeQL results before
promotion to the default branch, with no bypass actors. It blocks generic
error-level alerts and security alerts of medium severity or higher. Lower-level
diagnostics remain visible for review. This adds enforcement of current scanning;
it does not repair historical scan coverage or establish independent review.
Verify both configured languages and the actual rule-suite result for each
publication. See GitHub's [code-scanning merge protection](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/manage-your-configuration/set-merge-protection).

Repository settings are hosted state; verify them in GitHub rather than
inferring enforcement from this document. Administrators can still change the
rules themselves. See GitHub's [ruleset documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## Tooling, permissions and contacts

Lean/mathlib revisions, Actions and downloaded scanner binaries remain pinned;
binary downloads have verified SHA256 digests. Toolchains, dependency caches,
hosted runner images and providers remain trusted inputs. Pull-request CI uses
read-only access. Scorecard has the additional permissions needed to publish its
report with OIDC. Its SARIF uploader is separate from CodeQL analysis.

CodeQL default setup is configured for Python and GitHub Actions, with successful
analyses recorded for the red-team repair commit. The maintainer confirmed
Copilot Autofix off and account two-factor authentication enabled. Those account
and UI confirmations are separate from API-verified code-scanning results;
neither setting is inferred from a missing API field. See GitHub's
[Autofix settings](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/disabling-copilot-autofix-for-code-scanning).

The local coverage gate replaces an external coverage service. No DCO,
automated review app or automatic merging is configured. Contributors confirm
contribution rights in the contributing guide. GitHub is the available contact
channel; the conduct policy explains the lack of a separate confidential
maintainer channel and distinguishes GitHub's platform-abuse reporting.

## Scorecard recommendations

| Finding | Response and remaining limit |
| --- | --- |
| Branch protection | Enforce checks even for administrators. Independent approval requirements remain disabled while there is only one maintainer. |
| Code review | Automated checks and maintainer review are not independent approval. A second person's review cannot be manufactured. |
| Fuzzing | Run bounded, seeded differential checks and Atheris coverage-guided mutation against the exact-arithmetic oracle. Check engine detection of a deliberately faulty API and replay the captured input against the genuine API. These finite tests do not prove software correctness. See the [fuzzing guide](../../fuzz/README.md). |
| SAST history | Run CodeQL on current changes. PR 3 has no historical scan; PR 4 has successful setup analyses that Scorecard does not recognize as its required SAST-app check. Preserve that distinction and the original history. |
| Maintenance history | Repository age and sustained maintenance require elapsed time and actual work. |
| Best-practices badge | The program is a public self-certification, not independent security review. Assess all criteria, including human developer-knowledge attestations, before submitting a passing claim. Registration alone would not establish those facts. |

Inspect the exact commit's Actions results and the actual Scorecard report.
The configured workflow alone is not evidence that it ran or passed. The
recommendations remain visible even when they cannot be resolved immediately.

## Scientific obligations

Repository maintenance supplies evidence about the artifact, not its physical
model or historical priority. The [proof roadmap](../roadmap.md) identifies
remaining mathematical and software-verification tasks and the measurements
needed for a physical study. The [review request](../reviewer-request.md) and
[originality review](../originality-review.md) support outside scrutiny; neither
establishes that it has occurred. Further automated checks in the same research
campaign do not count as independent human review.
