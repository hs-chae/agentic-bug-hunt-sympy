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

import mpmath as mp
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

mp.mp.dps = 80
CASES = [(S(1), "1"), (S(2), "2"), (S(3), "3"), (S.Half, "0.5"), (S(5), "5"), (3*S.Half, "1.5")]


def check_case(scale, scale_text):
    x = symbols("x", positive=True)
    actual = series(expint(2, scale*x), x, 0, 2)
    expected = 1 + scale*x*(log(scale*x) - 1 + EulerGamma) + O(x**2)
    symbolic_diff = simplify(actual.removeO() - expected.removeO())
    sample_x = mp.mpf("0.001")
    oracle = mp.expint(2, mp.mpf(scale_text)*sample_x)
    truncated = N(actual.removeO().subs(x, Rational(1, 1000)), 50)
    ok = symbolic_diff == 0
    detail = (
        f"scale={scale} series={actual} expected={expected} "
        f"diff={symbolic_diff} truncated_at_0.001={truncated} mpmath={oracle}"
    )
    return ok, detail


@pytest.mark.parametrize("scale,scale_text", CASES)
def test_sympy_correct(scale, scale_text):
    ok, detail = check_case(scale, scale_text)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for scale, scale_text in CASES:
        ok, detail = check_case(scale, scale_text)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
