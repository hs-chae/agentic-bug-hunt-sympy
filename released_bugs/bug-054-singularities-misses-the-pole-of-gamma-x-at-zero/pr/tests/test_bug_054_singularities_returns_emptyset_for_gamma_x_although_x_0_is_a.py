import pytest
from sympy import S, gamma, symbols
from sympy.calculus.singularities import singularities


@pytest.mark.parametrize("shift", [0, 1, 2, -1, 3, -2])
def test_singularities_gamma_shifted_poles(shift):
    x = symbols("x")
    assert singularities(gamma(x + shift), x, S.Complexes).contains(-shift) == S.true
