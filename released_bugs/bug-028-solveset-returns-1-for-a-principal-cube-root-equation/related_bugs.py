import cmath
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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [3, 5, 7, 9, 11, 13]


def check_case(denominator):
    x = symbols("x")
    eq = Eq(x**Rational(1, denominator), -1)
    sol = solveset(eq, x, S.Reals)
    residual = simplify(eq.lhs.subs(x, -1) - eq.rhs)
    oracle_residual = complex(-1) ** (1.0 / denominator) - (-1)
    ok = (sol == S.EmptySet) and abs(oracle_residual) > 1e-12
    detail = (
        f"denominator={denominator} sol={sol} residual={residual} "
        f"oracle_residual={oracle_residual}"
    )
    return ok, detail


@pytest.mark.parametrize("denominator", CASES)
def test_sympy_correct(denominator):
    ok, detail = check_case(denominator)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for denominator in CASES:
        ok, detail = check_case(denominator)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
