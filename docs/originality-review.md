# Internal prior-art comparison and unresolved priority

Literature search updated 23 October 2026. **The priority of the universal identification
theorem remains unresolved.** A targeted search is not proof of novelty, and no
independent human literature review is claimed.

The exact question is whether every probability law on a known
$\lbrace0,\ldots,D\rbrace$ is determined by factorial cumulants
$\kappa_2,\ldots,\kappa_{D+1}$, without supplying $\kappa_1$. The
[theorem and proof](theorem.md) compare arbitrary admissible laws. Results that
assume the mean, a factorization into Bernoulli laws, or knowledge of the entire
generating function have different hypotheses.

## Publication decision

Present the [short note](theorem.md) as a theorem with an elementary proof and
explicit attribution, without claiming a new theorem, a new sharpness family,
or a new emitter-counting method. The current evidence supports these separate
decisions:

| Question | Current answer | Consequence for the note |
| --- | --- | --- |
| Is the sharpness construction original here? | No. Afendras–Papadatos give the exact generalized matching law and factorial moments, crediting Niermann for the law. | Attribute the construction and its matching property. |
| Is cancellation of independent fixed Poisson background original here? | No. It is established factorial-cumulant machinery. | State it as the observation-model corollary, with a citation. |
| Is identification for sums of independent Bernoulli variables already covered? | Yes, as a consequence of Melánová–Sturmfels–Winter, Proposition 24, under the power-sum substitution below. | Acknowledge this subclass overlap; the substitution is our comparison with their statement. |
| Is the universal theorem for arbitrary laws on $0,\ldots,D$ known or new? | Unresolved. No exact earlier statement or complete reduction was located in the inspected sources. | Make no priority claim. Correctness of the supplied proof does not settle this question. |
| Does the emitter illustration establish a new measurement method? | No. Its conclusions are conditional on the count model; no physical validation or competitive estimation result is supplied. | Keep it an application under assumptions. |

This is a definite decision about what to publish, not a definitive historical
verdict. A positive novelty claim requires further evidence.

## Established ingredients

