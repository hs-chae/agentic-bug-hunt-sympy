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

import math
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
from sympy.calculus.util import continuous_domain, function_range

CASES = [0, 1, 2, 3, 4, 5]


def check_case(a):
    x = symbols("x")
    expr = cos(x + a)/cot(x + a)
    dom = continuous_domain(expr, x, S.Reals)
    rng = function_range(expr, x, S.Reals)
    sample = pi/3 - a
    singular = pi/2 - a
    sample_value = expr.subs(x, sample)
    singular_value = expr.subs(x, singular)
    contains_sample = rng.contains(sample_value)
    oracle_sample = math.sin(math.pi/3)
    ok = not (dom == S.Reals and rng == FiniteSet(0) and contains_sample is S.false and abs(float(sample_value) - oracle_sample) < 1e-12)
    detail = (
        f"a={a} domain={dom} range={rng} sample={sample} sample_value={sample_value} "
        f"contains_sample={contains_sample} singular_value={singular_value} oracle_sample={oracle_sample}"
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
