import cmath
import os
import sys


SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        def parametrize(self, *args, **kwargs):
            return lambda func: func

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()


print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

checkout_real = os.path.realpath(SYMPY_CHECKOUT_PATH)
sympy_file_real = os.path.realpath(sympy.__file__)
if not sympy_file_real.startswith(checkout_real + os.sep):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, followed by five additional instantiations.
CASES = [
    S.NegativeOne,
    S(-2),
    S(-3),
    Rational(-1, 2),
    S(-5),
    Rational(-7, 3),
]


def check_case(bad_value):
    """Return (ok, detail), where ok means SymPy does not include bad_value."""
    x = symbols("x")
    lhs = sqrt(1/x)
    rhs = 1/sqrt(x)
    sol = solveset(Eq(lhs, rhs), x, domain=S.Complexes)

    sympy_claims_solution = sol.contains(bad_value)
    sympy_residual = simplify((lhs - rhs).subs(x, bad_value))

    z = complex(float(bad_value), 0.0)
    reciprocal_z = complex(1.0 / float(bad_value), 0.0)
    oracle_lhs = cmath.sqrt(reciprocal_z)
    oracle_rhs = 1 / cmath.sqrt(z)
    oracle_residual = oracle_lhs - oracle_rhs
    oracle_rejects = abs(oracle_residual) > 1e-12

    ok = not (sympy_claims_solution is S.true and oracle_rejects)
    detail = (
        f"x={bad_value} sol={sol} contains={sympy_claims_solution} "
        f"sympy_residual={sympy_residual} "
        f"oracle_lhs={oracle_lhs} oracle_rhs={oracle_rhs} "
        f"oracle_residual={oracle_residual}"
    )
    return ok, detail


@pytest.mark.parametrize("bad_value", CASES)
def test_sympy_correct(bad_value):
    ok, detail = check_case(bad_value)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for bad_value in CASES:
        ok, detail = check_case(bad_value)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
