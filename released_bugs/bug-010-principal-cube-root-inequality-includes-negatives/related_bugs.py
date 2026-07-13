import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

import cmath
try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*_args, **_kwargs):
            return lambda func: func

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()
from sympy.solvers.inequalities import solve_univariate_inequality

CASES = [1, 2, 3, 4, 5, 6]

def principal_cuberoot(z):
    return cmath.exp(cmath.log(complex(z)) / 3.0)

def check_case(m):
    x = symbols("x")
    sol = solve_univariate_inequality(x**(S(1)/3) <= m, x, relational=False)
    expected = Interval(0, m**3)
    bad = -1
    lhs_bad = N(bad**(S(1)/3), 50)
    oracle_bad = principal_cuberoot(bad)
    ok = sol == expected
    detail = f"m={m} sol={sol} expected={expected} contains_-1={sol.contains(bad)} lhs_bad={lhs_bad} oracle_bad={oracle_bad}"
    return ok, detail

@pytest.mark.parametrize("m", CASES)
def test_sympy_correct(m):
    ok, detail = check_case(m)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for case in CASES:
        ok, detail = check_case(case)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
