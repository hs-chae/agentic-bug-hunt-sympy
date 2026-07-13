import pytest
from sympy import Eq, FiniteSet, Integer, Rational, S, solveset, symbols


@pytest.mark.parametrize("m", [2, 3, 4, 5, 6, 7])
def test_solveset_principal_two_thirds_power_excludes_negative_branch(m):
    x = symbols("x")
    sol = solveset(Eq(x**Rational(2, 3), Integer(m)**2), x, S.Reals)
    assert sol == FiniteSet(Integer(m)**3)
