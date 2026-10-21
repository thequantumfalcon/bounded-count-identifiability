# Request for mathematical and attribution review

We welcome a focused review of the statement below, its formal encoding and its
relationship to prior work. No independent human review or originality is
currently claimed. Publishing this invitation does not mean a reviewer has
accepted it. The [research-process statement](../PROVENANCE.md) explains how the
material was developed.

## Statement to inspect

Let $D\geq1$ be a known integer and let $X,X'$ be arbitrary probability laws
supported on $\{0,\ldots,D\}$. Write

$$
P(t)=\mathbb E(1+t)^X,\qquad
\kappa_r(X)=r![t^r]\log P(t).
$$

The logarithm is formal at $P(0)=1$. The claim is

$$
\bigl(\kappa_r(X)=\kappa_r(X')\text{ for }2\leq r\leq D+1\bigr)
\quad\Longrightarrow\quad X\overset{d}=X'.
$$

The source mean is not supplied. All cumulants are exact population quantities.
The distributions may have zero masses, lower support degree or be point masses.

**Proof outline.** If $Q$ is the polynomial for $X'$ and
$c=\mathbb EX-\mathbb EX'$, the equalities imply
$P=e^{ct}Q+O(t^{D+2})$. If $c>0$, the degree-$D+1$ coefficient on the right is
at least $c^{D+1}/(D+1)!>0$, because $Q(0)=1$ and every coefficient of $Q$
is nonnegative. The left coefficient is zero. Swapping the laws excludes
$c<0$. Thus $c=0$ and the two degree-at-most-$D$ polynomials agree.
Here the $O$ notation means equality of coefficients below the indicated degree.

For $Y=X+Z$ with independent $Z\sim\operatorname{Poisson}(b)$ and fixed
$b\geq0$, the factorial generating function is $e^{bt}P(t)$. Higher factorial
cumulants therefore identify $X$; the observed mean then identifies $b$.
Random rates and source–background dependence are excluded.

The cutoff is sharp for the full class: the established generalized matching
family has $P_{D,h}(t)=\sum_{k=0}^{D}(ht)^k/k!$, $0<h<1$, and
$\kappa_2=\cdots=\kappa_D=0$, while $\kappa_{D+1}=-h^{D+1}$.
It differs from the point mass at zero. This family is credited to
[Afendras–Papadatos, equation (3.1) and Lemma 3.1, citing Niermann](https://arxiv.org/pdf/1411.1165).
[Poisson translation](https://arxiv.org/pdf/1409.7482) and
[nonnegative power-sum recovery](https://arxiv.org/pdf/2106.13981) are also
established; the latter covers the Poisson-binomial subclass. The
[originality review](originality-review.md) distinguishes this overlap from
the arbitrary-law claim.

## Three review questions

1. Does the coefficient argument prove the exact arbitrary-law statement above,
   including boundary cases, without an implicit extra assumption?
2. Do the Lean definitions and theorem statements in the
   [formal proof map](theorem.md#what-the-formal-proof-covers) encode that claim
   faithfully? In particular, are any assumptions stronger than the written
   probability-law assumptions?
3. Is this exact sufficient-order theorem, or a general result implying it,
   already in the literature? A primary citation and a comparison of hypotheses
   would help settle attribution.

## Evidence and review boundary

The repository supplies written proofs, exact-arithmetic examples and pinned
[Lean reproduction commands](../lean/README.md). Selected formal results have
also passed additional proof checkers, with shared dependencies and ancestry.
These are development checks, not outside peer review. The
[probability extensions](probability-extensions.md#independent-poisson-observations)
construct independent Poisson addition and prove its generating identity. The
[analytic connection](probability-extensions.md#analytic-cumulants) proves its
all-order logarithm-derivative interpretation and states identification in
terms of those derivatives.
Physical validation, finite-sample
performance and mathematical priority are separate questions.

Please identify the commit examined and the scope of any feedback: informal
proof, formal statements, reproduced build or literature attribution. A partial
review is useful and will be described as partial. Corrections and
counterexamples are welcome through the repository's
[Discussions](https://github.com/thequantumfalcon/bounded-count-identifiability/discussions)
or [Issues](https://github.com/thequantumfalcon/bounded-count-identifiability/issues).
