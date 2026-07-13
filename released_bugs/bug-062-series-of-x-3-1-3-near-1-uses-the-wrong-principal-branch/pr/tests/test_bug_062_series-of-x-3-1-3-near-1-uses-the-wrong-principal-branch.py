from sympy import I, Rational, exp, pi, series, simplify, symbols
import pytest


@pytest.mark.parametrize("power", [3, 5, 7, 9, 11, 13])
def test_series_odd_root_power_respects_principal_branch_at_negative_point(power):
    x = symbols("x")
    expr = (x**power)**Rational(1, power)
    ser = series(expr, x, -1, 2).removeO()
    assert simplify(ser.subs(x, -1) - exp(I*pi/power)) == 0
