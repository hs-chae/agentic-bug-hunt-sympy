import pytest

from sympy import EmptySet, nonlinsolve, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_nonlinsolve_rejects_zero_denominator_solution(a):
    x, y = symbols("x y")
    eqs = [(x*y - a*x)/(x - a) - y, y - a]
    assert nonlinsolve(eqs, [x, y]) == EmptySet
