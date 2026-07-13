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

CASES = [1, 2, 3, 4, 5, 6]


def check_case(c):
    x = symbols("x")
    f = Function("f")
    ode = Eq(diff(f(x), x), sqrt(f(x)**2))
    sol = dsolve(ode)
    failures = []
    details = []
    for equation in sol:
        rhs = equation.rhs
        constants = [s for s in rhs.free_symbols if s != x]
        concrete_rhs = rhs.subs({constant: c for constant in constants})
        residual = simplify(diff(concrete_rhs, x) - sqrt(concrete_rhs**2))
        residual_at_zero = N(residual.subs(x, 0), 50)
        oracle_residual = -c - abs(c) if concrete_rhs == c*exp(-x) else None
        details.append(
            f"branch={concrete_rhs} residual={residual} "
            f"residual_at_0={residual_at_zero} oracle_residual={oracle_residual}"
        )
        if abs(complex(residual_at_zero)) > 1e-40:
            failures.append(str(concrete_rhs))
    ok = not failures
    detail = f"c={c} dsolve={sol} " + "; ".join(details)
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
