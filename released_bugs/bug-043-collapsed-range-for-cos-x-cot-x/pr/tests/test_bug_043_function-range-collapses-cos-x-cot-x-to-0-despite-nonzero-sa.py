import pytest
from sympy import S, cos, cot, pi, sqrt, symbols
from sympy.calculus.util import continuous_domain, function_range


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_function_range_cos_over_cot_contains_defined_sample(a):
    x = symbols("x")
    expr = cos(x + a)/cot(x + a)

    assert expr.subs(x, pi/3 - a) == sqrt(3)/2
    assert expr.subs(x, pi/2 - a) is S.NaN
    assert continuous_domain(expr, x, S.Reals) != S.Reals
    assert function_range(expr, x, S.Reals).contains(sqrt(3)/2) is S.true
