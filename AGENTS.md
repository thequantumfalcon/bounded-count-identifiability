# Project instructions

This is a research artifact about bounded count laws. Preserve the distinction
between mathematical truth under assumptions, software checks, originality and
physical validation. Read [the claim map](docs/claims.md) before changing claims.

The [scope decision](docs/decisions/0001-research-scope.md) records the repository's
publication boundaries and governance choices.

## Build and checks

- `python tools/tasks.py help` lists the shared command catalog.
- Test the installed package, including the wheel and source distribution.
- Build Lean against the committed toolchain and complete dependency lock.
- Never add `sorry`, `admit`, `native_decide` or a new unproved axiom to satisfy CI.
- A changed proof source requires new verification, not just a new file hash.

## Boundaries

- Do not add credentials, machine-specific paths, unpublished source documents,
  raw personal information, tool caches or compiled proof artifacts.
- Use exact rational/algebraic arithmetic where correctness depends on signs.
- Preserve negative findings, prior-art citations and unresolved obligations.
- Synthetic calculations must be labeled and must not imply measurement.
- Do not broaden the public claim when only an example or partial check passes.

## Changes and reviews

Follow [CONTRIBUTING.md](.github/CONTRIBUTING.md). Explain changed assumptions,
tests and mathematical consequences. Keep commits under the maintainer's public
name, Thomas Albrecht; do not add automated co-author credit trailers. The process
disclosure belongs in [PROVENANCE.md](PROVENANCE.md).
