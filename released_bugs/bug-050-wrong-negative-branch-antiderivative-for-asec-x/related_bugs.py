import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import mpmath as mp
import sympy
from sympy import S, asec, diff, integrate, lambdify, simplify, symbols

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

mp.mp.dps = 80

# Representative case first, then five more negative real inputs on the same
# smooth branch x < -1.
CASES = [
    ("representative", S(-2), "-2"),
    ("negative_integer_3", S(-3), "-3"),
    ("negative_rational_3_over_2", -S(3) / 2, "-1.5"),
    ("negative_integer_4", S(-4), "-4"),
    ("negative_rational_5_over_2", -S(5) / 2, "-2.5"),
    ("negative_integer_10", S(-10), "-10"),
]


def check_case(label, exact_value, decimal_value):
    """Return (ok, detail), where ok means the antiderivative differentiates
    back to asec(x) both exactly and under an independent mpmath derivative.
    """
    x = symbols("x", real=True)
    primitive = integrate(asec(x), x)
    residual_expr = diff(primitive, x) - asec(x)
    exact_residual = simplify(residual_expr.subs(x, exact_value))

    f = lambdify(x, primitive, "mpmath")
    t = mp.mpf(decimal_value)
    numerical_residual = mp.diff(f, t) - mp.acos(1 / t)

    exact_ok = exact_residual == 0
    numerical_ok = abs(numerical_residual) < mp.mpf("1e-50")
    ok = exact_ok and numerical_ok
    detail = (
        f"{label}: x={exact_value}, primitive={primitive}, "
        f"exact_residual={exact_residual}, "
        f"mpmath_derivative_minus_asec={mp.nstr(numerical_residual, 60)}"
    )
    return ok, detail


@pytest.mark.parametrize("label, exact_value, decimal_value", CASES)
def test_sympy_correct(label, exact_value, decimal_value):
    ok, detail = check_case(label, exact_value, decimal_value)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for label, exact_value, decimal_value in CASES:
        ok, detail = check_case(label, exact_value, decimal_value)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
