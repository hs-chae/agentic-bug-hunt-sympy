import pytest
from sympy import Eq, I, Interval, S, exp, pi, solveset, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_solveset_exp_i_x_includes_closed_period_endpoint(a):
    x = symbols("x")
    sol = solveset(Eq(exp(I*(x + a)), 1), x, Interval(-a, 2*pi - a))
    assert sol.contains(2*pi - a) is S.true
