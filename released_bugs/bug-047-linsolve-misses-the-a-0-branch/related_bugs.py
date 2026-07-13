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
x, a = symbols("x a")
CASES = [1, 2, 3, 4, 5, 6]

def check_case(root):
    expr = a*(x - root)
    sol = linsolve([expr], [x])
    extra_solution = S(root + 1)
    residual = expr.subs({a: 0, x: extra_solution})
    reported_contains = (extra_solution,) in sol.subs(a, 0)
    ok = not (residual == 0 and not reported_contains)
    return ok, f"root={root} sol={sol} extra_solution={extra_solution} residual_at_a0={residual} reported_contains_after_a0={reported_contains}"

@pytest.mark.parametrize("root", CASES)
def test_sympy_correct(root):
    ok, detail = check_case(root)
    assert ok, detail

if __name__ == "__main__":
    failures = []
    for root in CASES:
        ok, detail = check_case(root)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
