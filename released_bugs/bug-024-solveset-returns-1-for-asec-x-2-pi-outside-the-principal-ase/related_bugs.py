import cmath
import os
import sys

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
            return lambda func: func

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, -1, 3, 4, 5]


def oracle_asec(z):
    return cmath.acos(1/z)


def check_case(n):
    x = symbols("x")
    target = 2*pi*n
    eq = Eq(asec(x), target)
    sol = solveset(eq, x, domain=S.Complexes)
    bad = 1
    sympy_residual = simplify((eq.lhs - eq.rhs).subs(x, bad))
    oracle_residual = oracle_asec(complex(bad)) - complex(2*cmath.pi*n)
    ok = not (sol == FiniteSet(bad) and sympy_residual != 0 and abs(oracle_residual) > 1e-12)
    detail = f"n={n} sol={sol} bad={bad} sympy_residual={sympy_residual} oracle_residual={oracle_residual}"
    return ok, detail


@pytest.mark.parametrize("n", CASES)
def test_sympy_correct(n):
    ok, detail = check_case(n)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for n in CASES:
        ok, detail = check_case(n)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
