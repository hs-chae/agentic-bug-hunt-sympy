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
# Representative m=2 first: x**(2/3) = m**2 should only have x=m**3.
CASES = [2, 3, 4, 5, 6, 7]


def check_case(m):
    x = symbols("x")
    rhs = Integer(m) ** 2
    sol = solveset(Eq(x**Rational(2, 3), rhs), x, S.Reals)
    bad = -Integer(m) ** 3
    good = Integer(m) ** 3
    sympy_residual = N((x**Rational(2, 3) - rhs).subs(x, bad), 80)
    oracle_residual = cmath.exp((2.0/3.0) * cmath.log(complex(int(bad)))) - complex(int(rhs))
    ok = (sol == FiniteSet(good)) and abs(complex(sympy_residual)) < 1e-40
    detail = (f"m={m} sol={sol} bad={bad} sympy_residual={sympy_residual} "
              f"oracle_residual={oracle_residual}")
    return ok, detail


@pytest.mark.parametrize("m", CASES)
def test_sympy_correct(m):
    ok, detail = check_case(m)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for m in CASES:
        ok, detail = check_case(m)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
