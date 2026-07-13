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

# Representative pair first, then five more jumps with the same boundary pattern.
CASES = [(0, 1), (2, 5), (-3, 7), (4, -2), (11, 13), (-8, -1)]


def check_case(left_value, default_value):
    x = symbols("x", real=True)
    p = Piecewise((left_value, x < 0), (default_value, True))
    got = limit(p, x, 0, dir="-")
    left_sample = p.subs(x, Rational(-1, 10))
    right_sample = p.subs(x, Rational(1, 10))
    ok = got == left_value
    detail = (
        f"left_value={left_value} default_value={default_value} "
        f"limit_dir_minus={got} left_sample={left_sample} right_sample={right_sample}"
    )
    return ok, detail


@pytest.mark.parametrize("left_value, default_value", CASES)
def test_sympy_correct(left_value, default_value):
    ok, detail = check_case(left_value, default_value)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for left_value, default_value in CASES:
        ok, detail = check_case(left_value, default_value)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
