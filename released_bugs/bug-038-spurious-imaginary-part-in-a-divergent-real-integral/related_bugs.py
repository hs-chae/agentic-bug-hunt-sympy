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
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
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
CASES = [1, 2, 3, 4, 5, 6]


def check_case(a):
    x = symbols("x", real=True)
    val = integrate(1/Abs(x), (x, -a, 0))
    truncated_10 = integrate(1/Abs(x), (x, -a, -Rational(1, 10)))
    truncated_100 = integrate(1/Abs(x), (x, -a, -Rational(1, 100)))
    oracle_10 = math.log(10*a)
    oracle_100 = math.log(100*a)
    ok = val == oo
    detail = (f"a={a} integral={val} truncated_1_10={truncated_10} "
              f"truncated_1_100={truncated_100} oracle10={oracle_10} oracle100={oracle_100}")
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
