import pytest

from sympy import EulerGamma, O, S, expint, log, series, simplify, symbols


@pytest.mark.parametrize("scale", [S(1), S(2), S(3), S.Half, S(5), 3*S.Half])
def test_expint_two_positive_origin_series_has_no_imaginary_branch_term(scale):
    x = symbols("x", positive=True)
    actual = series(expint(2, scale*x), x, 0, 2)
    expected = 1 + scale*x*(log(scale*x) - 1 + EulerGamma) + O(x**2)
    assert simplify(actual.removeO() - expected.removeO()) == 0
