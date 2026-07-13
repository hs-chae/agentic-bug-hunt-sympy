import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

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
from sympy.calculus.util import continuous_domain

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 6]


def check_case(k):
    x = symbols("x")
    expr = sqrt(sin(k*x))
    dom = continuous_domain(expr, x, S.Reals)
    witness = 5*pi/(2*k)
    contained = dom.contains(witness)
    value = expr.subs(x, witness)
    oracle_value = cmath.sqrt(complex(cmath.sin(complex(N(k*witness, 80)))))
    ok = contained is S.true
    detail = (f"k={k} domain={dom} witness={witness} contained={contained} "
              f"sympy_value={value} oracle_value={oracle_value}")
    return ok, detail


@pytest.mark.parametrize("k", CASES)
def test_sympy_correct(k):
    ok, detail = check_case(k)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for k in CASES:
        ok, detail = check_case(k)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
