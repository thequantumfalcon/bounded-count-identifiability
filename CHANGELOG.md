# Changelog

Notable changes are recorded here using the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) structure.
The Python API is experimental; no stable release has been published.

## [Unreleased]

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

- Written bounded-count identification proof and explicit assumption boundaries.
- Six Lean source modules covering identification, exponential-factor invariance
  and universal order sharpness.
- An exact rational Python library, examples and installed-package tests.
- A portable optional Sage confidence-projection example for support `{0, 1}`.
- Research provenance, prior-art attribution and a prioritized proof roadmap.
- Reproduction and repository-integrity checks.
