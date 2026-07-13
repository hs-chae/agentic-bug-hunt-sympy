import os
import sys
import cmath

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
            def decorator(func):
                return func
            return decorator

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 6]

def check_case(a):
    u = symbols("u")
    target = -a
    sol = solveset(Eq(acos(cos(u)), target), u, S.Reals)
    sample = a
    sympy_residual = simplify(acos(cos(sample)) - target)
    oracle_value = cmath.acos(cmath.cos(sample)).real
    oracle_residual = oracle_value - target
    ok = (sol is S.EmptySet or sol == EmptySet)
    detail = f"a={a} sol={sol} expected=EmptySet sample={sample} residual={sympy_residual} oracle_residual={oracle_residual}"
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
