import pytest
from sympy import N, diff, integrate, log, simplify, symbols

@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_log_over_quadratic_antiderivative_differentiates_back(a):
    x = symbols("x")
    f = log(x)/(x**2 - a**2)
    F = integrate(f, x)
    residual = simplify(diff(F, x) - f)
    assert abs(complex(N(residual.subs(x, 2*a), 40))) < 1e-30
