import pytest

from sympy import Eq, Piecewise, S, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_incomplete_piecewise_undefined_branch_survives_core_identities(a):
    x = symbols("x", real=True)
    p = Piecewise((a + 1, x > a))
    bad_point = a - 1

    assert p.subs(x, bad_point) is S.NaN
    assert (p * 0).subs(x, bad_point) is S.NaN
    assert (p - p).subs(x, bad_point) is S.NaN
    assert Eq(p, p).subs(x, bad_point) is not S.true
