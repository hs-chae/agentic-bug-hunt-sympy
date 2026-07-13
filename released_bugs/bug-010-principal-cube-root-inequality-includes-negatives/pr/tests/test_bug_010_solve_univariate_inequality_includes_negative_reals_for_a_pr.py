import pytest
from sympy import Interval, S, symbols
from sympy.solvers.inequalities import solve_univariate_inequality

@pytest.mark.parametrize("m", [1, 2, 3, 4, 5, 6])
def test_fractional_power_inequality_real_domain(m):
    x = symbols("x")
    assert solve_univariate_inequality(x**(S(1)/3) <= m, x, relational=False) == Interval(0, m**3)
