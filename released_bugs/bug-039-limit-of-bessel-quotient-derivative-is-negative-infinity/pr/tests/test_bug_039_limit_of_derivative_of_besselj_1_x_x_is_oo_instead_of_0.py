import pytest

from sympy import Rational, besselj, diff, limit, symbols


@pytest.mark.parametrize("c", [1, Rational(1, 2), Rational(3, 2), 3, 4, 5])
def test_limit_derivative_scaled_besselj1_quotient(c):
    x = symbols("x")
    expr = diff(besselj(1, c * x) / x, x)

    assert limit(expr, x, 0) == 0
