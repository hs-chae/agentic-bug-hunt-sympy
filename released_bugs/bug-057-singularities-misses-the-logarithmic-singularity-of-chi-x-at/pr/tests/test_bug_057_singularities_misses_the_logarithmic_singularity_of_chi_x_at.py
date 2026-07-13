import pytest

from sympy import Chi, S, singularities, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_singularities_chi_includes_logarithmic_origin(a):
    x = symbols("x")
    result = singularities(Chi(x - a), x, S.Complexes)
    assert result.contains(S(a)) is S.true
