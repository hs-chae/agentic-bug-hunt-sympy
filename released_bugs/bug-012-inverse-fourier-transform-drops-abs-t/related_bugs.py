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
import mpmath as mp

CASES = [1, 2, 3, 4, 5, 6]


def check_case(a):
    t, w = symbols("t w", real=True)
    expr = 2*a/(a**2 + 4*pi**2*w**2)
    inv = inverse_fourier_transform(expr, w, t)
    bad_t = -1
    actual = inv.subs(t, bad_t)
    expected = exp(-a*Abs(bad_t))
    mp_expected = mp.e**(-a*abs(bad_t))
    mp_actual = complex(N(actual, 80))
    ok = simplify(actual - expected) == 0
    detail = (f"a={a} inverse={inv} actual={actual} expected={expected} "
              f"mp_actual={mp_actual} mp_expected={mp_expected}")
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
