import pytest
from sympy import N, diff, integrate, sqrt, symbols


@pytest.mark.parametrize("x_value", [-2, -3, -4, -5, -6, -7])
def test_integral_of_inverse_x_sqrt_x2_minus_1_negative_branch(x_value):
    x = symbols("x")
    integrand = 1/(x*sqrt(x**2 - 1))
    antiderivative = integrate(integrand, x)
    residual = diff(antiderivative, x) - integrand
    assert abs(complex(N(residual.subs(x, x_value), 50))) < 1e-40
