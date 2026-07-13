import cmath
import math
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import S, cos, sec, solveset, symbols

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

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five same-pattern instantiations.
# Each expression is nonzero_scale * sec(slope*x + offset).
CASES = [
    ("sec(x)", 1, 1, 0),
    ("sec(x + 1)", 1, 1, 1),
    ("sec(x - 2)", 1, 1, -2),
    ("sec(2*x)", 1, 2, 0),
    ("sec(3*x + 1)", 1, 3, 1),
    ("2*sec(x)", 2, 1, 0),
]


def _independent_value(scale, slope, offset, z):
    return scale / cmath.cos(slope * z + offset)


def check_case(label, scale, slope, offset):
    """Return (ok, detail), where ok means SymPy found no zero."""
    x = symbols("x")
    arg = slope * x + offset
    expr = scale * sec(arg)
    sol = solveset(expr, x, domain=S.Complexes)

    # A mathematically equivalent reciprocal spelling takes a different
    # SymPy path and returns the expected empty set on this version.
    reciprocal_sol = solveset(scale / cos(arg), x, domain=S.Complexes)

    # Independent numerical evidence: at a finite complex point away from
    # poles, sec is a finite reciprocal and not zero. At SymPy's reported
    # nan candidate, the independent value is also nan, not zero.
    sample = complex(0.375, -0.5)
    sample_value = _independent_value(scale, slope, offset, sample)
    nan_candidate = complex(math.nan, 0.0)
    nan_value = _independent_value(scale, slope, offset, nan_candidate)

    ok = sol == S.EmptySet
    detail = (
        f"{label}: solveset={sol}, expected=EmptySet, "
        f"reciprocal_solveset={reciprocal_sol}, "
        f"sample={sample}, independent_value={sample_value}, "
        f"nan_candidate_value={nan_value}"
    )
    return ok, detail


@pytest.mark.parametrize("label, scale, slope, offset", CASES)
def test_sympy_correct(label, scale, slope, offset):
    ok, detail = check_case(label, scale, slope, offset)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for case in CASES:
        ok, detail = check_case(*case)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
