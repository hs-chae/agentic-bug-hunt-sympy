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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")


import math
try:
    import pytest
except ModuleNotFoundError:
    class _DummyMark:
        def parametrize(self, *args, **kwargs):
            def decorate(func):
                return func
            return decorate

    class _DummyPytest:
        mark = _DummyMark()

    pytest = _DummyPytest()

x = symbols("x")

CASES = [
    (S.One, S.One, S.One),
    (S.One, S(2), S.One),
    (S(2), S.One, S.One),
    (Rational(1, 3), S.One, S.One),
    (-S.One, S.One, S.One),
    (S.One, S.One, -S.One),
]


def check_case(scale, denom, sign):
    rhs = sign*pi
    eq = Eq(atan2(scale*x, denom), rhs)
    sol = solveset(eq, x, S.Reals)
    residual_at_zero = (eq.lhs - eq.rhs).subs(x, 0)
    oracle_residual = math.atan2(float(scale)*0.0, float(denom)) - float(sign)*math.pi
    ok = sol == S.EmptySet
    detail = (
        f"scale={scale} denom={denom} rhs={rhs} sol={sol} "
        f"residual_at_zero={residual_at_zero} oracle_residual={oracle_residual}"
    )
    return ok, detail


@pytest.mark.parametrize("scale,denom,sign", CASES)
def test_sympy_correct(scale, denom, sign):
    ok, detail = check_case(scale, denom, sign)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for case in CASES:
        ok, detail = check_case(*case)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
