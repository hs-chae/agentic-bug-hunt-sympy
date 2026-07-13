import pytest

from sympy import Eq, S, simplify, solveset, sqrt, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_solveset_sqrt_square_not_all_complexes(a):
    x = symbols("x")
    eq = Eq(sqrt((x + a)**2), x + a)
    sol = solveset(eq, x, domain=S.Complexes)
    bad = -a - 1

    assert sol != S.Complexes
    assert simplify(eq.lhs.subs(x, bad) - eq.rhs.subs(x, bad)) != 0
