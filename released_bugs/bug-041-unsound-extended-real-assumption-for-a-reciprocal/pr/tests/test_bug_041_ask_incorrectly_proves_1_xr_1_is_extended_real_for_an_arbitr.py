import pytest
from sympy import zoo, symbols
from sympy.assumptions import Q, ask


@pytest.mark.parametrize("a", [1, 0, -1, 2, 3, -2])
def test_extended_real_reciprocal_requires_nonzero_denominator(a):
    xr = symbols("xr", real=True)
    expr = 1/(xr - a)
    assert ask(Q.extended_real(expr)) is not True
    assert expr.subs(xr, a) == zoo
