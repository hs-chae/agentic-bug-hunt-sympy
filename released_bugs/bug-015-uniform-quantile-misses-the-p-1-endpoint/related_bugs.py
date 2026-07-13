import os
import sys
from fractions import Fraction

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403
from sympy.stats import P, Uniform, cdf, quantile

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


# Representative case first, followed by five additional finite Uniform intervals.
CASES = [
    ("unit_interval", Fraction(0), Fraction(1)),
    ("shifted_interval", Fraction(-2), Fraction(3)),
    ("positive_interval", Fraction(2), Fraction(5)),
    ("rational_interval", Fraction(1, 3), Fraction(7, 3)),
    ("negative_interval", Fraction(-5, 2), Fraction(-1, 2)),
    ("ending_at_zero", Fraction(-1), Fraction(0)),
]


def as_sympy_number(value):
    return Rational(value.numerator, value.denominator)


def uniform_cdf_oracle(x, a, b):
    if x < a:
        return Fraction(0)
    if x >= b:
        return Fraction(1)
    return (x - a) / (b - a)


def oracle_quantile_at_one(a, b):
    below_endpoint = b - (b - a) / 10
    assert uniform_cdf_oracle(below_endpoint, a, b) < 1
    assert uniform_cdf_oracle(b, a, b) == 1
    return b


def check_case(label, a, b):
    sym_a = as_sympy_number(a)
    sym_b = as_sympy_number(b)
    U = Uniform("U_" + label, sym_a, sym_b)

    actual = quantile(U)(S.One)
    expected = FiniteSet(as_sympy_number(oracle_quantile_at_one(a, b)))

    sympy_cdf_at_upper = cdf(U)(sym_b)
    sympy_probability_at_upper = P(U <= sym_b)
    below_endpoint = b - (b - a) / 10
    oracle_below = uniform_cdf_oracle(below_endpoint, a, b)
    oracle_at_upper = uniform_cdf_oracle(b, a, b)

    ok = actual == expected
    detail = (
        f"{label}: interval=({sym_a}, {sym_b}) actual={actual} "
        f"expected={expected} sympy_cdf_at_upper={sympy_cdf_at_upper} "
        f"sympy_P_U_le_upper={sympy_probability_at_upper} "
        f"oracle_cdf_below={oracle_below} oracle_cdf_at_upper={oracle_at_upper}"
    )
    return ok, detail


@pytest.mark.parametrize("label,a,b", CASES)
def test_sympy_correct(label, a, b):
    ok, detail = check_case(label, a, b)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for label, a, b in CASES:
        ok, detail = check_case(label, a, b)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
