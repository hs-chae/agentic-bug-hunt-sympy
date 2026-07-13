import pytest

from sympy import Eq, FiniteSet, S, asin, pi, simplify, solveset, symbols


@pytest.mark.parametrize("n", [1, 2, -1, 3, 4, 5])
def test_solveset_principal_asin_rejects_out_of_range_targets(n):
    x = symbols("x")
    eq = Eq(asin(x), n*pi)
    sol = solveset(eq, x, domain=S.Complexes)

    assert sol != FiniteSet(0)
    assert simplify(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0)) != 0
