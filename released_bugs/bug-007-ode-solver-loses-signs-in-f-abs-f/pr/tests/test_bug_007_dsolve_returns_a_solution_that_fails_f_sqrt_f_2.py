import pytest

from sympy import Eq, Function, N, diff, dsolve, sqrt, symbols


@pytest.mark.parametrize("c", [1, 2, 3, 4, 5, 6])
def test_dsolve_sqrt_f_squared_branches_satisfy_ode_for_positive_constants(c):
    x = symbols("x")
    f = Function("f")
    ode = Eq(diff(f(x), x), sqrt(f(x)**2))
    sol = dsolve(ode)

    for equation in sol:
        rhs = equation.rhs
        constants = [s for s in rhs.free_symbols if s != x]
        concrete_rhs = rhs.subs({constant: c for constant in constants})
        residual_at_zero = N((diff(concrete_rhs, x) - sqrt(concrete_rhs**2)).subs(x, 0), 50)
        assert abs(complex(residual_at_zero)) < 1e-40
