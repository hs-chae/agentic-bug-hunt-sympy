from sympy import S, limit, polygamma, symbols
import pytest


@pytest.mark.parametrize("scale", [1, 2, 3, 4, 5, 6])
def test_digamma_right_limit_at_zero_preserves_sign(scale):
    x = symbols("x")
    assert limit(polygamma(0, scale*x), x, 0, dir="+") == S.NegativeInfinity
