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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

import math
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

CASES = [(pi, 0), (3*pi/4, -1), (2*pi, 0), (5*pi/4, 1), (10, tan(10)), (3*pi, 0)]


def check_case(bound, omitted):
    x = symbols("x")
    sol = solve_univariate_inequality(atan(x) < bound, x, relational=False)
    sympy_contains = omitted in sol
    sympy_truth = bool(atan(omitted) < bound)
    oracle_truth = math.atan(float(N(omitted, 30))) < float(N(bound, 30))
    ok = bool(sympy_contains) == oracle_truth
    detail = f"bound={bound} sol={sol} omitted={omitted} contains={sympy_contains} sympy_truth={sympy_truth} oracle_truth={oracle_truth}"
    return ok, detail


@pytest.mark.parametrize("bound,omitted", CASES)
def test_sympy_correct(bound, omitted):
    ok, detail = check_case(bound, omitted)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for bound, omitted in CASES:
        ok, detail = check_case(bound, omitted)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
