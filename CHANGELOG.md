# Changelog

Notable changes are recorded here using the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) structure.
The Python API is experimental; no stable release has been published.

## [Unreleased]

- Reviewed and updated development tools: build 1.6.1, pyproject-hooks 1.3.3,
  coverage 7.16.2, Ruff 0.17.0 and zizmor 1.30.1. Download hashes were checked
  against the corresponding PyPI release files; compatibility, security-hardening
  and formatting changes were assessed before installed-artifact testing.

- Updated build inputs to setuptools 84.2.1 and wheel 0.48.0 after the initial
  dependency scan identified
  [GHSA-h35f-9h28-mq5c](https://github.com/pypa/setuptools/security/advisories/GHSA-h35f-9h28-mq5c)
  and [GHSA-8rrh-rw8j-w5fx](https://github.com/pypa/wheel/security/advisories/GHSA-8rrh-rw8j-w5fx).
  These tools are development/build dependencies; the library has no runtime
  dependencies. Updated download hashes are committed with the version pins.

- Preserved the first successful fresh-host Linux proof build and cross-platform
  Python artifact checks, bound to the exact initial commit.
- Used a supported `.txt` requirements filename so Dependabot can discover all
  locked development packages, not just the build-system requirements.

### Added

- An actual finite-mixture Bernoulli–Poisson probability construction in Lean,
  including all positive factorial moments, the second-cumulant interpretation,
  a conditional rate-range variance bound and the resulting pairwise stability.
  This does not validate calibration or extend fixed-rate sampling guarantees.
- A separate Python-FLINT reproduction of finite-mixture generating series,
  factorial moments, second cumulants and range bounds, including deliberate
  wrong-formula controls. Exact finite agreement supplements the universal proof.
- A hash-pinned Atheris coverage-guided runner, required in CI, with bounded
  inputs, time and memory, a deliberate-fault detection control, genuine-API
  replay and source-bound execution receipts.
- Removal of the remaining administrator PR-rule bypass, preserving the locally
  signed single-commit PR and exact-commit fast-forward procedure.
- A primary-source comparison with existing generalized-factorial-cumulant
  inverse counting statistics; originality remains unresolved.
- Bounded, seeded differential fuzz checks against a separate exact
  integer-partition cumulant oracle, with a saved corpus and fault-detection
  controls. CI and installed-artifact checks exercise the runner; this is finite
  software testing, not formal verification or coverage-guided fuzzing.
- Required CI and dependency review for the exact signed commit promoted to
  main, including administrator pushes.
- An explicit assessment of remaining Scorecard and scientific obligations.

- A red-team follow-up covering the verifier defects, evidence indexing, Sage
  execution and parameter-specific confidence-width diagnostics. Historical
  receipts remain unchanged and are explicitly scoped to their original checks.
- A dated index of the completed 21-module hosted milestone and a fresh read-only
  repository-settings snapshot, separating API evidence from maintainer
  confirmations about account 2FA and Copilot Autofix.
- A digest-pinned hosted Sage projection job and an exact rational diagnostic
  for the sample sizes of a specified population-centered moment-box example.
- All-order analytic/formal cumulant equivalence, including actual expectation
  derivatives and source/background identification stated in those terms.
- Actual Poisson and Bernoulli-plus-Poisson factorial moments, quadratic-statistic
  square integrability, exact variances, and projected-region coverage from
  the probability laws and pairwise-independent observed windows.
- Exact D=1 confidence projection in Lean, including clipping, zero ceiling,
  square-root guards and empty sets. A fresh local Sage execution checks the
  unchanged prototype on boundary, membership and witness cases; the program
  itself is not formally verified.
- A further primary-source comparison with the aggregate-recovery assumptions
  in *Count Bridges*. Historical priority remains unresolved.
- Actual Poisson exponential moments and the independent bounded-source
  generating identity, including a concrete product probability space and zero
  rate, used by the subsequent analytic and moment connections.
- Unified zero/positive-ceiling confidence bounds and preservation of pairwise
  independence under measurable transforms, including the factorial statistic.
  The generic theorem keeps square integrability explicit; the subsequent
  Bernoulli-plus-Poisson specialization derives it from the actual laws.
- A scoped historical record of Lean4Lean and nanoda checks for 26 probability,
  sampling and uncertainty roots, including their diagnostics and rejection control.
- Actual finite probability measures and expectation identities, conditional
  Chebyshev coverage, finite-sample mean variance bounds, and a D=1
  background-uncertainty inequality in separate Lean extensions. A research
  verification suite recompiles their project dependencies from source.
- A separately verified D=1 Bernoulli-law connection, including endpoint laws,
  the core formal cumulant definitions and the formal observed stability bound.
  Its portable verifier freshly checks all imported project modules.
- A focused mathematical review request and an expanded, qualified prior-art
  review. Neither document claims that outside review or originality is established.
- A separately verified D=1 algebraic stability extension, with five checked
  theorem roots, a portable compilation check and scoped additional-kernel
  evidence. General-dimensional stability and constructive finite-sample
  inference beyond D=1 remain open.
- Written bounded-count identification proof and explicit assumption boundaries.
- Six Lean source modules covering identification, exponential-factor invariance
  and universal order sharpness.
- An exact rational Python library, examples and installed-package tests.
- A portable optional Sage confidence-projection example for support `{0, 1}`.
- Research provenance, prior-art attribution and a prioritized proof roadmap.
- Reproduction and repository-integrity checks.

### Fixed

- Separate generated import-only axiom queries from proof compilation output,
  so a proof file's messages cannot supply its axiom audit. Require exact unique
  root coverage and an allowed-axiom subset across core and extension checks;
  retain diagnostics and source, object and query bindings.
- Add stored-proof replay as a complementary check through the pinned Lean
  kernel. This does not constitute an independent kernel or replace axiom
  auditing, statement review or upstream-dependency trust.
- Capture verifier inputs before environment resolution and recheck their
  manifests afterward and before success. This rejects source, manifest or
  configuration changes during a slow toolchain lookup.
