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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")
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
x = symbols("x")
CASES = [(I, "exp(2*I*x) would have to be 0"), (-I, "the inverse tangent is non-finite")]


def check_case(target, reason):
    sol = solveset(Eq(tan(x), target), x, domain=S.Complexes)
    has_infinity = "oo" in str(sol) or "zoo" in str(sol)
    ok = sol is S.EmptySet
    detail = f"target={target} sol={sol} reason={reason} has_infinity={has_infinity}"
    return ok, detail

@pytest.mark.parametrize("target,reason", CASES)
def test_sympy_correct(target, reason):
    ok, detail = check_case(target, reason)
    assert ok, detail

if __name__ == "__main__":
    failures=[]
    for case in CASES:
        ok, detail = check_case(*case)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
