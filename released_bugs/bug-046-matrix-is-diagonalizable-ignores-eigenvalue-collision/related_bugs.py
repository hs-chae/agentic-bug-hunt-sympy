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

import cmath
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
a, b = symbols("a b")
CASES = [1, 2, 3, 4, 5, 6]

def check_case(offdiag):
    M = Matrix([[a, offdiag], [0, b]])
    generic = M.is_diagonalizable()
    specialized = M.subs(b, a)
    specialized_result = specialized.is_diagonalizable()
    eigenspace_dim = len((specialized - a*eye(2)).nullspace())
    ok = not (generic is True and specialized_result is False)
    return ok, f"offdiag={offdiag} generic={generic} specialized={specialized} specialized_result={specialized_result} eigenspace_dim={eigenspace_dim}"

@pytest.mark.parametrize("offdiag", CASES)
def test_sympy_correct(offdiag):
    ok, detail = check_case(offdiag)
    assert ok, detail

if __name__ == "__main__":
    failures = []
    for offdiag in CASES:
        ok, detail = check_case(offdiag)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
