"""Exact rational calculations for a specified bounded-count probability model.

All public numerical inputs are integers or fractions.Fraction values. Floating
point inputs are rejected rather than silently converted. Moment and cumulant
tuples include order zero: m[0] = 1 and kappa[0] = 0.

The functions describe population quantities. They neither estimate a law from
measurements nor check the physical independence, support or detector assumptions.
"""

from .core import (
    factorial_cumulants,
    factorial_cumulants_from_moments,
    factorial_moments,
    generalized_matching_law,
    poisson_added_factorial_cumulants,
    poisson_added_factorial_moments,
    validate_law,
)

__all__ = [
    "factorial_cumulants",
    "factorial_cumulants_from_moments",
    "factorial_moments",
    "generalized_matching_law",
    "poisson_added_factorial_cumulants",
    "poisson_added_factorial_moments",
    "validate_law",
]

__version__ = "0.1.0.dev0"
