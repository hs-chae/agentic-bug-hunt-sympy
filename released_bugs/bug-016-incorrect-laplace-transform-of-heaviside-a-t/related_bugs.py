import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath as mp
import sympy
from sympy import *  # noqa: F401,F403

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        def parametrize(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")


# Representative cutoff first, followed by five additional positive cutoffs.
CASES = [2, 1, 3, 4, 5, 6]


def independent_laplace_window(cutoff, s_value):
    """Integral of exp(-s*t) over 0 <= t <= cutoff, independent of SymPy."""
    mp.mp.dps = 80
    return mp.quad(lambda tau: mp.exp(-s_value*tau), [mp.mpf("0"), mp.mpf(cutoff)])


def check_case(cutoff):
    t = symbols("t", real=True)
    s = symbols("s", positive=True)
    a = symbols("a")

    symbolic_transform = laplace_transform(Heaviside(a - t), t, s, noconds=True)
    actual = symbolic_transform.subs(a, cutoff)
    expected = (1 - exp(-cutoff*s))/s

    symbolic_difference = simplify(actual - expected)

    s_value_sympy = Rational(3, 2)
    s_value_mp = mp.mpf(3) / 2
    actual_numeric = mp.mpf(str(N(actual.subs(s, s_value_sympy), 80)))
    oracle_numeric = independent_laplace_window(cutoff, s_value_mp)
    numeric_difference = actual_numeric - oracle_numeric

    ok = symbolic_difference == 0 and abs(numeric_difference) < mp.mpf("1e-60")
    detail = (
        f"cutoff={cutoff} symbolic_transform={symbolic_transform} "
        f"actual_after_substitution={actual} expected={expected} "
        f"symbolic_difference={symbolic_difference} "
        f"actual_numeric_at_s_3_2={actual_numeric} "
        f"independent_integral={oracle_numeric} "
        f"numeric_difference={numeric_difference}"
    )
    return ok, detail


@pytest.mark.parametrize("cutoff", CASES)
def test_sympy_correct(cutoff):
    ok, detail = check_case(cutoff)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for cutoff in CASES:
        ok, detail = check_case(cutoff)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
