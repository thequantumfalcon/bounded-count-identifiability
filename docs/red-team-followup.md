# Verification tooling: internal cross-checks

This development note records internal checks prompted by a supplied report on
commit `68e644a497428c6580a1daf6506998ead2a6bc57`. It is not an external human
review or endorsement; the report's authorship has not been authenticated.
The checks confirmed two material defects in verification tooling. We corroborated
the principal output-forgery case in an isolated copy: the old core verifier accepted
a proof depending on an added axiom when compilation emitted a forged permitted
axiom message. A separate query exposed the extra axiom. This is a defect in
the audit gate, not evidence that the genuine source contains that axiom.

As a separate check, a generated import query inspected all 124 theorem roots
of the genuine 21-module milestone. Only the permitted standard axioms appeared.
That check reused existing compiled project objects identified by source hashes;
it was not a fresh 21-module compile or an additional proof-kernel implementation.
Successful older CI runs did not cover the demonstrated attack and are not
presented as doing so.

## Disposition of the five findings

| Finding | Assessment and response | Remaining boundary |
| --- | --- | --- |
| BCI-01: forgeable axiom audit | Confirmed. Separate generated import-only axiom queries replace reliance on messages emitted during proof compilation. Exact source, artifact and audit bindings accompany the result. | A separate process is not a hostile-code sandbox. Compiler, dependencies, verifier and host remain trusted. |
| BCI-02: incomplete core audit | Confirmed in substance. Core and extensions use an explicit root registry and shared admission policy. Missing, duplicate or extra roots and unapproved axioms must fail. Valid proofs may use a strict subset of the allowed axioms. | The review's particular single-root deletion example would already fail; a multi-root module supplies the valid missing-root case. Token checks are defense in depth. |
| BCI-03: historical CI evidence | Preserve the original records and add a [dated index and settings readback](../evidence/verification-index-2026-10-21.json) for the completed 21-module milestone. The earlier documentation already labeled the initial run as historical. | No committed index can contain a completed hosted result for its own future commit hash. Inspect the exact commit's Actions runs and artifacts. |
| BCI-04: Sage execution checks | Add a hosted Sage projection job, with a digest-pinned runtime and a result artifact recording the checked source hashes. Existing local exact checks were already present; describing execution as entirely unchecked was too strong. | Neither tests nor the Lean interval theorem formally verify the executable program, its input handling or Sage's arithmetic library. |
| BCI-05: numerical scale | Add a reproducible [population-centered scale diagnostic](claims.md#population-centered-scale-diagnostic), with explicit parameters and exact outward bounds. The reviewed example's large sample counts are corroborated. | These are not universal lower bounds, best-case widths or measured sample requirements. The repository's lack of a general-D solver is not a theorem that none exists. |

The verification changes leave the mathematical proof sources and stated
assumptions unchanged. Refer to [reproduction](reproduction.md) for commands
and to the [verification record](../evidence/README.md) for evidence boundaries.
Workflow configuration describes intended checks; only the completed run and
its verification records establish that those checks passed for a particular
commit.

## What the strengthened checks mean

An axiom audit asks which assumptions the selected declarations use. A separate
stored-proof replay checks their saved proof terms again through the pinned
kernel. These are complementary checks: replay can accept a theorem relative
to an unwanted axiom, so replay does not replace the allowlist. The replay uses
Lean's kernel and is not an independent implementation. Its replay covers safe,
total declarations; the current project sources use neither unsafe nor partial
declarations. Split-module sidecars are rejected until explicitly supported and
bound by the runner. Upstream dependency
objects and their interpretation remain trusted. These distinctions follow
[Lean's validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

The executable policies are in [proof_audit.py](../lean/proof_audit.py) and
[replay.py](../lean/replay.py). The axiom policy requires exactly the requested
roots, once each, with no extra output, and accepts any subset of the three
allowed standard axioms. Compile logs remain useful diagnostics; they cannot
stand in for the separately generated query result.

Admission filters reject disallowed constructs in this project's submitted
proof files. They do not establish that arbitrary Lean metaprograms are safe,
and `opaque` declarations or metaprogramming are not intrinsically unsound.
Review of theorem statements, definitions and assumptions remains necessary.

For the Sage projection, sampled points cannot establish exact emptiness:
for `B=1` and the singleton moment boxes `[1,1]` and `[1/2,1/2]`, the feasible
source parameter is the irrational singleton `p=1/sqrt(2)`, with
`b=1-1/sqrt(2)`. A rational grid can miss that feasible set entirely. The formal
interval theorem supplies the universal statement; exact boundary fixtures,
membership comparisons and original-constraint witness checks test the program.

## Review provenance and open scientific questions

The underlying PDF is not included in the repository. Its SHA-256 is
`68d1259d3e324762b1a1dee9e93e49f890e82f80727ca90d5e21bbf2d0c66520`.
The review's raw scripts and logs were not supplied with it. We reproduced the
specific findings described above within this research campaign; this does
not authenticate the reviewer, establish independent human peer review or
corroborate every reported external run.

Historical priority, outside mathematical review and physical validation remain
open. The formal result is conditional on its probability model. The fixes do
not establish a practical detector protocol, an optimal confidence estimator
or complete verification of every executable. The [roadmap](roadmap.md) retains
those distinctions.
