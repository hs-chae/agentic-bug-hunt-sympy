import pytest
from sympy import S, symbols, zeta
from sympy.calculus.singularities import singularities


@pytest.mark.parametrize("offset", [0, 1, 2, -1, 3, -2])
def test_singularities_zeta_includes_shifted_pole(offset):
    x = symbols("x")
    result = singularities(zeta(x + offset), x, S.Complexes)
    assert result.contains(S.One - offset) is S.true
