import pytest
from sympy import diff, integrate, simplify, sqrt, symbols


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_integrate_sqrt_x_squared_plus_one_over_x_negative_branch(n):
    x = symbols("x")
    integrand = sqrt(x**2 + 1)/x
    antiderivative = integrate(integrand, x)
    assert simplify((diff(antiderivative, x) - integrand).subs(x, -n)) == 0
