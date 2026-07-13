import pytest
from sympy import Rational, S, symbols
from sympy.calculus.singularities import singularities


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_singularities_include_poles_of_shifted_principal_power(a):
    x = symbols("x")
    expr = 1/(((x - a)**2)**Rational(1, 3) - 1)
    s = singularities(expr, x, S.Reals)
    assert s.contains(a - 1) is S.true
    assert s.contains(a + 1) is S.true
