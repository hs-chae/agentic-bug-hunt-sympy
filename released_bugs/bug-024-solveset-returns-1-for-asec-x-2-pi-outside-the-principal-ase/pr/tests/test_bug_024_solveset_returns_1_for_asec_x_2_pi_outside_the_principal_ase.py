import pytest

from sympy import Eq, FiniteSet, S, asec, pi, simplify, solveset, symbols


@pytest.mark.parametrize("n", [1, 2, -1, 3, 4, 5])
def test_solveset_asec_rejects_out_of_range_targets(n):
    x = symbols("x")
    eq = Eq(asec(x), 2*pi*n)
    sol = solveset(eq, x, domain=S.Complexes)

    assert sol != FiniteSet(1)
    assert simplify((eq.lhs - eq.rhs).subs(x, 1)) != 0
