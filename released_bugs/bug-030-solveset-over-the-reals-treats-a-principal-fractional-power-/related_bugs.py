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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [0, 1, 2, 3, 4, 5]


def principal_power(z, q):
    return cmath.exp(q * cmath.log(complex(z)))


def check_case(a):
    x = symbols("x")
    lhs = ((x + a)**2)**Rational(1, 3)
    rhs = (x + a)**Rational(2, 3)
    bad = -a - 1
    sol = solveset(Eq(lhs, rhs), x, domain=S.Reals)
    sympy_residual = N((lhs - rhs).subs(x, bad), 30)
    y = bad + a
    oracle_residual = principal_power(y*y, 1/3) - principal_power(y, 2/3)
    ok = not (sol.contains(bad) is S.true and abs(oracle_residual) > 1e-12)
    detail = (f"a={a} sol={sol} bad={bad} sympy_residual={sympy_residual} "
              f"oracle_residual={oracle_residual}")
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
