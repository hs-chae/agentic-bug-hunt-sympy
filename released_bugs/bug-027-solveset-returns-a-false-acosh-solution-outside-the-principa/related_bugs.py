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
x = symbols("x")
CASES = [("2*pi*I", 2*pi*I, 1, complex(0, 2*cmath.pi)), ("-2*pi*I", -2*pi*I, 1, complex(0, -2*cmath.pi)), ("3*pi*I", 3*pi*I, -1, complex(0, 3*cmath.pi)), ("-3*pi*I", -3*pi*I, -1, complex(0, -3*cmath.pi)), ("4*pi*I", 4*pi*I, 1, complex(0, 4*cmath.pi)), ("-4*pi*I", -4*pi*I, 1, complex(0, -4*cmath.pi))]


def check_case(label, target, bad, target_complex):
    func = acosh
    sol = solveset(Eq(func(x), target), x, domain=S.Complexes)
    sympy_residual = simplify(func(bad) - target)
    oracle_residual = cmath.acosh(complex(bad)) - target_complex
    false_solution_returned = sol.contains(bad) is S.true and sympy_residual != 0
    ok = not false_solution_returned
    detail = (f"case={label} sol={sol} bad={bad} sympy_residual={sympy_residual} "
              f"oracle_residual={oracle_residual}")
    return ok, detail


@pytest.mark.parametrize("label,target,bad,target_complex", CASES)
def test_sympy_correct(label, target, bad, target_complex):
    ok, detail = check_case(label, target, bad, target_complex)
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
