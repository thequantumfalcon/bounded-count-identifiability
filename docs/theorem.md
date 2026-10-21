# Bounded counts from higher factorial cumulants

A probability law supported on the known set $\{0,\ldots,D\}$ is uniquely determined by its factorial cumulants of orders $2,\ldots,D+1$. The source mean need not be supplied. This gives identification under independent, unknown, fixed-rate Poisson background. The maximum order $D+1$ is sharp for the general class.

These are exact population statements. The known sharpness distribution is attributed below. Priority for the general sufficient-order theorem remains unresolved; this project does not claim an original discovery.

## Definitions and assumptions

Let $D\geq1$ be an integer and let $X$ be a nonnegative integer random variable with $\Pr(X\leq D)=1$. Its factorial generating polynomial is

$$
P(t)=\mathbb E[(1+t)^X]=\sum_{j=0}^{D}p_j(1+t)^j.
$$

Here $p_j\geq0$ and $\sum_jp_j=1$. Thus $P(0)=1$, $\deg P\leq D$, and

$$
[t^r]P(t)=\mathbb E\binom{X}{r}\geq0.
$$

Define the factorial cumulants by

$$
\kappa_r(X)=r![t^r]\log P(t),\qquad r\geq1.
$$

The logarithm may be interpreted as a formal power series at $P(0)=1$. Analytically, the same coefficients are the derivatives of the real logarithm near $t=0$. In particular, $\kappa_1=\mathbb E X$ and $\kappa_2=\operatorname{Var}(X)-\mathbb E X$. Ordinary cumulants are different quantities.

## Identification theorem and proof

**Theorem.** If $X$ and $X'$ both satisfy the support bound and

