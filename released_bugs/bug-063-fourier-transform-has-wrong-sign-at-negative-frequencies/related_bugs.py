import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath
try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*args, **kwargs):
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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

CASES = [S(-1) / 3, S(-1) / 4, S(-1) / 2, S(-2) / 3, S(-1), S(-3) / 2]

x, k = symbols("x k", real=True)
TRANSFORM = fourier_transform(cos(x) / (x**2 + 1), x, k)


def mp_value(q):
    return mpmath.mpf(q.p) / mpmath.mpf(q.q)


def shift_theorem_expected_sympy(value):
    return pi * (exp(-Abs(2*pi*value - 1)) + exp(-Abs(2*pi*value + 1))) / 2


def shift_theorem_expected_mpmath(value):
    kval = mp_value(value)
    return mpmath.pi * (
        mpmath.exp(-abs(2 * mpmath.pi * kval - 1))
        + mpmath.exp(-abs(2 * mpmath.pi * kval + 1))
    ) / 2


def check_case(value):
    got = TRANSFORM.subs(k, value)
    expected = shift_theorem_expected_sympy(value)
    oracle = shift_theorem_expected_mpmath(value)
    diff = N(got - expected, 80)
    oracle_error = abs(complex(N(got, 80)) - complex(oracle))
    evenness_diff = N(got - TRANSFORM.subs(k, -value), 80)
    ok = abs(complex(diff)) < 1e-40 and oracle_error < 1e-40
    detail = (
        f"k={value} sympy={N(got, 50)} expected={N(expected, 50)} "
        f"diff={diff} mpmath_shift_oracle={oracle} oracle_error={oracle_error} "
        f"evenness_diff={evenness_diff}"
    )
    return ok, detail


@pytest.mark.parametrize("value", CASES)
def test_sympy_correct(value):
    ok, detail = check_case(value)
    assert ok, detail


if __name__ == "__main__":
    print("transform:", TRANSFORM)
    failures = []
    for value in CASES:
        ok, detail = check_case(value)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
