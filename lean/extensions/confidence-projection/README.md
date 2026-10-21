# Exact D=1 interval projection

[CountConfidenceProjection.lean](CountConfidenceProjection.lean) proves the
exact real projection of the constraints

```text
0 <= p <= 1,  0 <= b <= B,
a <= p+b <= c,  d <= (p+b)^2-p^2 <= e.
```

For `B>0`, `a>=0`, `d>=0`, and ordered intervals, membership is exactly
`d<=c^2` and `L<=p<=U`, where

```text
L = max(0, a-B, sqrt(max(0,a^2-e)), (d-B^2)/(2B))
U = min(1, c, sqrt(c^2-d)).
```

The guard `d<=c^2` is explicit. Reversed input intervals and a failed guard
give the empty set; a reversed final interval `L>U` is also empty. The proof
uses the exact change of variable `m=p+b` and constructs the feasible mean
`max(a,p,sqrt(d+p^2))` in the reverse direction.

Clipping raw first-moment bounds to `[0,1+B]` and second-factorial-moment
bounds to `[0,B^2+2B]` preserves the feasible set, including empty
intersections. For `B=0`, with clipped lower bounds and `c<=1`, the result is
`[a,c]` exactly when both intervals are nonempty and `d=0`; otherwise it is
empty. Negative `B` is algebraically infeasible. The positive-background
theorem is stronger than the clipped-box version because it does not require
the two upper clipping bounds as additional assumptions.

These results justify deterministic elimination once the two algebraic moment
constraints apply. They do not prove the sampling coverage premise or the
Python/Sage implementation. The [Sage example](../../../examples/d1_projection_sage.py)
also has an API policy: it raises `ValueError` for negative background ceilings
or reversed raw input boxes, whereas the Lean predicate characterizes their
constraints as infeasible. Exact endpoint mathematics does not by itself
certify input parsing, arithmetic execution, or the witness helper.

The source manifest lists 16 checked roots, including clipping, membership,
nonemptiness, and all boundary cases above. Reproduce them with the research
suite in the [formal verification guide](../../README.md). Pinned imports are
reused; checked roots use only `propext`, `Classical.choice`, and `Quot.sound`.
No outside human review, empirical validation, or originality claim is made.
