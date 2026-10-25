# Exact reconstruction and stability of bounded laws

For a law on a known $\lbrace0,\ldots,D\rbrace$, the mean is the largest real
root of a polynomial determined by factorial cumulants $2,\ldots,D+1$.
The probabilities then follow by a finite coefficient inversion.
Across this class the inverse has a uniform Hölder bound with exponent
$1/(D+1)$, and no larger exponent works uniformly.

These are written consequences of the [identification argument](theorem.md).
They are not yet formalized in Lean. The constants below are conservative;
the results compare exact admissible population laws and do not supply
sampling errors, detector calibration or a practical reconstruction algorithm.
No historical-priority claim is made.

## The largest real root

Fix $D\geq1$ and put $n=D+1$. Write

$$
P(t)=\mathbb E[(1+t)^X]=\sum_{j=0}^{D}\frac{m_j}{j!}t^j,
\qquad m_j=\mathbb E[(X)_j],\quad m_0=1,\quad \mu=m_1.
$$

Given the exact factorial cumulants $\kappa_2,\ldots,\kappa_n$, form

$$
F(u)=n![t^n]\exp\left(ut+\sum_{r=2}^{n}\frac{\kappa_r}{r!}t^r\right).
$$

This is a monic polynomial of degree $n$ in $u$. For every real $h$, the
formal series identity through degree $n$ gives

$$
F(\mu+h)=n![t^n]e^{ht}P(t)
=\sum_{j=0}^{D}\binom{n}{j}m_j h^{n-j}.
$$

Every $m_j$ is nonnegative. Thus $F(\mu)=0$, whereas $F(\mu+h)>0$ for
$h>0$ because its $j=0$ term is $h^n$. Therefore **$\mu$ is the largest
real root of $F$**. Other roots need not be real or yield probability laws.

If the actual support maximum is $d=\max\lbrace j:p_j>0\rbrace$, the smallest
nonzero power above is $h^{n-d}$. The mean root therefore has multiplicity
exactly $n-d$. Padding the known support bound with zeros can create a
multiple root without destroying uniqueness of the admissible law.

Recover the moments and probabilities by

$$
m_k=k![t^k]\exp\left(\mu t+\sum_{r=2}^{n}\frac{\kappa_r}{r!}t^r\right),
\qquad 0\leq k\leq D,
$$

$$
p_j=\frac1{j!}\sum_{k=j}^{D}\frac{(-1)^{k-j}m_k}{(k-j)!},
\qquad 0\leq j\leq D.
$$

