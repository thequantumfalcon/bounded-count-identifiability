# Bounded counts from higher factorial cumulants

Thomas Albrecht

A probability law supported on the known set $\lbrace0,\ldots,D\rbrace$ is uniquely determined by its factorial cumulants of orders $2,\ldots,D+1$. The source mean need not be supplied. This gives identification under independent, unknown, fixed-rate Poisson background. The maximum order $D+1$ is sharp for the general class.

These are exact population statements. The known sharpness distribution is attributed below. Priority for the general sufficient-order theorem remains unresolved; this project does not claim an original discovery.

This note gives the proof, the known-family sharpness example and a conditional
emitter-counting application. The application also illustrates why identifying
a population law and estimating it from a finite sample are separate questions.

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

Nonnegativity is essential to the coefficient argument. If signed masses were
allowed, $P(t)=1+t$ and $Q(t)=1-t$ would be distinct degree-one polynomials with
the same $\kappa_2=-1$. The latter corresponds to masses $(2,-1)$ on $\lbrace0,1\rbrace$,
so it is excluded by the probability-law assumptions.

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

Since $P_{D,h}(t)=e^{ht}-(ht)^{D+1}/(D+1)!+O(t^{D+2})$, its formal logarithm is
$ht-(ht)^{D+1}/(D+1)!+O(t^{D+2})$. Thus

$$
\kappa_1=h,\qquad \kappa_2=\cdots=\kappa_D=0,
\qquad \kappa_{D+1}=-h^{D+1}.
$$

The point mass at zero has the same cumulants $2,\ldots,D$, but is a different law. Moreover, $P_{D,h}$ with background zero and the zero source with background rate $h$ have equal observed cumulants $1,\ldots,D$. Both background rates are nonnegative. Thus lowering the general cutoff from $D+1$ to $D$ fails, even if the observed mean is included. This is a direct consequence of the known family.

The claim concerns the full class of laws supported on $0,\ldots,D$. It does not say every pair needs order $D+1$, nor establish the same sharpness for subclasses that exclude the zero source.

## Conditional emitter-counting application

Let $n\geq1$ be an integer. Suppose $n$ identical emitters each independently
contribute one detected count with probability $p\in(0,1]$ in an observation
window. With independent fixed Poisson background of mean $b\geq0$, the
observed count has law

$$
Y\sim\operatorname{Binomial}(n,p)+\operatorname{Poisson}(b),
\qquad \log\mathbb E[(1+t)^Y]=n\log(1+pt)+bt.
$$

The general theorem applies when a known bound $D$ includes every candidate
emitter count. This subclass also has the simpler identities

$$
\kappa_2(Y)=-np^2,\qquad \kappa_3(Y)=2np^3.
$$

$$
p=-\frac{\kappa_3(Y)}{2\kappa_2(Y)},\qquad
n=-\frac{4\kappa_2(Y)^3}{\kappa_3(Y)^2}.
$$

The mean then gives $b=\mathbb EY-np$. These formulas follow directly from the
binomial generating function and Poisson cancellation; their use here carries
no originality claim. They require neither the general $D+1$ cutoff nor a
known bound on $n$. If $p=0$, all emitter counts give the same zero source law,
so $n$ cannot be recovered. The general sharpness example compares arbitrary
bounded laws and does not establish sharpness for this binomial subclass.

Emitter counting from photon coincidences is established work, including
[Weston et al. (2002)](https://doi.org/10.1021/ac025730z) and
[counting by photon statistics (CoPS)](https://doi.org/10.1002/smll.201300619).
The [synthetic emitter study](emitter-counting.md) examines specified estimators
and numerical testing bounds under this model. It retains failed estimates and
large errors from the cancellation procedure. Neither exact identification nor
those simulations establish a useful sample size or a validated measurement
method. Unequal brightness, changing backgrounds and detector effects require
separate assumptions; see [calibration](calibration.md#photon-counts-and-detector-clicks).

## Attribution and unresolved priority

The generalized matching family and its matched factorial moments are
established prior work, and the lower-order counterexample above follows
directly from them. Poisson cancellation is also established. For sums of at
most $D$ independent Bernoulli variables, factorial cumulants are signed,
scaled power sums of their success probabilities, as explicitly given by
[Kambly, Flindt and Büttiker (2011), equation (14), unidirectional case](https://arxiv.org/pdf/1012.0750v2).
Consequently, Proposition 24
of [Melánová, Sturmfels and Winter, *Recovery from Power Sums*](https://arxiv.org/pdf/2106.13981v1)
implies identification from orders $2,\ldots,D+1$ for that subclass. This is our
application of their stated result, not an originality claim.

An arbitrary bounded law need not be a sum of independent Bernoulli variables:
masses $1/2$ at each of $0$ and $2$ give $P(t)=1+t+t^2/2$, which has no real
linear factorization. The exact priority question concerns all bounded laws,
with the mean omitted and the finite cutoff $D+1$. The
[literature comparison](originality-review.md) records the inspected sources
and remaining access and review gaps. No original discovery or independent
human literature review is claimed.

## What the formal proof covers

The [Lean identification theorem](../lean/CountIdentification.lean) and
[sharpness proof](../lean/CountSharpness.lean) encode the main statements.
The [formal proof map](../lean/README.md#statements-and-boundaries) describes
the six core modules; the [probability and analytic extensions](probability-extensions.md)
connect the formal series to actual laws and logarithm derivatives. The
emitter formulas above are a written algebraic specialization, with separate
synthetic software checks; they are not separately formalized here.

The [claim map](claims.md), [verification records](../evidence/README.md) and
[process disclosure](../PROVENANCE.md) state the limits of the checks and
development assistance. Formal verification supports the encoded propositions
under their assumptions; physical validity, finite-sample performance and
historical priority require separate evidence.
