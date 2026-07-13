import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath as mp
try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [1, 2, 3, 4, 5, 6]


def endpoint_partial_sum(a, terms):
    total = mp.mpf("0")
    for n in range(terms):
        total += 1/(mp.mpf(n) + a)
    return total


def near_one_partial_sum(a, q, terms):
    total = mp.mpf("0")
    power = mp.mpf("1")
    for n in range(terms):
        total += power/(mp.mpf(n) + a)
        power *= q
    return total


def check_case(a):
    x = symbols("x")
    expr = lerchphi(x, 1, a)
    got = limit(expr, x, 1, dir="-")
    mp.mp.dps = 50
    endpoint_lower_bound = endpoint_partial_sum(mp.mpf(a), 5000)
    near_one_value = near_one_partial_sum(mp.mpf(a), mp.mpf("0.9999"), 5000)
    ok = got == S.Infinity
    detail = (f"a={a} limit={got} expected=oo "
              f"endpoint_partial_sum_5000={endpoint_lower_bound} "
              f"near_one_partial_sum_q_0_9999={near_one_value}")
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
