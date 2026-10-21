# Maintenance controls and limits

This is a single-maintainer research project. Its checks protect reproducibility
and reviewability; they do not establish complete security or scientific truth.

- Python has no runtime dependencies. Development dependencies are version- and
  hash-locked in `requirements-dev.txt`, a format Dependabot recognizes.
  Lean/mathlib and all transitive package revisions are pinned.
- Actions use full commit hashes. Downloaded scanner and Elan binaries have
  fixed versions and verified SHA256 digests. Toolchains, upstream dependency
  caches, hosted runner images and their providers remain trusted inputs.
- Pull requests run without write credentials. CI uses read-only repository
  access; Scorecard alone has the permissions needed for its report and OIDC.
  The SARIF uploader is a reporting utility, not CodeQL analysis or an AI review.
- Installed-wheel and rebuilt-source tests, exact arithmetic tests, proof
  compilation, workflow checks and secret scans are separate checks.
- The local coverage gate replaces an external coverage service. No DCO or
  automated review app is installed; contributors instead confirm contribution
  rights in the contributing guide. No automatic merging is configured.
- CodeQL is deferred: GitHub enables Copilot Autofix by default when CodeQL is
  enabled. A maintainer must first establish and verify the desired off setting
  before activating that integration. No AI review app is requested.
- GitHub is the available contact channel. There is no separate confidential
  maintainer channel for conduct reports; the conduct policy explains that
  limitation and distinguishes GitHub's private platform-abuse reports.
- Account-level two-factor authentication has not been independently verified.
  Its state must not be inferred from a missing API field.

Repository settings are hosted state, not guaranteed by this document. Verify
their current state in GitHub. A no-bypass rule set can protect signed, linear
history against deletion and force-pushing. A separate rule set may permit an
administrator to bypass PR/check requirements for locally signed maintenance.
Such a bypass is an explicit exception, not independent review. Administrators
can still change the rules themselves.

Sources: [GitHub Autofix settings](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/disabling-copilot-autofix-for-code-scanning),
[repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).
