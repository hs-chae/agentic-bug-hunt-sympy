import cmath
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.singularities import singularities

try:
    import pytest
except ModuleNotFoundError:
    class _Mark:
        @staticmethod
        def parametrize(*_args, **_kwargs):
            return lambda func: func

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")

# Representative case first, then five additional instantiations.
CASES = [
    ("x", x, S.One),
    ("x + 1", x + 1, S.Zero),
    ("x - 2", x - 2, S(3)),
    ("2*x", 2*x, S.Half),
    ("-x", -x, S.NegativeOne),
    ("x/3", x/3, S(3)),
]


def oracle_log_status():
    try:
        value = -cmath.log(1 - complex(1, 0))
    except ValueError as exc:
        return f"singular: -cmath.log(0) raises {type(exc).__name__}"
    return f"finite: {value}"


def check_case(label, arg, point):
    expr = polylog(1, arg)
    found = singularities(expr, x, S.Complexes)
    contains = found.contains(point) if hasattr(found, "contains") else S.false
    value_at_point = expr.subs(x, point)
    arg_at_point = arg.subs(x, point)

    expanded = expand_func(expr)
    expanded_found = singularities(expanded, x, S.Complexes)
    expanded_contains = expanded_found.contains(point)

    near_value = -cmath.log(1 - complex(1 - 1e-12, 0))
    oracle = oracle_log_status()
    ok = contains == S.true
    detail = (
        f"arg={label} point={point} found={found} contains={contains} "
        f"value_at_point={value_at_point} arg_at_point={arg_at_point} "
        f"expanded={expanded} expanded_singularities={expanded_found} "
        f"expanded_contains={expanded_contains} oracle={oracle} "
        f"near_-log(1-z)_at_z=1-1e-12={near_value}"
    )
    return ok, detail


@pytest.mark.parametrize(("label", "arg", "point"), CASES)
def test_sympy_correct(label, arg, point):
    ok, detail = check_case(label, arg, point)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for label, arg, point in CASES:
        ok, detail = check_case(label, arg, point)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
