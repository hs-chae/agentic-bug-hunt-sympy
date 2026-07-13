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
n = symbols("n", integer=True, nonnegative=True)
k = symbols("k", integer=True)
CASES = [1, 2, 3, 4, 5, 6]


def direct(power, value):
    return sum(((-1)**j) * (j**power) * binomial(value, j) for j in range(value + 1))

def check_case(power):
    closed = summation((-1)**k*k**power*binomial(n, k), (k, 0, n))
    value = 1
    lhs = closed.subs(n, value)
    rhs = direct(power, value)
    ok = lhs == rhs
    detail = f"power={power} closed={closed} closed_at_1={lhs} direct={rhs} difference={lhs-rhs}"
    return ok, detail

@pytest.mark.parametrize("power", CASES)
def test_sympy_correct(power):
    ok, detail = check_case(power)
    assert ok, detail

if __name__ == "__main__":
    failures=[]
    for power in CASES:
        ok, detail = check_case(power)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
