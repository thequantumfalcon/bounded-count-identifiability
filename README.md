# Bounded count identifiability

For a known integer $D\geq1$, a probability law on $\lbrace0,\ldots,D\rbrace$ is
determined by its factorial cumulants of orders $2,\ldots,D+1$, without supplying
its mean.
Independent Poisson background with an unknown **fixed** rate preserves these
cumulants. The observed mean then determines the background rate.

**Proof sketch.** Write $P(t)=\mathbb E[(1+t)^X]$ and $Q(t)$ for two candidate
laws, and let $c$ be their mean difference. Equal factorial cumulants of orders
$2,\ldots,D+1$ imply $P=e^{ct}Q+O(t^{D+2})$. If $c>0$, the coefficient of
$t^{D+1}$ on the right is at least $c^{D+1}/(D+1)!>0$: all coefficients of $Q$
are nonnegative and $Q(0)=1$. The left coefficient is zero because $\deg P\leq D$.
Swapping the laws excludes $c<0$. Hence $c=0$, and the two polynomials, and
therefore the laws, agree. See the [full proof](docs/theorem.md) and
[Lean identification theorem](lean/CountIdentification.lean).

**Sharpness.** The established generalized matching distribution has factorial
generating polynomial $\sum_{k=0}^D (ht)^k/k!$, $0<h<1$. Its cumulants of orders
$2,\ldots,D$ vanish, just as for the point mass at zero, but its order-$D+1$
cumulant is $-h^{D+1}$. Thus the general cutoff cannot be lowered. The
[construction and prior-art attribution](docs/theorem.md#sharpness-using-an-established-family)
and [Lean sharpness proof](lean/CountSharpness.lean) give the details.

One motivation is separating a bounded source count from independent Poisson
background in an idealized photon-counting model. Related inverse-counting work
by [Stegmann and König](https://arxiv.org/abs/1611.02043) reconstructs features of
stochastic dynamics from generalized factorial cumulants; its assumptions and
target differ from this bounded-law result. See the
[literature comparison](docs/originality-review.md) and
[detector assumptions](docs/calibration.md#photon-counts-and-detector-clicks).

**Scope and disclaimer.** These are exact population results under the stated
support and independence assumptions. They do not validate a detector, identify
an emitted source separately from unknown detection efficiency, or establish
finite-sample performance. Priority remains unresolved, and no external human
peer review is claimed. Errors and omissions may remain; the material is
provided as-is. The [research-process disclosure](PROVENANCE.md) records the
development assistance and verification limitations.

## Review and reproduce

Start with the [one-page mathematical review request](docs/reviewer-request.md).
The [claim map](docs/claims.md) separates the main theorem, extensions, software
checks and unresolved obligations.

- [Theorem and proof](docs/theorem.md), including the role of nonnegativity.
- [Reproduction guide](docs/reproduction.md) and [pinned Lean project](lean/README.md).
- [Probability, sampling and uncertainty extensions](docs/probability-extensions.md).
- [Verification record](evidence/README.md), including hosted runs for specific commits.
- [Internal verification-tooling cross-checks](docs/red-team-followup.md) and
  [remaining research questions](docs/roadmap.md).
- [Synthetic experiment](docs/stress-test.md), [exact confidence decisions](lean/extensions/confidence-executable/README.md),
  [count-to-box certificates](lean/extensions/counts-confidence/README.md) and
  [Isabelle endpoint proofs](isabelle/README.md).

## Run an exact example

With Python 3.11.4 or newer, from the repository root:

```sh
python -m pip install .
python -m bounded_counts --degree 3 --strength 1/2
```

The example compares distinct bounded source laws with different Poisson
backgrounds. Their observed factorial cumulants agree through order $D$ and
separate at order $D+1$. The dependency-free Python library uses exact rational
arithmetic. These finite calculations illustrate the proof.

## Maintenance and reuse

Maintained by [The Quantum Falcon](https://github.com/thequantumfalcon).
Corrections, counterexamples and independent mathematical review are welcome
through [Discussions](https://github.com/thequantumfalcon/bounded-count-identifiability/discussions)
and the issue forms. See [contribution guidance](.github/CONTRIBUTING.md),
[security reporting](.github/SECURITY.md), [CITATION.cff](CITATION.cff) and the
[maintenance policy](docs/decisions/0002-maintenance-controls.md).

The Python API is experimental (`0.1.0.dev0`). Original code and documentation
are provided under the [MIT license](LICENSE.txt); third-party material retains
its stated terms in the [notices](NOTICE.md).
