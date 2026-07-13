import cmath
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)
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
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 6]


def check_case(n):
    x = symbols("x")
    integrand = sqrt(x**2 + 1)/x
    F = integrate(integrand, x)
    point = -n
    derivative_value = diff(F, x).subs(x, point)
    integrand_value = integrand.subs(x, point)
    residual = simplify(derivative_value - integrand_value)
    oracle_integrand = cmath.sqrt(point**2 + 1) / point
    ok = residual == 0
    detail = (f"x={point} derivative={derivative_value} integrand={integrand_value} "
              f"residual={residual} oracle_integrand={oracle_integrand}")
    return ok, detail


@pytest.mark.parametrize("n", CASES)
def test_sympy_correct(n):
    ok, detail = check_case(n)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for n in CASES:
        ok, detail = check_case(n)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
