import os
import sys

import mpmath as mp

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        def parametrize(self, *args, **kwargs):
            return lambda func: func

    class _PytestFallback:
        mark = _Mark()

    pytest = _PytestFallback()

import sympy
from sympy import *  # noqa: F401,F403
from sympy.stats import P, Rayleigh, cdf


print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

checkout_real = os.path.realpath(SYMPY_CHECKOUT_PATH)
sympy_file_real = os.path.realpath(sympy.__file__)
if not sympy_file_real.startswith(checkout_real + os.sep):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

mp.mp.dps = 80

# Representative case first, followed by five additional instantiations.
CASES = [
    ("representative", S.One, S.NegativeOne),
    ("larger_scale", S(2), S.NegativeOne),
    ("farther_left", S.One, S(-2)),
    ("large_scale_far_left", S(3), S(-5)),
    ("small_scale", Rational(1, 2), S.NegativeOne),
    ("irrational_scale", sqrt(2), S(-3)),
]


def to_mpf(expr):
    return mp.mpf(str(N(expr, 80)))


def rayleigh_cdf_oracle(z_mpf, sigma_mpf):
    """Independent Rayleigh CDF formula with the support condition included."""
    if z_mpf < 0:
        return mp.mpf("0")
    return 1 - mp.exp(-(z_mpf * z_mpf) / (2 * sigma_mpf * sigma_mpf))


def check_case(label, sigma, z):
    """Return (ok, detail), where ok means SymPy's CDF obeys the support."""
    R = Rayleigh("R_" + label, sigma)
    actual_expr = cdf(R)(z)
    actual_mpf = to_mpf(actual_expr)
    oracle_mpf = rayleigh_cdf_oracle(to_mpf(z), to_mpf(sigma))
    probability = P(R <= z)
    mismatch = abs(actual_mpf - oracle_mpf) > mp.mpf("1e-60")

    detail = (
        f"case={label} sigma={sigma} z={z} "
        f"cdf_expr={actual_expr} cdf_numeric={mp.nstr(actual_mpf, 30)} "
        f"oracle_cdf={mp.nstr(oracle_mpf, 30)} P(R <= z)={probability}"
    )
    return not mismatch, detail


@pytest.mark.parametrize("label,sigma,z", CASES)
def test_sympy_correct(label, sigma, z):
    ok, detail = check_case(label, sigma, z)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for label, sigma, z in CASES:
        ok, detail = check_case(label, sigma, z)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