The second formula extracts coefficients after substituting $t=z-1$. It is
the finite-support case of [Afendras and Papadatos, Lemma 2.1, equation (2.5),
PDF page 5](https://arxiv.org/pdf/1411.1165).
For independent fixed Poisson background, the identifying cumulants are
unchanged and the observed mean then gives $b=\mathbb EY-\mu$.

Bernoulli$(1/2)$ with supplied bound $D=2$ gives

$$
F(u)=u^3-\tfrac34u+\tfrac14=(u-\tfrac12)^2(u+1).
$$

The point mass at $2$, with supplied bound $D=3$, gives

$$
F(u)=u^4-12u^2+16u=u(u-2)^2(u+4).
$$

Both mean roots have multiplicity two.

## Exact admissibility

For a proposed real vector $(\kappa_2,\ldots,\kappa_n)$, the formulas give
an exact mathematical criterion:

1. If $F$ has no real root, the vector is inadmissible.
2. Otherwise take its largest real root $\rho$ and reconstruct the masses.
3. The vector is admissible precisely when every reconstructed mass is
   nonnegative.

Necessity follows from the largest-root argument. For sufficiency, the
reconstructed polynomial has constant coefficient $1$, so its masses sum to
$1$. Its coefficients through degree $D$ agree with the prescribed exponential
by construction. Their degree-$n$ coefficients also agree, since $F(\rho)=0$.
Taking formal logarithms recovers the supplied cumulants through degree $n$,
with mean $\rho$.

An arbitrary noisy vector need not be admissible: for $D=1$, positive
proposed $\kappa_2$ gives $F(u)=u^2+\kappa_2$ with no real root. Even a real
root does not establish nonnegative reconstructed masses. Certified root
isolation and sign decisions for rational or algebraic inputs remain
computational obligations; approximate roots are not exact certificates.

## A uniform inverse bound

Let $P,Q$ represent two probability laws under the same known support bound.
Define

$$
\varepsilon=\max_{2\leq r\leq n}|\kappa_r(P)-\kappa_r(Q)|,
\qquad S_n(v)=\sum_{r=2}^{n}\frac{v^r}{r!},
$$

$$
H_D(\varepsilon)=
\left[n!2^D e^D\left(e^{\varepsilon S_n(1)}-1\right)\right]^{1/n},
\qquad c_* = \min\lbrace D,H_D(\varepsilon)\rbrace.
$$

Then

$$
|\mu_P-\mu_Q|\leq c_*,
$$

$$
\operatorname{TV}(P,Q)
\leq\min\left\lbrace1,\frac{3^D}{2}
\left(e^{2c_*+\varepsilon S_n(2)}-1\right)\right\rbrace.
$$

Here total variation is half the sum of absolute probability differences.
The bounds can be numerically vacuous at moderate errors or large $D$.

**Proof.** Swap the laws if necessary so that $c=\mu_P-\mu_Q\geq0$.
Let $R(t)=\sum_{r=2}^n(\kappa_r(P)-\kappa_r(Q))t^r/r!$,
$B(t)=\varepsilon S_n(t)$ and $A(t)=e^{ct}Q(t)$. Through degree $n$,
$P=Ae^R$. Coefficientwise absolute values satisfy $|e^R-1|\leq e^B-1$.
All coefficients of $A$ are nonnegative, so the vanishing degree-$n$
coefficient of $P$ implies

$$
\frac{c^n}{n!}\leq[t^n]A
\leq[t^n]A(e^B-1)
\leq e^cQ(1)(e^{\varepsilon S_n(1)}-1)
\leq e^D2^D(e^{\varepsilon S_n(1)}-1).
$$

This proves the mean bound. If $a_j=[t^j]\big(P-Q\big)$, substituting $t=z-1$
shows $\sum_k|p_k-q_k|\leq\sum_{j=0}^D2^j|a_j|$. The finite-jet
identity $P-Q=Q(e^{ct+R}-1)$ bounds this by the nonnegative majorant
evaluated at $t=2$:

$$
\sum_{j=0}^D2^j|a_j|
\leq Q(2)(e^{2c+\varepsilon S_n(2)}-1)
\leq3^D(e^{2c+\varepsilon S_n(2)}-1).
$$

Only the convergent majorant series are evaluated at $1$ and $2$; no value
of $\log P$ or $\log Q$ there is assumed. This proves the stated bounds.

## The exponent is sharp

For each fixed $D$, these bounds imply constants depending only on $D$ with

$$
|\mu_P-\mu_Q|\leq C_D\varepsilon^{1/n},
\qquad \operatorname{TV}(P,Q)\leq C'_D\varepsilon^{1/n}.
$$

For $0\leq\varepsilon\leq1$, convexity gives
$e^{\varepsilon a}-1\leq\varepsilon(e^a-1)$ for $a=S_n(1)$.
Thus $c_*=O_D(\varepsilon^{1/n})$; using
$e^x-1\leq e^{2D+S_n(2)}x$ for $0\leq x\leq2D+S_n(2)$ proves
the total-variation bound with the same exponent. For $\varepsilon\geq1$,
use $|\mu_P-\mu_Q|\leq D$ and $\operatorname{TV}\leq1$.

Compare the established [generalized matching family](theorem.md#sharpness-using-an-established-family)
$P_{D,h}(t)=\sum_{k=0}^D(ht)^k/k!$, $0<h<1$, with the point mass at zero.
Its cumulant discrepancy is $\varepsilon=h^n$, mean discrepancy is $h$,
and total variation is

$$
1-\sum_{k=0}^D\frac{(-h)^k}{k!}=h+O(h^2).
$$

For any $\beta>1/n$, a uniform bound by $C\varepsilon^\beta$ would require
$1\leq C h^{n\beta-1}$ in the mean case, or a left side tending to $1$
in the total-variation case, as $h\downarrow0$. This is impossible.
The exponent is sharp; the constants are not claimed sharp. The distribution
and its moment matching are attributed in the linked note.

## Local sensitivity and estimated inputs

At a law with $p_D>0$ the mean root is simple, since $F'(\mu)=n!p_D$.
The implicit-function theorem gives a locally analytic inverse branch on
nearby admissible inputs, with

$$
d\mu=-\frac{\sum_{r=2}^{n}\binom nr m_{n-r}\,d\kappa_r}{n!p_D}.
$$

In particular, sensitivity to $\kappa_n$ grows as $1/(n!p_D)$ when the
mass at the supplied support ceiling vanishes. A multiple root alone does
not determine the best local exponent in every admissible direction.

The uniform bounds compare two admissible laws. If an estimated cumulant
vector is within $\delta$ of the truth in maximum norm, and an admissible fit
has residual at most $\delta$, their admissible vectors differ by at most
$2\delta$. Apply the bounds with $\varepsilon=2\delta$. A global
minimum-residual fit exists by compactness of the probability simplex, but
this supplies neither an efficient fitting algorithm nor a probability
that the assumed estimation error holds.

## Reproduce the finite algebra checks

After installing the package, run

```sh
python examples/largest_root_identity.py
```

The example uses exact rational arithmetic to check the shifted-polynomial
identity, multiplicity and probability inversion on a finite grid of laws
and on the attributed sharpness family. It checks the two displayed
polynomials and rejects a deliberately changed constant coefficient.
It starts from known laws to check the identity; it is not a general
root-isolation or noisy-data solver. These finite software checks supplement
the written proofs and do not formalize them.
