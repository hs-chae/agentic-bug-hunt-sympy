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
CASES = [1, 2, 3, 4, 5, 6]


def check_case(a):
    n = symbols("n")
    term = sin(pi*n)/(n - a)
    lo = a - 1
    hi = a + 1
    result = product(term, (n, lo, hi))
    values = [term.subs(n, i) for i in range(lo, hi + 1)]
    direct = Mul(*values)
    try:
        oracle_values = [cmath.sin(cmath.pi*i)/(i - a) for i in range(lo, hi + 1)]
        oracle_defined = True
    except ZeroDivisionError:
        oracle_values = None
        oracle_defined = False
    ok = not (nan in values and result == 0 and direct is nan and not oracle_defined)
    detail = (
        f"a={a} result={result} values={values} direct_raw_product={direct} "
        f"cmath_defined={oracle_defined} oracle_values={oracle_values}"
    )
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
