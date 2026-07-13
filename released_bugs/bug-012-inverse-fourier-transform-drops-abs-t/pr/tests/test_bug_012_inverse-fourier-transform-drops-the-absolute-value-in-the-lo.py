import pytest
from sympy import Abs, exp, inverse_fourier_transform, pi, simplify, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_inverse_fourier_lorentzian_is_even(a):
    t, w = symbols("t w", real=True)
    expr = 2*a/(a**2 + 4*pi**2*w**2)
    inv = inverse_fourier_transform(expr, w, t)
    assert simplify(inv.subs(t, -1) - exp(-a*Abs(-1))) == 0