$$
\kappa_r(X)=\kappa_r(X')\quad(2\leq r\leq D+1),
$$

then they have the same probability law.

**Proof.** Let $P,Q$ be their factorial generating polynomials, and put $c=\mathbb EX-\mathbb EX'$. Equality of the stated cumulants gives

$$
\log P(t)-\log Q(t)=ct+O(t^{D+2}),
\qquad
P(t)=e^{ct}Q(t)+O(t^{D+2}).
$$

Here $O(t^m)$ means that all coefficients below degree $m$ vanish. If $c>0$, nonnegativity of the coefficients of $Q$ and $Q(0)=1$ imply

$$
[t^{D+1}]\big(e^{ct}Q(t)\big)
=\sum_{j=0}^{D}[t^j]Q(t)\frac{c^{D+1-j}}{(D+1-j)!}
\geq\frac{c^{D+1}}{(D+1)!}>0.
$$

This contradicts $[t^{D+1}]P=0$. Interchanging $P,Q$ excludes $c<0$. Hence $c=0$ and $P-Q=O(t^{D+2})$. Since both have degree at most $D$, they are equal. Substituting $t=z-1$ recovers the ordinary probability generating polynomials, so every probability agrees. $\square$

For $D=0$ the only admissible law is the point mass at zero; identification is trivial.

## Unknown Poisson background

Suppose $Y=X+Z$, where $Z\sim\operatorname{Poisson}(b)$, $b\geq0$ is fixed, and $X,Z$ are independent. Then

$$
\mathbb E[(1+t)^Y]=P(t)e^{bt},
\qquad
\kappa_r(Y)=\kappa_r(X)\quad(r\geq2).
$$

Therefore observed factorial cumulants $2,\ldots,D+1$ identify the bounded source law. If the observed mean is also known, it identifies $b=\mathbb EY-\mathbb EX$. This higher-cumulant invariance is established Poisson-translation theory; see [Jørgensen and Kokonendji, equations (2.9)–(2.10)](https://arxiv.org/pdf/1409.7482).

The support bound applies to $X$, not $Y$. The total observed count has unbounded support when $b>0$. No assumption about independence between different observation windows is needed for this population identity. Sampling guarantees require additional assumptions. Random background rates, source–background dependence and nonlinear detector responses are not covered by this corollary.

## Sharpness using an established family

For $0<h<1$, set

$$
P_{D,h}(t)=\sum_{k=0}^{D}\frac{(ht)^k}{k!}.
$$

This is the factorial generating polynomial of the **generalized matching distribution**. Its probabilities and matched factorial moments appear in [Afendras and Papadatos, equation (3.1) and Lemma 3.1, PDF page 7](https://arxiv.org/pdf/1411.1165), which credits [Niermann (1999)](https://link.springer.com/article/10.1007/BF02925521). The family and its moment matching are established results; they are not new constructions of this project.

Indeed the ordinary probabilities are

$$
p_j=\frac{h^j}{j!}\sum_{i=0}^{D-j}\frac{(-h)^i}{i!},\quad 0\leq j\leq D,
\qquad p_j=0\quad(j>D).
$$

Each alternating partial sum is positive: pair successive even and odd terms, whose absolute values decrease for $0<h<1$, and retain a positive last term when necessary. Normalization follows from $P_{D,h}(0)=1$ after the substitution $t=z-1$.

Expanding the formal logarithm gives

$$
\kappa_1=h,\qquad \kappa_2=\cdots=\kappa_D=0,
\qquad \kappa_{D+1}=-h^{D+1}.
$$

The point mass at zero has the same cumulants $2,\ldots,D$, but is a different law. Moreover, $P_{D,h}$ with background zero and the zero source with background rate $h$ have equal observed cumulants $1,\ldots,D$. Both background rates are nonnegative. Thus lowering the general cutoff from $D+1$ to $D$ fails, even if the observed mean is included. This is a direct consequence of the known family.

The claim concerns the full class of laws supported on $0,\ldots,D$. It does not say every pair needs order $D+1$, nor establish the same sharpness for subclasses that exclude the zero source.

## What the formal proof covers

The six core Lean modules encode the following chain:

| Module | Encoded statement |
| --- | --- |
| [CountLawEncoding.lean](../lean/CountLawEncoding.lean) | Actual count probabilities, factorial polynomial coefficients and recovery of the law. |
| [CountSeriesCore.lean](../lean/CountSeriesCore.lean) | Formal-log cumulants, the finite exponential-shift relation and positivity argument. |
| [CountIdentification.lean](../lean/CountIdentification.lean) | Equality of arbitrary admissible bounded laws from orders $2,\ldots,D+1$. |
| [CountPoissonChannel.lean](../lean/CountPoissonChannel.lean) | Multiplication by the formal exponential factor and cancellation above first order. |
| [CountObservedIdentification.lean](../lean/CountObservedIdentification.lean) | Observed-cumulant source identification and recovery of the background parameter. |
| [CountSharpness.lean](../lean/CountSharpness.lean) | Validity, distinctness, cumulants and the universal lower-order counterexample. |

The core definitions use mathlib's formal logarithm. The [probability extensions](probability-extensions.md#independent-poisson-observations) construct independent Poisson addition and prove its integrable generating identity. The [analytic connection](probability-extensions.md#analytic-cumulants) proves equality with real logarithm derivatives at every order, including derivatives of the actual generating expectation. It also states source and source/background identification directly in those analytic terms. The algebraic channel accepts real parameters; the probability construction uses nonnegative background rates.

A [separate D=1 extension](../lean/extensions/d1/README.md) proves deterministic
inverse-error bounds for the algebraic formulas $\kappa_2(p)=-p^2$ and
$b=\mu-p$. It does not change the six core modules. The probability and analytic
connections are supplied by other extensions; general-$D$ stability remains separate.

The additional [finite-law connection](../lean/extensions/d1-law/README.md)
proves validity of Bernoulli masses on the closed interval $p\in[0,1]$ and
identifies their core formal cumulants as $\kappa_1=p$, $\kappa_2=-p^2$.
It lifts the deterministic stability bounds to these definitions and to the
formal observed channel. The subsequent probability and analytic extensions
connect these definitions to the actual independent-Poisson observation model.

Formal acceptance does not verify a detector, prove a useful finite sample size or establish mathematical priority. The calculation software and confidence-region argument have their own scope; see [claims](claims.md), the [formal reproduction guide](../lean/README.md) and the [next proof obligations](roadmap.md).
