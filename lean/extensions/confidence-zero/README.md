# Nonnegative confidence ceilings and measurable transforms

[CountConfidenceZeroAndTransforms.lean](CountConfidenceZeroAndTransforms.lean)
extends the [finite sample-mean results](../sample-mean/README.md) to nonnegative
variance ceilings, including both-zero and mixed zero/positive cases. Its
[source manifest](source_manifest.json) lists six theorem roots.

The bad events use strict inequalities
`sqrt(2W/(Nα)) < |sampleMean - m|`, so the corresponding good intervals include
their endpoints. A zero ceiling gives almost-sure equality through the existing
zero-variance theorem; positive ceilings use Chebyshev. The probability of either
bad event is at most `α`. The earlier positive-ceiling theorem is unchanged.

The estimators are actual finite sample means with positive natural sample size.
Their premises require square-integrable per-window statistics, pairwise
independence within each family, common expectations, nonnegative individual
variance ceilings, and positive `α`. Independence between the two estimators is
not required.

The module also proves that coordinate-specific measurable transforms preserve
pairwise independence and specializes this to `Y ↦ Y*(Y-1)`. Its factorial
sample-mean theorem assumes square integrability of both `Y` and `Y*(Y-1)`
explicitly. Square integrability of `Y` alone does not establish that of the
quadratic statistic. Distribution-specific moment formulas, the projection
formula and implementation certification remain separate obligations.

Run the research suite from the repository root with an unused run name:

```sh
python lean/extensions/d1-law/verify_law_bridge.py --suite research --run external-confidence
```

The suite checks explicit roots and standard axioms with `--trust=0`, using the
pinned dependency cache. See the [extension guide](../../../docs/probability-extensions.md)
for the surrounding assumptions and reproduction limits. These standard
independence and variance arguments carry no novelty claim.
