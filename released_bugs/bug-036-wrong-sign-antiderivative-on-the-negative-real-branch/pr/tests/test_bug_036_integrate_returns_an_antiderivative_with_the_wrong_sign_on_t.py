import pytest

from sympy import N, diff, integrate, sqrt, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 9])
def test_integrate_x_sqrt_x2_plus_a_negative_branch_sign(a):
    x = symbols("x")
    integrand = 1/(x*sqrt(x**2 + a))
    F = integrate(integrand, x)
    difference = N((diff(F, x) - integrand).subs(x, -2), 50)

    assert abs(complex(difference)) < 1e-40
