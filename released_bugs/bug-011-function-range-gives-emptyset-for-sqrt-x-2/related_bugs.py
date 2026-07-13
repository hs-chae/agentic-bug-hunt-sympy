import math
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)
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
import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.util import function_range

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [0, 1, -1, 2, -2, 3]


def check_case(a):
    x = symbols("x")
    expr = sqrt((x + a)**2)
    actual = function_range(expr, x, S.Reals)
    expected = Interval(0, oo)
    samples = [-a, -a + 2, -a - 3]
    oracle_values = [math.sqrt((float(s) + float(a))**2) for s in samples]
    contains = [actual.contains(v) for v in [0, 2, 3]]
    ok = actual == expected and oracle_values == [0.0, 2.0, 3.0]
    detail = f"a={a} actual={actual} expected={expected} samples={samples} oracle_values={oracle_values} contains={contains}"
    return ok, detail


@pytest.mark.parametrize("a", CASES)
def test_sympy_correct(a):
    ok, detail = check_case(a)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for a in CASES:
        ok, detail = check_case(a)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
