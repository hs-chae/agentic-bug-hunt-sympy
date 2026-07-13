import pytest

from sympy import Sum, oo, symbols


@pytest.mark.parametrize("shift", [0, 1, 2, 3, 4, 5])
def test_telescoping_sum_does_not_ignore_undefined_initial_terms(shift):
    k = symbols("k", integer=True)
    expr = 1/((k - shift)*(k - shift - 1))
    result = Sum(expr, (k, shift, oo)).doit()
    assert result.is_finite is not True
