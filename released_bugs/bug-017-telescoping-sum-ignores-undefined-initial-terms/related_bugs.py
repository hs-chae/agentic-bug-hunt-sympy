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
        def parametrize(self, *args, **kwargs):
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

CASES = [0, 1, 2, 3, 4, 5]


def check_case(shift):
    k = symbols("k", integer=True)
    expr = 1/((k - shift)*(k - shift - 1))
    result = Sum(expr, (k, shift, oo)).doit()
    first_terms = [expr.subs(k, shift + i) for i in range(3)]
    tail = Sum(expr, (k, shift + 2, oo)).doit()

    undefined_indices = []
    for j in range(shift, shift + 3):
        denom = (j - shift)*(j - shift - 1)
        if denom == 0:
            undefined_indices.append(j)

    oracle_undefined = bool(undefined_indices)
    ok = not (oracle_undefined and result.is_finite is True)
    detail = (
        f"shift={shift} result={result} first_terms={first_terms} "
        f"undefined_indices={undefined_indices} tail_from_shift_plus_2={tail}"
    )
    return ok, detail


@pytest.mark.parametrize("shift", CASES)
def test_sympy_correct(shift):
    ok, detail = check_case(shift)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for shift in CASES:
        ok, detail = check_case(shift)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
