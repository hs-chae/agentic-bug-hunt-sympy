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

CASES = [3*pi/2, 5*pi/2, -3*pi/2, 7*pi/2, 11*pi/2, -5*pi/2]


def independent_acsc(z):
    return cmath.asin(1 / z)


def check_case(target):
    x = symbols("x")
    sol = solveset(Eq(acsc(x), target), x, S.Complexes)
    bad_details = []
    for candidate in sol:
        residual = simplify(acsc(candidate) - target)
        oracle_residual = independent_acsc(complex(N(candidate, 50))) - complex(N(target, 50))
        if residual != 0 and abs(oracle_residual) > 1e-12:
            bad_details.append(
                f"candidate={candidate} residual={residual} "
                f"numeric_residual={N(residual, 50)} oracle_residual={oracle_residual}"
            )
    ok = not bad_details
    detail = f"target={target} sol={sol} " + "; ".join(bad_details)
    return ok, detail


@pytest.mark.parametrize("target", CASES)
def test_sympy_correct(target):
    ok, detail = check_case(target)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for target in CASES:
        ok, detail = check_case(target)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
