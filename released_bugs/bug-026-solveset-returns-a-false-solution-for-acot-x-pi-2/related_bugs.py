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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [0, 1, -1, 2, -3, pi]


def principal_acot_real(value):
    if value == 0:
        return math.pi/2
    return math.atan(1/value)


def check_case(shift):
    x = symbols("x")
    sol = solveset(Eq(acot(x - shift), -pi/2), x, S.Reals)
    witness = shift
    sympy_contains = sol.contains(witness)
    sympy_residual = simplify(acot(witness - shift) + pi/2)
    oracle_residual = principal_acot_real(0) + math.pi/2
    ok = not (sympy_contains is S.true and sympy_residual != 0 and abs(oracle_residual) > 1e-12)
    detail = (
        f"shift={shift} sol={sol} witness={witness} contains={sympy_contains} "
        f"sympy_residual={sympy_residual} oracle_residual={oracle_residual}"
    )
    return ok, detail


@pytest.mark.parametrize("shift", CASES)
def test_sympy_correct(shift):
    ok, detail = check_case(shift)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for shift in CASES:
        ok, detail = check_case(shift)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")

