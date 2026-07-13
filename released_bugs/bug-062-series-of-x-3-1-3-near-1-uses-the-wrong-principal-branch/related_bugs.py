import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import cmath
import math
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

CASES = [3, 5, 7, 9, 11, 13]


def check_case(power):
    x = symbols("x")
    expr = (x**power)**Rational(1, power)
    ser = series(expr, x, -1, 2).removeO()
    center = ser.subs(x, -1)
    expected_center = exp(I*pi/power)
    sample = Rational(-9, 10)
    expr_sample = N(expr.subs(x, sample), 50)
    series_sample = N(ser.subs(x, sample), 50)
    oracle_sample = complex(float(sample) ** power, 0.0) ** (1.0 / power)
    oracle_center = cmath.exp(1j * math.pi / power)
    ok = simplify(center - expected_center) == 0
    detail = (f"power={power} series={ser} center={center} expected_center={expected_center} "
              f"expr_sample={expr_sample} series_sample={series_sample} "
              f"oracle_center={oracle_center} oracle_sample={oracle_sample}")
    return ok, detail


@pytest.mark.parametrize("power", CASES)
def test_sympy_correct(power):
    ok, detail = check_case(power)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for power in CASES:
        ok, detail = check_case(power)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
