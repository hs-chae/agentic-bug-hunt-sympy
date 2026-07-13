import pytest
from sympy import Function, S, rsolve, symbols


CASES = [2, 3, 4, 5, 6, 7]


@pytest.mark.parametrize("a", CASES)
def test_rsolve_constant_free_solution_satisfies_initial_conditions(a):
    n = symbols("n", integer=True)
    y = Function("y")
    rec = y(n + 2) - (n + a)*y(n + 1) + y(n)
    sol = rsolve(rec, y(n), {y(0): S.One, y(1): S.One})

    assert sol is not None
    assert sol.subs(n, 0) == S.One
    assert sol.subs(n, 1) == S.One
