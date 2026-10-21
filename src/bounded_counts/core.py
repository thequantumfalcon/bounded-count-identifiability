"""Standard factorial-moment and factorial-cumulant identities over rationals.

For P(t) = E[(1+t)**X], m_r = P^(r)(0) and
kappa_r = (log P)^(r)(0). The finite recurrence below avoids numerical
logarithms and any approximation to a Poisson tail.
"""

from collections.abc import Iterable
from fractions import Fraction
from math import comb, factorial

Exact = int | Fraction


def _fraction(value: Exact, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(
            f"{name} must be an integer or Fraction; floats are not accepted"
        )
    return Fraction(value)


def _nonnegative_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def validate_law(
    probabilities: Iterable[Exact], *, support_bound: int | None = None
) -> tuple[Fraction, ...]:
    """Validate p[x] = P(X=x) and return an exact probability tuple.

    Inputs must be nonempty, nonnegative and sum exactly to one. If a known
    support bound D is supplied, zero padding/trimming returns D+1 entries;
    positive probability above D is rejected. Without D, trailing zeros are
    preserved. Validating this array does not validate a physical source bound.
    """
    p = tuple(_fraction(value, "probability") for value in probabilities)
    if not p:
        raise ValueError("a probability law must contain at least one entry")
    if any(value < 0 for value in p):
        raise ValueError("probabilities must be nonnegative")
    if sum(p, Fraction(0)) != 1:
        raise ValueError("probabilities must sum exactly to one")
    if support_bound is None:
        return p
    degree = _nonnegative_integer(support_bound, "support_bound")
    if any(p[degree + 1 :]):
        raise ValueError("positive probability occurs above support_bound")
    return p[: degree + 1] + (Fraction(0),) * max(0, degree + 1 - len(p))


def factorial_moments(
    probabilities: Iterable[Exact],
    order: int,
    *,
    support_bound: int | None = None,
) -> tuple[Fraction, ...]:
    """Return (1, E[X], E[X(X-1)], ...) through the requested order.

    Orders above the actual source support return zero, including the D=0 law.
    """
    order = _nonnegative_integer(order, "order")
    p = validate_law(probabilities, support_bound=support_bound)
    falling = [1] * len(p)
    moments = [Fraction(1)]
    for r in range(1, order + 1):
        for x in range(len(p)):
            falling[x] = falling[x] * (x - r + 1) if x >= r else 0
        moments.append(
            sum((mass * value for mass, value in zip(p, falling)), Fraction(0))
        )
    return tuple(moments)


def factorial_cumulants_from_moments(moments: Iterable[Exact]) -> tuple[Fraction, ...]:
    """Convert a finite factorial-moment list, including m[0]=1, to cumulants.

    The recurrence is kappa_n = m_n - sum_{j=1}^{n-1}
    binom(n-1,j-1) kappa_j m_{n-j}. This checks normalization and nonnegative
    moment entries; it does NOT decide whether an arbitrary moment sequence is
    realizable by a probability law. kappa[0]=0 is the log-normalization term.
    """
    m = tuple(_fraction(value, "moment") for value in moments)
    if not m or m[0] != 1:
        raise ValueError("moments must start with order-zero moment 1")
    if any(value < 0 for value in m):
        raise ValueError("factorial moments of a nonnegative count must be nonnegative")
    cumulants = [Fraction(0)]
    for n in range(1, len(m)):
        correction = sum(
            (comb(n - 1, j - 1) * cumulants[j] * m[n - j] for j in range(1, n)),
            Fraction(0),
        )
        cumulants.append(m[n] - correction)
    return tuple(cumulants)


def factorial_cumulants(
    probabilities: Iterable[Exact],
    order: int,
    *,
    support_bound: int | None = None,
) -> tuple[Fraction, ...]:
    """Return factorial cumulants through order, including kappa[0]=0."""
    return factorial_cumulants_from_moments(
        factorial_moments(probabilities, order, support_bound=support_bound)
    )


def poisson_added_factorial_moments(
    probabilities: Iterable[Exact],
    background: Exact,
    order: int,
    *,
    support_bound: int | None = None,
) -> tuple[Fraction, ...]:
    """Exact factorial moments of Y=X+Z, assuming independent Z~Poisson(b).

    background is b, the fixed expected count per window, not an instantaneous
    rate in unspecified units. Random b, dependence and detector nonlinearities
    are outside this function's model. No finite Poisson-tail truncation is used.
    """
    b = _fraction(background, "background")
    if b < 0:
        raise ValueError("background must be nonnegative")
    source = factorial_moments(probabilities, order, support_bound=support_bound)
    return tuple(
        sum((comb(r, k) * source[k] * b ** (r - k) for k in range(r + 1)), Fraction(0))
        for r in range(len(source))
    )


def poisson_added_factorial_cumulants(
    probabilities: Iterable[Exact],
    background: Exact,
    order: int,
    *,
    support_bound: int | None = None,
) -> tuple[Fraction, ...]:
    """Cumulants of the independent fixed-Poisson addition model.

    Computed from the full factorial-moment convolution. The resulting first
    cumulant shifts by b; every higher cumulant equals that of the source.
    """
    return factorial_cumulants_from_moments(
        poisson_added_factorial_moments(
            probabilities, background, order, support_bound=support_bound
        )
    )


def generalized_matching_law(degree: int, strength: Exact) -> tuple[Fraction, ...]:
    """Return the established generalized matching (quasi-Poisson) count law.

    For D>=0 and 0<=h<=1, p_j = h**j/j! * sum_{i=0}^{D-j} (-h)**i/i!.
    Equivalently, retain each fixed point of a uniform permutation of D items
    independently with probability h. D=0 always gives the zero-count law.
    For D>=1 the factorial moments through D are h**r; the factorial cumulants
    are kappa_1=h, kappa_2=...=kappa_D=0, kappa_{D+1}=-h**(D+1).

    Attribution: Afendras and Papadatos, "A factorial moment distance and an
    application to the matching problem", arXiv:1411.1165, Eq. (3.1) and Lemma
    3.1, https://arxiv.org/abs/1411.1165. That paper credits Niermann (1999),
    "A generalization of the matching distribution", DOI 10.1007/BF02925521.
    The distribution and its moment-matching property are established prior art.
    """
    degree = _nonnegative_integer(degree, "degree")
    h = _fraction(strength, "strength")
    if not 0 <= h <= 1:
        raise ValueError("strength must lie in [0, 1]")
    probabilities = (
        h**j
        / factorial(j)
        * sum(((-h) ** i / factorial(i) for i in range(degree - j + 1)), Fraction(0))
        for j in range(degree + 1)
    )
    return validate_law(probabilities, support_bound=degree)
