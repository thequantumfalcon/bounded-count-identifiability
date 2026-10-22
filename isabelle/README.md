# Isabelle endpoint reconstruction

This small Isabelle/HOL development reconstructs one family of the project's
algebraic confidence-region endpoints. It uses standard `Complex_Main`, with
no AFP dependency or imported Lean proof.

A local Isabelle2025-2 build and exported audit passed for 23 named roots in
`Count_Endpoints` and eight in `Count_Endpoint_Descriptors`. The audit found
the two specified local defining equations, no additional local axioms, no
transitive oracle dependencies and no skipped proofs. These 31 audited roots
are separate from the repository's Lean module and theorem-root counts.
Four deliberately incorrect control builds were rejected for their expected
reasons: a wrong endpoint, an admitted proof, an added axiom and a changed
model definition. Hosted results are reported by the workflow for each commit.

## Mathematical scope

The specification considers real pairs satisfying

$$
0\le p\le1,\qquad 0\le b\le B,\qquad
a\le p+b\le c,\qquad d\le b^2+2pb\le e.
$$

For the mean-one, ceiling-one family, set $B=a=c=1$ and
$d=u,e=v$, with $0\le u\le v\le1$. The endpoint theorem states

$$
\exists b\quad\operatorname{pairbox}(1,1,1,u,v,p,b)
\quad\Longleftrightarrow\quad
\sqrt{1-v}\le p\le\sqrt{1-u}.
$$

The witness is $b=1-p$. Thus the second factorial-moment interval
$[1/4,3/4]$ gives $p\in[1/2,\sqrt3/2]$, and the singleton
$[1/2,1/2]$ admits the real parameter $p=\sqrt{1/2}$.
The latter is an existence statement; this development does not assert an
irrationality or minimal-polynomial irreducibility theorem.

The descriptor theory checks the following exact constants retained from a
Sage calculation. Each polynomial equation together with its bracket selects
one real root.

| Parameter | Polynomial equation | Closed rational bracket | Selected root |
| --- | --- | --- | --- |
| $p$ | $p^2=3/4$ | $[1859775393/2147483648,3719550787/4294967296]$ | $\sqrt3/2$ |
| $b$ | $b^2-2b+1/4=0$ | $[575416509/4294967296,287708255/2147483648]$ | $1-\sqrt3/2$ |

The reconstructed pair satisfies the illustrative constraints. Further
statements cover endpoint inclusion, selected empty and boundary cases,
incorrect endpoints and the necessity of square-root guards. Isabelle's real
square root is signed on negative arguments, so the nonnegative-radicand
hypotheses matter.

These checks do not verify the full arbitrary-mean projection, a Python/Sage
frontend, arbitrary descriptor parsing or serialization, or an executable
algebraic-number library. The moment equations are algebraic assumptions here;
the theories do not construct probability laws, prove sampling coverage,
validate physical measurements or establish originality.

## Reproduction

Use **Isabelle2025-2**. [Toolchain metadata](toolchain.json) pins the complete
Windows and Linux x86-64 distributions by size and SHA-256 from the
[release distribution index](https://isabelle.in.tum.de/website-Isabelle2025-2/dist/index.html).
Verify the archive before extraction and use the selected distribution's
`isabelle` launcher. Standard HOL supplies the required imports; no AFP
download or additional component installation is required.

From the repository root, with that launcher available:

```sh
isabelle version
isabelle build -j 1 -o threads=2 -o timeout=300 -D isabelle
isabelle build_log -v Bounded_Count_Endpoints
isabelle export -n -d isabelle -O build/isabelle-export \
  -x 'Bounded_Count_Endpoints.Endpoint_Audit:endpoint-audit.txt' \
  Bounded_Count_Endpoints
```

The first command must identify `Isabelle2025-2`. The build command selects the
`Bounded_Count_Endpoints` session in `ROOT`; `build_log` displays available
diagnostics and may produce no text. The child session's `ROOT` options include
`record_theories=true`, `quick_and_dirty=false` and `document=false`.
Keep theory recording local to this session: passing that option globally can
rebuild parent sessions. The explicit export command retrieves
`build/isabelle-export/Bounded_Count_Endpoints.Endpoint_Audit/endpoint-audit.txt`;
the expected acceptance line is
`ENDPOINT_AUDIT_PASS roots=31 local_definitions=2 oracles=0`, exactly once.
The local checked build produced that export and acceptance line.
The timeout option limits session work; it is not a total
installation or download deadline. A successful build alone does not replace
the separate source-bound axiom/oracle audit and negative controls. Local Windows evidence and hosted Linux runs are separate records; inspect
the workflow results for the commit being reviewed.

The separate standard-library control harness requires Python 3.11 or later
and a fresh output directory. In a shell where the pinned launcher is on
`PATH`, run:

```sh
python3 isabelle/check_controls.py --isabelle "$(command -v isabelle)" \
  --output build/isabelle-controls
```

It tests a false endpoint, a skipped proof, an extra axiom and a changed
defining equation. Expected failures must have the intended mathematical or
audit diagnostic; missing tools, import failures and timeouts do not count as
successful rejection controls. Preserve the generated receipt and logs.

## Independence and trust

Isabelle/HOL checks a reconstruction through a different proof assistant and
kernel from the Lean development. The source still shares the project's
mathematical specification and development process; see
[research provenance](../PROVENANCE.md). This is additional implementation
diversity, not independent human peer review. Acceptance must exclude skipped
proofs, newly introduced unproved axioms and oracle-dependent results, while
recording the standard HOL assumptions and the exact audited theorem roots.

The [local evidence record](../evidence/isabelle-endpoints-check.json) binds
the checked sources and complete exported report. A [readable statement
excerpt](../evidence/isabelle-endpoint-statements.txt) omits typed constructor
records; it is a display derivative, not a replacement proof certificate.
