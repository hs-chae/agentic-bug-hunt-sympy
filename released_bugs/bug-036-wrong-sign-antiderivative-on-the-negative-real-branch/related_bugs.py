import math
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403
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
print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 9]


def check_case(a):
    x = symbols("x")
    integrand = 1/(x*sqrt(x**2 + a))
    F = integrate(integrand, x)
    dF = diff(F, x)
    point = -2
    sympy_derivative = N(dF.subs(x, point), 50)
    sympy_integrand = N(integrand.subs(x, point), 50)
    difference = N((dF - integrand).subs(x, point), 50)
    oracle_integrand = 1.0/(point*math.sqrt(point*point + a))
    ok = abs(complex(difference)) < 1e-40
    detail = (
        f"a={a} F={F} derivative_at_-2={sympy_derivative} "
        f"integrand_at_-2={sympy_integrand} difference={difference} "
        f"oracle_integrand={oracle_integrand}"
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
