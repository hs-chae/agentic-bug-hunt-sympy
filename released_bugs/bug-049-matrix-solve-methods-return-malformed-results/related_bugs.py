import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Matrix, S, simplify
from sympy.matrices.exceptions import NonInvertibleMatrixError

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

METHODS = ["QR", "LDL", "CRAMER"]

# Representative case first, then five additional instantiations of the same
# singular-but-consistent pattern:
#   A = [[1, 1], [a, a]], b = [c, a*c].
CASES = [
    (2, 1),
    (3, 1),
    (2, 5),
    (-1, 4),
    (4, -2),
    (5, 3),
]


def pure_python_residual(a, c, x0, x1):
    """Direct arithmetic oracle for A*x - b without using SymPy matrices."""
    return (x0 + x1 - c, a * x0 + a * x1 - a * c)


def has_nan(matrix):
    return any(entry is S.NaN or entry.has(S.NaN) for entry in matrix)


def check_case(a, c, method):
    A = Matrix([[1, 1], [a, a]])
    b = Matrix([c, a * c])

    # Independent evidence: two distinct exact solutions exist, so the system
    # is consistent and non-unique.
    oracle_residual_1 = pure_python_residual(a, c, c, 0)
    oracle_residual_2 = pure_python_residual(a, c, c - 7, 7)
    oracle_detail = (
        f"oracle_solutions=({c}, 0), ({c - 7}, 7); "
        f"oracle_residuals={oracle_residual_1}, {oracle_residual_2}"
    )
    if oracle_residual_1 != (0, 0) or oracle_residual_2 != (0, 0):
        return False, f"internal oracle error for a={a}, c={c}: {oracle_detail}"

    try:
        sol = A.solve(b, method=method)
    except NonInvertibleMatrixError as exc:
        return True, (
            f"a={a} c={c} method={method} correctly rejected non-unique "
            f"system with {type(exc).__name__}; {oracle_detail}"
        )
    except ValueError as exc:
        return True, (
            f"a={a} c={c} method={method} correctly rejected non-unique "
            f"system with {type(exc).__name__}; {oracle_detail}"
        )

    if getattr(sol, "shape", None) != (A.cols, b.cols):
        return False, (
            f"a={a} c={c} method={method} returned malformed shape "
            f"{getattr(sol, 'shape', None)}: sol={sol}; {oracle_detail}"
        )

    residual = A * sol - b
    ok = (not has_nan(sol)) and all(simplify(entry) == 0 for entry in residual)
    detail = (
        f"a={a} c={c} method={method} sol={sol} shape={sol.shape} "
        f"residual={residual}; {oracle_detail}"
    )
    return ok, detail


@pytest.mark.parametrize("a,c", CASES)
@pytest.mark.parametrize("method", METHODS)
def test_sympy_correct(a, c, method):
    ok, detail = check_case(a, c, method)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for a, c in CASES:
        for method in METHODS:
            ok, detail = check_case(a, c, method)
            print(detail)
            if not ok:
                failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
