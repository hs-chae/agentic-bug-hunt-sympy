import pytest

from sympy import S, loggamma, symbols
from sympy.calculus.singularities import singularities


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_singularities_loggamma_contains_shifted_zero(a):
    x = symbols("x")
    s = singularities(loggamma(x - a), x, S.Complexes)
    assert s.contains(a) is S.true
