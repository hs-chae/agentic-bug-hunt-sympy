import pytest

from sympy import elliptic_k, limit, oo, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_left_limit_elliptic_k_at_one_is_positive_infinity(a):
    x = symbols("x")
    assert limit(elliptic_k(x - a), x, a + 1, dir="-") == oo