| Ingredient | Primary source and inspected location | Consequence for attribution |
| --- | --- | --- |
| Generalized matching distribution and its matched factorial moments | [Afendras and Papadatos, arXiv:1411.1165](https://arxiv.org/pdf/1411.1165), equation (3.1) and Lemma 3.1, PDF page 7. | Exactly the family used in the order-sharpness example. The source credits Niermann (1999). Neither the family nor its moment matching is new here. |
| Factorial-moment inversion | The same paper, Lemma 2.1, equation (2.5), PDF page 5. | Recovering probabilities once all required factorial moments are known is established machinery. |
| Poisson translation and subtraction | [Jørgensen and Kokonendji, arXiv:1409.7482](https://arxiv.org/pdf/1409.7482), section 2.2, equations (2.9)–(2.10). | A fixed independent Poisson contribution changes only the first factorial cumulant. This cancellation is established. |
| Recovery of nonnegative numbers from selected power sums | [Melánová, Sturmfels and Winter, arXiv:2106.13981v1](https://arxiv.org/pdf/2106.13981v1), Proposition 24, PDF page 12. | States a closely related identification result applicable to the Poisson-binomial subclass, as explained below. |

Niermann's [publisher record](https://link.springer.com/article/10.1007/BF02925521)
was inspected previously, but its restricted full text was not accessed. The
exact formula attribution above rests on the accessible Afendras–Papadatos
preprint. On 23 October 2026 the publisher still offered only a subscription
preview. The [author-affiliated publication list](https://ewas.de/publikationen.html)
listed the article without a full-text link; no accessible copy was obtained.
Additional references and access boundaries are in
[references.md](references.md).

## Additional terminology: finitized Poisson laws

Another established name for the sharpness family is **finitized Poisson**.
Golnabi, Levy and Cochran's
[*Finitizing power series distributions* (2009)](https://www.sciencedirect.com/science/article/abs/pii/S0167715209001886)
describes finite-support laws preserving Poisson moments through a specified
order under a parameter restriction. Cochran, Levy and Golnabi's
[*Matching the finitized Poisson distribution to the matching distributions*
(2013)](https://www.sciencedirect.com/science/article/abs/pii/S0167715213000564)
identifies that family with the generalized matching distributions. Its
displayed probabilities agree with this project's sharpness family after
substituting $n=D$ and $\lambda=h$; that substitution is our comparison.

Publisher-indexed previews, including the 2013 equivalence section comparing
equations (7) and (2), were inspected on 21 October 2026. Direct page access was
blocked and the complete papers were not reviewed. These references strengthen
the attribution and search terminology for the known lower-order example. They
do not resolve priority for the arbitrary bounded-law identification theorem
from orders $2,\ldots,D+1$ with the mean omitted.

## A closer overlap: the Poisson-binomial subclass

Proposition 24 of *Recovery from Power Sums* states that any $D$ distinct
positive-integer power sums determine a nonnegative $D$-vector up to permutation.
This is a relevant existing result even when the first power sum is omitted.
This comparison uses the stated proposition; it is not an independent audit of
its proof. The accessible preprint was inspected; direct access to the
[journal PDF](https://doi.org/10.1080/10586458.2022.2061650) returned HTTP 403.

The following application is our comparison with that result. For a sum of $D$
independent Bernoulli variables with parameters $p_i\in[0,1]$,

$$
P(t)=\prod_{i=1}^{D}(1+p_it),\qquad
\kappa_r=(-1)^{r-1}(r-1)!\sum_{i=1}^{D}p_i^r.
$$

Choosing power orders $2,\ldots,D+1$ therefore identifies the multiset of
parameters and hence the law. Zero parameters allow fewer than $D$ summands.
The preprint does not state this application in bounded-count language.

An arbitrary bounded law need not have this factorization. For example,
$\Pr(X=0)=\Pr(X=2)=1/2$ gives
$P(t)=1+t+t^2/2$, whose quadratic discriminant is $-1$. It cannot be written
as $(1+p_1t)(1+p_2t)$ with real Bernoulli parameters. Thus this application
does not by itself settle the general theorem's priority. The wider
power-sum literature is a concrete citation trail for further review.

### Follow-up through the cited injectivity theorem

Proposition 24 cites Müller, Feliu, Regensburger, Conradi, Shiu and Dickenstein's
[*Sign conditions for injectivity of generalized polynomial maps*](https://arxiv.org/pdf/1311.5493v2),
Theorem 1.4. Its statement and the preceding definitions were inspected on
23 October 2026. It characterizes injectivity for a family of generalized
polynomial maps on the positive orthant, with conditions quantified over all
positive coefficient parameters. This is an earlier general injectivity result
and a concrete continuation of the citation trail.

No reduction of the arbitrary bounded-law cumulant map to those hypotheses was
established in this review. Such a reduction would have to specify the maps and
parameter domain, verify the sign conditions, and cover boundary laws with zero
masses. Merely observing a nonzero Jacobian at interior points would not supply
that comparison. This source is a review lead, not a resolution of priority.

## Aggregate recovery from full generating functions

Fishman and coauthors' [*Count Bridges*, arXiv:2603.04730v1](https://arxiv.org/html/2603.04730v1),
Appendix B.2, gives another relevant comparison. Theorem B.10 recovers component
parameters as a multiset, up to permutation, from the full aggregate law under
conditional independence and an
explicit additive-identifiability assumption (Definition B.8). Lemma B.9 gives
finite linear independence of the analytic signatures as a sufficient condition.
Our comparison is that these statements do not supply the universal finite
`D+1` cutoff for arbitrary bounded laws while omitting the first factorial
cumulant. They provide related context, without resolving priority here.

This comparison concerns the inspected arXiv version, not search excerpts from
other versions. The OpenReview page presented an access challenge; the primary
arXiv text was available. No claim of a complete audit of that paper is made.

## What the search establishes

A further comparison is Stegmann and König's
[*Inverse counting statistics based on generalized factorial cumulants*,
arXiv:1611.02043v2](https://arxiv.org/pdf/1611.02043v2), sections 2–3,
equations (8)–(13), PDF pages 6–9. Their inputs are scaled long-time cumulants
of counted transitions in a finite-state stochastic system. A linear system
reconstructs its generator's characteristic polynomial when the required
uniqueness holds; they explicitly discuss failures of that uniqueness. Our
comparison is that a finite state space is not a bounded count per observation
window, and those inputs include lower orders. This establishes relevant prior
inverse-counting methodology, without supplying the arbitrary bounded-law,
missing-mean theorem here. It also cautions against presenting reconstruction
from factorial cumulants as a new general idea.

This follow-up searched for bounded and finite-support factorial-cumulant
identification, unknown Poisson addition, shifted-Poisson recovery, missing-first
power sums and polynomial logarithmic derivatives. It inspected the primary
sources identified above and compared their hypotheses with the project's
statement. No exact earlier statement covering every law on $0,\ldots,D$ at
the cutoff $D+1$ was located in that inspected material.

The 23 October follow-up rechecked the exact Afendras–Papadatos and
Melánová–Sturmfels–Winter statements, pursued legitimate access to Niermann's
article, and followed Proposition 24's reference to the earlier injectivity
theorem. Searches also used “missing mean”, “finite support”, “Poisson
convolution” and “nonnegative polynomial coefficients”. These steps did not
change the unresolved-priority conclusion.

This is a bounded search result. It does not establish that no such theorem
exists, that the positivity proof is new, or that this project has priority.
Older books, other terminology, non-English work, subscription sources and
comprehensive MathSciNet/zbMATH citation searches remain incompletely covered.
The elementary proof may be a corollary of an older general result.

Independent review should resolve both the exact statement and its relationship
to earlier work. A focused [review request](reviewer-request.md) identifies the
questions. A citation with a theorem number and a precise hypothesis comparison
would be more useful than an informal claim that the result is familiar or new.

## Exact questions still requiring review

1. Does an earlier theorem identify **every** law on a known $0,\ldots,D$ from
   precisely the factorial-cumulant orders $2,\ldots,D+1$, with no supplied
   mean? A result for generic laws, real-rooted generating polynomials, or an
   entire generating function does not alone answer this question.
2. Is the positivity argument in the short note an immediate corollary of an
   earlier polynomial or injectivity theorem? Supply the theorem number and
   full substitution, including degenerate support and zero coefficients.
3. Does Niermann's full article contain an identification statement beyond the
   known matching family? Direct inspection remains outstanding; the
   Afendras–Papadatos attribution already settles the family's status.
4. What publication description best reflects the resulting comparison: an
   exposition of a known result, a corollary with a short proof, or a result
   whose priority still needs investigation? Until that comparison is supplied,
   retain the publication decision above.
