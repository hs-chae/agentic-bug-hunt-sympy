import pytest

from sympy import Rational, S, sqrt
from sympy.stats import Rayleigh, cdf


CASES = [
    (S.One, S.NegativeOne),
    (S(2), S.NegativeOne),
    (S.One, S(-2)),
    (S(3), S(-5)),
    (Rational(1, 2), S.NegativeOne),
    (sqrt(2), S(-3)),
]


@pytest.mark.parametrize("sigma,z", CASES)
def test_rayleigh_cdf_is_zero_below_support(sigma, z):
    R = Rayleigh("R", sigma)
    assert cdf(R)(z) == 0
