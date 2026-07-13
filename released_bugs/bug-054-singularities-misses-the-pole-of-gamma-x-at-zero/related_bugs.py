import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath
import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.singularities import singularities

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

mpmath.mp.dps = 80

CASES = [0, 1, 2, -1, 3, -2]


def check_case(shift):
    x = symbols("x")
    expr = gamma(x + shift)
    pole = -shift
    sings = singularities(expr, x, S.Complexes)
    eps = mpmath.mpf("1e-40")
    oracle_near_pole = mpmath.gamma(eps)
    ok = sings.contains(pole) == S.true
    detail = (
        f"shift={shift} expr={expr} singularities={sings} pole={pole} "
        f"contains={sings.contains(pole)} oracle_near_pole={oracle_near_pole}"
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
