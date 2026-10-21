# Exact rational confidence decisions

`CountConfidenceExecutable.lean` proves correctness of three computable rational
decision functions for the fixed-rate `D=1` moment-box model. The eight roots in
`source_manifest.json` are included in the research suite's separate axiom audit
and stored-proof replay. The prior real projection theorem supplies the model.

All inputs are rational. The constraints are

```math
0\le p\le1,\quad 0\le b\le B,\quad
a\le p+b\le c,\quad d\le(p+b)^2-p^2\le e.
```

| Function | Meaning of `true` | Meaning of `false` |
| --- | --- | --- |
| `checkPair B a c d e p b` | The supplied rational pair satisfies the original real constraints. | That pair violates the constraints. |
| `checkSource B a c d e p` | Some real background makes the supplied rational source probability feasible. | No real background can make that source probability feasible. |
| `checkNonempty B a c d e` | Some real source probability and real background satisfy the box. | The entire real feasible region is empty. |

The last test does not search a rational grid. It eliminates the square roots
in the interval-endpoint comparison using rational squared inequalities. For
`B=1, a=c=1, d=e=1/2`, the projected set is the singleton `p=sqrt(1/2)`.
`checkNonempty` accepts it even though it contains no rational probability.
Negative ceilings, reversed boxes, clipping, boundary equality and `B=0` are
included in the equivalences. The decision functions return `false` for
infeasible constraints; Sage's input-error interface is a separate convention.

## Check a concrete answer

After retrieving the pinned dependencies, from the repository root:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run exact-query
python lean/check_certificates.py --proof-run exact-query --run exact-query
```

The second command checks 19 boundary queries and three deliberately incorrect
answers against the freshly bound proof objects. Each accepted query has a
separate axiom audit. An incorrect answer must leave exactly the normalized
goal `False`; a missing import, different unsolved goal or timeout does not count
as rejection evidence. This failure diagnostic is not itself a negation proof:
each opposite, correct answer is separately checked as a successful theorem.
Receipts, source statements and logs are saved under `build/certificates/exact-query`.
Use a fresh run name for every execution. Existing evidence is never replaced.

To certify the irrational-singleton region's nonemptiness:

```sh
python lean/check_certificates.py --proof-run exact-query --run singleton --kind nonempty --expect accept --values=1,1,1,1/2,1/2
```

To check a proposed point, use `--kind source` and append `p`; for a supplied
pair use `--kind pair` and append `p,b`. `--expect reject` asks for a proof of
the corresponding negation. Values are comma-separated integers or fractions,
with at most 64 decimal digits per numerator and denominator. Use `--values=...`
so negative fractions are passed as values. Decimals and expressions are rejected.
The runner also supports the research verifier's explicit `existing-cache` mode.

The standalone [emitter](../../../examples/d1_certificates.py) can write a fresh
`.lean` request without invoking Lean:

```sh
python examples/d1_certificates.py --kind source --expect reject --values=1,0,1,0,1,-1/2 --output Query.lean
```

Emitting text does not certify an answer. The generated theorem spells out its
exact rational inputs and real-valued proposition. Proof-producing rational
normalization and the proved equivalence produce a kernel-checked certificate.
No native-evaluation axiom is used. Inspect the generated statement when
checking that it represents an intended query.

## Scope

The rational decision functions and their mathematical specifications are
formally connected. Concrete requests are checked by Lean; the Python emitter
does not supply a trusted numerical answer. The frontend, parser, compiler,
operating system and imported upstream objects remain trusted execution inputs.
This does not formally verify the full Sage algebraic-number program, construct
all algebraic interval endpoints, certify arbitrary irrational input boxes,
or justify a statistical confidence level from raw data. Sampling assumptions
and physical calibration remain separate. No novelty claim is made for this
decision procedure or the elementary elimination argument.
