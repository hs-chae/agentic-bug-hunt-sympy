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
        def parametrize(*args, **kwargs):
            return lambda func: func

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [2, 3, 4, 5, 6, 7]


def forward_terms(a, count=6):
    terms = [S(1), S(1)]
    for i in range(count - 2):
        terms.append((i + a)*terms[-1] - terms[-2])
    return terms


def check_case(a):
    n = symbols("n", integer=True)
    y = Function("y")
    rec = y(n + 2) - (n + a)*y(n + 1) + y(n)
    sol = rsolve(rec, y(n), {y(0): 1, y(1): 1})
    terms = forward_terms(a)
    ok = sol is not None and sol.subs(n, 0) == 1 and sol.subs(n, 1) == 1
    detail = (
        f"a={a} sol={sol} returned_y0={None if sol is None else sol.subs(n, 0)} "
        f"returned_y1={None if sol is None else sol.subs(n, 1)} "
        f"forward_terms={terms}"
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
