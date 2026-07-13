import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import cmath
import math
import sympy
from sympy import *  # noqa: F401,F403

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        def parametrize(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative offset first, then five additional split-period arguments.
CASES = [1, 2, 3, 4, 5, 6]


def check_case(offset):
    expr = sinh(I*pi + I*(pi - offset))
    exact_expected = -I*sin(offset)
    sympy_value = complex(N(expr, 80))
    oracle_value = cmath.sinh(1j*(2*math.pi - offset))
    ok = abs(sympy_value - oracle_value) < 1e-40 and simplify(expr - exact_expected) == 0
    detail = (
        f"offset={offset} expr={expr} expected={exact_expected} "
        f"sympy_numeric={sympy_value} cmath_oracle={oracle_value}"
    )
    return ok, detail


@pytest.mark.parametrize("offset", CASES)
def test_sympy_correct(offset):
    ok, detail = check_case(offset)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for offset in CASES:
        ok, detail = check_case(offset)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
