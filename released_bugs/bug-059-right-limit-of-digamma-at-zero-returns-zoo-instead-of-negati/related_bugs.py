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
        @staticmethod
        def parametrize(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 6]


def check_case(scale):
    x = symbols("x")
    expr = polygamma(0, scale*x)
    got = limit(expr, x, 0, dir="+")
    sample = Rational(1, 10)**30
    sympy_sample = N(expr.subs(x, sample), 80)
    mp.mp.dps = 80
    oracle_sample = mp.digamma(mp.mpf(scale) * mp.mpf("1e-30"))
    ok = got == S.NegativeInfinity
    detail = (f"scale={scale} limit={got} expected=-oo "
              f"sympy_sample={sympy_sample} mpmath_sample={oracle_sample}")
    return ok, detail


@pytest.mark.parametrize("scale", CASES)
def test_sympy_correct(scale):
    ok, detail = check_case(scale)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for scale in CASES:
        ok, detail = check_case(scale)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
