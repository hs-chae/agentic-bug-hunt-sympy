import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import S, integrate, oo, symbols
from sympy.stats import P, Uniform, density, given

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
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then five additional thresholds.
CASES = [S.Half, S(1) / 3, S(1) / 4, S(2) / 3, S(3) / 4, S(1) / 5]


def oracle_density_value(t, value):
    return S.One / (1 - t) if t < value <= 1 else S.Zero


def check_case(t):
    x = symbols("x")
    U = Uniform("U", 0, 1)
    Y = given(U, U > t)
    d = density(Y)(x)

    total_mass = integrate(d, (x, -oo, oo))
    density_mass_below = integrate(d, (x, 0, t))
    probability_below = P(Y < t)
    probe = t / 2
    sympy_value_below = d.subs(x, probe)
    oracle_value_below = oracle_density_value(t, probe)

    ok = (
        total_mass == 1
        and density_mass_below == 0
        and probability_below == 0
        and sympy_value_below == oracle_value_below
    )
    detail = (
        f"t={t} density={d} total_mass={total_mass} "
        f"density_mass_below={density_mass_below} P(Y<t)={probability_below} "
        f"value_at_{probe}={sympy_value_below} oracle_value={oracle_value_below}"
    )
    return ok, detail


@pytest.mark.parametrize("t", CASES)
def test_sympy_correct(t):
    ok, detail = check_case(t)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for t in CASES:
        ok, detail = check_case(t)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
