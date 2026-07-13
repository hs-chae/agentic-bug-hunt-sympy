import pytest

from sympy import FiniteSet, Rational, S
from sympy.stats import Uniform, quantile


@pytest.mark.parametrize(
    "name,a,b",
    [
        ("unit_interval", S.Zero, S.One),
        ("shifted_interval", S(-2), S(3)),
        ("positive_interval", S(2), S(5)),
        ("rational_interval", Rational(1, 3), Rational(7, 3)),
        ("negative_interval", Rational(-5, 2), Rational(-1, 2)),
        ("ending_at_zero", S(-1), S.Zero),
    ],
)
def test_uniform_quantile_at_one_returns_upper_endpoint(name, a, b):
    U = Uniform("U_" + name, a, b)
    assert quantile(U)(S.One) == FiniteSet(b)
