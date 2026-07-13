import pytest
from sympy import S, linsolve, symbols

x, a = symbols("x a")

@pytest.mark.parametrize("root", [1, 2, 3, 4, 5, 6])
def test_linsolve_keeps_zero_parameter_branch(root):
    expr = a*(x - root)
    sol = linsolve([expr], [x])
    extra_solution = S(root + 1)
    assert (extra_solution,) in sol.subs(a, 0)
