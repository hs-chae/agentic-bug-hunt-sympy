import cmath
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Abs, I, N, Rational, sign

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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five additional non-real complex values.
CASES = [
    ("1 + I", 1 + I, complex(1, 1)),
    ("1 + 2*I", 1 + 2 * I, complex(1, 2)),
    ("2 + I", 2 + I, complex(2, 1)),
    ("-1 + I", -1 + I, complex(-1, 1)),
    ("2 - I", 2 - I, complex(2, -1)),
    ("3/5 + I/7", Rational(3, 5) + I / 7, complex(3 / 5, 1 / 7)),
]


def check_case(label, z, oracle_z):
    """Return (ok, detail), where ok means SymPy agrees with sign(z)=z/abs(z)."""
    actual = sign(z) ** 2
    definition_expected = z ** 2 / Abs(z) ** 2

    actual_numeric = complex(N(actual, 80))
    definition_numeric = complex(N(definition_expected, 80))
    oracle_numeric = (oracle_z / abs(oracle_z)) ** 2

    definition_ok = abs(definition_numeric - oracle_numeric) < 1e-45
    actual_ok = abs(actual_numeric - oracle_numeric) < 1e-45
    ok = definition_ok and actual_ok

    detail = (
        f"label={label} z={z} actual={actual} definition_expected={definition_expected} "
        f"actual_numeric={actual_numeric!r} definition_numeric={definition_numeric!r} "
        f"cmath_oracle={oracle_numeric!r}"
    )
    return ok, detail


@pytest.mark.parametrize("label,z,oracle_z", CASES)
def test_sympy_correct(label, z, oracle_z):
    ok, detail = check_case(label, z, oracle_z)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for label, z, oracle_z in CASES:
        ok, detail = check_case(label, z, oracle_z)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
