import math
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Eq, Piecewise, S, symbols

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
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five additional instantiations.
CASES = [0, 1, 2, 3, 4, 5]


def independent_piecewise_value(a, point):
    if point > a:
        return float(a + 1)
    return math.nan


def check_case(a):
    """Return (ok, detail). ok is True iff undefined branches are preserved."""
    x = symbols("x", real=True)
    p = Piecewise((a + 1, x > a))
    bad_point = a - 1

    original = p.subs(x, bad_point)
    product = (p * 0).subs(x, bad_point)
    difference = (p - p).subs(x, bad_point)
    equality = Eq(p, p).subs(x, bad_point)

    oracle_original = independent_piecewise_value(a, bad_point)
    oracle_product = oracle_original * 0
    oracle_difference = oracle_original - oracle_original
    oracle_equality_is_true = oracle_original == oracle_original

    ok = (
        original is S.NaN
        and product is S.NaN
        and difference is S.NaN
        and equality is not S.true
        and math.isnan(oracle_original)
        and math.isnan(oracle_product)
        and math.isnan(oracle_difference)
        and not oracle_equality_is_true
    )
    detail = (
        f"a={a} bad_point={bad_point} original={original} product={product} "
        f"difference={difference} equality={equality} "
        f"oracle_original=nan oracle_product=nan oracle_difference=nan "
        f"oracle_equality_is_true={oracle_equality_is_true}"
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
