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
        @staticmethod
        def parametrize(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five additional instantiations.
CASES = [1, 2, 3, 4, 5, 6]


def check_case(a):
    """Return (ok, detail). ok is True iff every returned solution satisfies the
    original rational equations and the expected set is EmptySet."""
    x, y = symbols("x y")
    eqs = [(x*y - a*x)/(x - a) - y, y - a]
    sol = nonlinsolve(eqs, [x, y])

    invalid_details = []
    for candidate in sol:
        subs = {x: candidate[0], y: candidate[1]}
        residuals = [eq.subs(subs) for eq in eqs]
        denominator = (x - a).subs(subs)
        valid = denominator != 0 and all(res == 0 for res in residuals)
        if not valid:
            invalid_details.append((candidate, residuals, denominator))

    # Independent algebra: y = a from the second equation. Clearing the first
    # equation gives y = x, but that step requires x != a. Hence x = a is
    # forced and excluded, so there are no valid solutions.
    expected_empty_by_hand = True
    ok = sol == EmptySet and not invalid_details and expected_empty_by_hand
    detail = (
        f"a={a} sol={sol} invalid_details={invalid_details} "
        f"cleared_equation={expand((x*y - a*x) - y*(x - a))} "
        f"denominator=x-{a}"
    )
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
