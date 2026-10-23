# Finite Bernoulli-law connection to D=1 stability

[CountD1LawBridge.lean](CountD1LawBridge.lean) connects the separate
[algebraic stability proof](../d1/README.md) to the finite-law and formal observed
cumulant definitions used by the six-module core. The existing core and D=1
source manifests remain unchanged. This module has its own exact-byte
[source manifest](source_manifest.json).

The finite mass vector has masses `1-p` and `p` at zero and one. It is a bounded
law for `0 ≤ p ≤ 1`, including both endpoints, and its first two factorial
cumulants are `p` and `-p²`. In the formal exponential-factor channel, the first
two observed cumulants are `p+b` and `-p²`. The stability inequalities therefore
apply to those same formal definitions.

The algebra permits any real background parameter. A Poisson interpretation
requires a nonnegative rate and the additional probability and independence
connection. This module does not construct that probability space, connect the
formal series to analytic logarithms, prove sampling coverage, establish a
physical model, or claim originality for the Bernoulli formulas.

## Reproduce

After retrieving the pinned Lean dependencies as described in the
[formal verification guide](../../README.md), run from the repository root:

```text
python lean/extensions/d1-law/verify_law_bridge.py --run local-check
```

The verifier resolves Lean and dependency paths through `lake env`, excludes
Lake's cached project library, and invokes the core verifier to
compile all six core sources afresh. It checks the new core verification record, theorem
root lists, source bindings and artifact hashes before compiling D=1 stability
and the law bridge in order with `--trust=0`. The extensions import the fresh
core outputs. Existing project or extension artifacts in dependency search
directories are rejected. Lean and mathlib dependency caches are still reused;
this is not a clean rebuild of the entire toolchain.

Portable verification records and logs are written to `build/law-bridge/local-check/` and
`lean/verification/d1-law-local-check/`. Compiled core artifacts are under
`lean/.verification/d1-law-local-check/`. Run names cannot be reused. CI uploads
the verification records and logs, not compiled artifacts.

For an already installed compiler and dependency cache, use `--mode
existing-cache --lean-executable <compiler> --library <dependency-directory>`
and repeat `--library` as needed. Include only dependency libraries, not cached
project proof artifacts. This mode performs no installation or downloads.

## Checked roots

- `CountD1LawBridge.sharpLaw_one_eq_bernoulliMass`
- `CountD1LawBridge.bernoulliMass_isBoundedLaw`
- `CountD1LawBridge.bernoulli_second_cumulant`
- `CountD1LawBridge.bernoulli_parameter_stability`
- `CountD1LawBridge.observed_bernoulli_cumulants`
- `CountD1LawBridge.observed_bernoulli_stability`

The extension requires exactly those six roots in a separately generated import
query; compilation messages cannot supply the axiom evidence. Each root may use
any subset of `propext`, `Classical.choice` and `Quot.sound`, including no axioms.
Input changes,
nonzero exits, timeouts, diagnostics, missing outputs, or changed core artifacts
fail verification. The ordinary Python tests mock compiler execution to test
these acceptance gates; real Lean runs separately in formal CI.
