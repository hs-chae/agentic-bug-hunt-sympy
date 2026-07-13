import pytest

from sympy import S, integrate, oo, symbols
from sympy.stats import P, Uniform, density, given


@pytest.mark.parametrize("t", [S.Half, S(1)/3, S(1)/4, S(2)/3, S(3)/4, S(1)/5])
def test_conditional_uniform_density_support_is_restricted(t):
    x = symbols("x")
    U = Uniform("U", 0, 1)
    Y = given(U, U > t)
    d = density(Y)(x)

    assert integrate(d, (x, -oo, oo)) == 1
    assert integrate(d, (x, 0, t)) == 0
    assert d.subs(x, t/2) == 0
    assert P(Y < t) == 0
