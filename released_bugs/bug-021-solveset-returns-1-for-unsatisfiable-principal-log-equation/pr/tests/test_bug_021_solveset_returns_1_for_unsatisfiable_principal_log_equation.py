import pytest

from sympy import Eq, FiniteSet, I, S, log, pi, simplify, solveset, symbols


@pytest.mark.parametrize("n", [1, 2, -1, 3, 4, 5])
def test_solveset_principal_log_rejects_out_of_range_targets(n):
    x = symbols("x")
    eq = Eq(log(x), 2*pi*I*n)
    sol = solveset(eq, x, domain=S.Complexes)

    assert sol != FiniteSet(1)
    assert simplify(eq.lhs.subs(x, 1) - eq.rhs.subs(x, 1)) != 0
