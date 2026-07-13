import pytest
from sympy import Eq, N, Rational, S, solveset, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_principal_fractional_power_equation_excludes_negative_branch(a):
    x = symbols("x")
    lhs = ((x + a)**2)**Rational(1, 3)
    rhs = (x + a)**Rational(2, 3)
    bad = -a - 1
    sol = solveset(Eq(lhs, rhs), x, domain=S.Reals)
    assert N((lhs - rhs).subs(x, bad), 30) != 0
    assert sol.contains(bad) is not S.true
