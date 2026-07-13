import pytest
from sympy import S, atan, pi, symbols, tan
from sympy.solvers.inequalities import solve_univariate_inequality


@pytest.mark.parametrize("bound,point", [(pi, 0), (3*pi/4, -1), (2*pi, 0), (5*pi/4, 1), (10, tan(10)), (3*pi, 0)])
def test_atan_inequality_keeps_points_that_satisfy_strict_inequality(bound, point):
    x = symbols("x")
    sol = solve_univariate_inequality(atan(x) < bound, x, relational=False)
    assert S(point) in sol
    assert atan(S(point)) < bound
