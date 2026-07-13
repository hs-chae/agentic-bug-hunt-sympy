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

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

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


# Representative shift first, then five additional shifts of the same zeta pole.
CASES = [0, 1, 2, -1, 3, -2]


def check_case(offset):
    x = symbols("x")
    expr = zeta(x + offset)
    pole = S.One - offset
    result = singularities(expr, x, S.Complexes)

    mpmath.mp.dps = 80
    eps = mpmath.mpf("1e-30")
    oracle_near_pole = mpmath.zeta(1 + eps)
    has_expected_pole = result.contains(pole) is S.true
    sympy_value_at_pole = expr.subs(x, pole)
    sympy_limit_at_pole = limit(expr, x, pole)
    ok = has_expected_pole
    detail = (
        f"offset={offset} expr={expr} pole={pole} singularities={result} "
        f"contains_pole={result.contains(pole)} value_at_pole={sympy_value_at_pole} "
        f"limit_at_pole={sympy_limit_at_pole} "
        f"mpmath_zeta_1_plus_eps_abs={abs(oracle_near_pole)}"
    )
    return ok, detail


@pytest.mark.parametrize("offset", CASES)
def test_sympy_correct(offset):
    ok, detail = check_case(offset)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for offset in CASES:
        ok, detail = check_case(offset)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
