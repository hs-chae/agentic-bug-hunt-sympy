import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath
import sympy
from sympy import S, besselj, diff, limit, symbols

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

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five additional scaled instantiations.
CASES = [S(1), S(1) / 2, S(3) / 2, S(3), S(4), S(5)]


def independent_numeric_derivative(c):
    """Evaluate d/dx J_1(c*x)/x near zero using mpmath only."""
    mpmath.mp.dps = 80
    cc = mpmath.mpf(str(c))
    xx = mpmath.mpf("1e-6")
    value = (
        cc * (mpmath.besselj(0, cc * xx) - mpmath.besselj(2, cc * xx)) / (2 * xx)
        - mpmath.besselj(1, cc * xx) / (xx**2)
    )
    expected_linear_approx = -(cc**3) * xx / 8
    return value, expected_linear_approx


def check_case(c):
    """Return (ok, detail). ok is True iff SymPy gives the correct zero limit."""
    x = symbols("x")
    expr = diff(besselj(1, c * x) / x, x)
    actual = limit(expr, x, 0)
    numeric, expected_near_zero = independent_numeric_derivative(c)
    numeric_ok = abs(numeric - expected_near_zero) < mpmath.mpf("1e-18")
    ok = actual == 0 and numeric_ok
    detail = (
        f"c={c} actual_limit={actual} expected_limit=0 "
        f"mpmath_at_1e-6={mpmath.nstr(numeric, 30)} "
        f"expected_near_zero={mpmath.nstr(expected_near_zero, 30)}"
    )
    return ok, detail


@pytest.mark.parametrize("c", CASES)
def test_sympy_correct(c):
    ok, detail = check_case(c)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for c in CASES:
        ok, detail = check_case(c)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
