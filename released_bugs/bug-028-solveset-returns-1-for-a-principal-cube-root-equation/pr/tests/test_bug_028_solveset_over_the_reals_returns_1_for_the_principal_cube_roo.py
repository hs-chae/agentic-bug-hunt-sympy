import pytest

from sympy import Eq, EmptySet, Rational, S, solveset, symbols


@pytest.mark.parametrize("denominator", [3, 5, 7, 9, 11, 13])
def test_principal_odd_root_equation_has_no_negative_real_solution(denominator):
    x = symbols("x")
    assert solveset(Eq(x**Rational(1, denominator), -1), x, S.Reals) == EmptySet
