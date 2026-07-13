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


import mpmath as mp
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
CASES = [-2, -3, -4, -5, -6, -7]


def oracle_integrand(x_value):
    return 1/(x_value*mp.sqrt(x_value*x_value - 1))


def check_case(x_value):
    x = symbols("x")
    integrand = 1/(x*sqrt(x**2 - 1))
    F = integrate(integrand, x)
    dF = diff(F, x)
    actual = N(dF.subs(x, x_value), 80)
    expected = N(integrand.subs(x, x_value), 80)
    oracle = oracle_integrand(mp.mpf(x_value))
    ok = abs(complex(actual - expected)) < 1e-50 and abs(complex(actual) - complex(oracle)) < 1e-40
    detail = (f"x={x_value} antiderivative={F} derivative={actual} "
              f"integrand={expected} oracle={oracle} difference={N(actual - expected, 50)}")
    return ok, detail


@pytest.mark.parametrize("x_value", CASES)
def test_sympy_correct(x_value):
    ok, detail = check_case(x_value)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for x_value in CASES:
        ok, detail = check_case(x_value)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
