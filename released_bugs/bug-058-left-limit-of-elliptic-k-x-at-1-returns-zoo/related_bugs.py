import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath as mp
try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        def parametrize(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [0, 1, 2, 3, 4, 5]


def check_case(a):
    x = symbols("x")
    got = limit(elliptic_k(x - a), x, a + 1, dir="-")
    mp.mp.dps = 80
    eps = mp.mpf("1e-30")
    oracle_near = mp.ellipk(1 - eps)
    ok = got == oo and oracle_near > 0
    detail = f"a={a} got={got} expected=oo mpmath_ellipk_1_minus_eps={oracle_near}"
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
