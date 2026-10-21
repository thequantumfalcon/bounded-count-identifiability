# D=1 algebraic inverse stability

This extension proves deterministic error bounds for the algebraic formulas
`secondCumulant p = -p^2` and `backgroundFromMean mu p = mu-p`.
It is separate from the six core modules and their historical receipts.

For nonnegative real parameters $p,q$,

$$
|p-q|^2\leq|p^2-q^2|,
\qquad |p-q|\leq\sqrt{|\kappa_2(p)-\kappa_2(q)|}.
$$

Consequently, if
$|\kappa_2(p)-\kappa_2(q)|\leq\varepsilon$ and
$|\mu-\nu|\leq\delta$, then

$$
|p-q|\leq\sqrt{\varepsilon},
\qquad |(\mu-p)-(\nu-q)|\leq\delta+\sqrt{\varepsilon}.
$$

The error premises imply $\varepsilon,\delta\geq0$. The formal theorem requires
only $p,q\geq0$, not that they lie in $[0,1]$ or that either background is
nonnegative. Those additional restrictions are needed for the Bernoulli-plus-
Poisson interpretation. The file defines the second cumulant formula
algebraically; it does not connect that definition to the core formal logarithm
or construct random variables.

The five checked roots in [CountD1Stability.lean](CountD1Stability.lean) are:

```text
CountD1Stability.squared_parameter_error_le
CountD1Stability.parameter_error_le_sqrt
CountD1Stability.parameter_error_from_cumulant
CountD1Stability.background_error_le
CountD1Stability.bounded_observation_error
```

These elementary inequalities carry no originality or optimality claim. They
do not establish a statistical confidence level, accuracy of an observed
cumulant, admissibility of an arbitrary estimate, stability for general $D$,
or a detector model. See the [claim map](../../../docs/claims.md).

## Reproduce

First follow the pinned dependency setup and core build in
[the formal guide](../../README.md). Then, from the repository root:

```sh
python lean/extensions/d1/verify_stability.py --run external-check
```

The verifier uses `lake env` from the core Lean project and compiles this source
freshly with `--trust=0`. It checks the source binding, successful compilation,
nonempty compiled output and unchanged inputs; a separately generated import
query audits exactly the five theorem roots, so compilation messages cannot
supply the axiom evidence. Each list may contain any subset of the standard
`propext`, `Classical.choice` and `Quot.sound` axioms, including no axioms.
Results and logs are saved under
`build/stability/external-check/`; choose a new run name for every check.

The public CI formal job invokes this verifier after the six-module core check.
Workflow configuration is not a passing run: inspect the exact commit's checks.
The shared local command `python tools/tasks.py formal` also invokes it.

The [additional kernel record](../../../evidence/d1-stability-kernel-checks.json)
summarizes prior local checks of these exact proof bytes using six existing
checker executables. All accepted the dependency-closed export. They share
parts of the toolchain, design or implementation lineage and do not represent
six independent mathematical reviews. Nanoda reported zero type-checking
errors and one axiom pretty-printing error, retained in the record. Those extra
checkers are not installed or rerun by this extension's public CI step.

Large exports, private development paths and checker installations are excluded
from the repository. The summary alone cannot reproduce the extra checker runs;
the portable source and verifier support a fresh Lean compilation.
