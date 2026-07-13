import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import math
import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.util import function_range

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

# Representative interval first, then five additional intervals inside (-pi/2, pi/2).
CASES = [S.One, Rational(1, 2), Rational(1, 3), Rational(2, 3), Rational(3, 4), Rational(1, 4)]


def check_case(bound):
    x = symbols("x")
    expr = sqrt(tan(x)**2)
    actual = function_range(expr, x, Interval(-bound, bound))
    expected = Interval(0, tan(bound))

    sample = bound/2
    sympy_sample = N(expr.subs(x, sample), 50)
    oracle_sample = abs(math.tan(float(sample)))
    sample_error = abs(float(sympy_sample) - oracle_sample)

    ok = actual == expected and expr.subs(x, 0) == 0 and sample_error < 1e-14
    detail = (
        f"bound={bound} actual={actual} expected={expected} "
        f"contains_0={actual.contains(0)} value_at_0={expr.subs(x, 0)} "
        f"sample={sample} sympy_sample={sympy_sample} "
        f"python_abs_tan_sample={oracle_sample} sample_error={sample_error}"
    )
    return ok, detail


@pytest.mark.parametrize("bound", CASES)
def test_sympy_correct(bound):
    ok, detail = check_case(bound)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for bound in CASES:
        ok, detail = check_case(bound)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
