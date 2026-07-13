import pytest

from sympy import S, lerchphi, limit, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_left_limit_lerchphi_s_one_at_one_is_positive_infinity(a):
    x = symbols("x")
    assert limit(lerchphi(x, 1, a), x, 1, dir="-") == S.Infinity
