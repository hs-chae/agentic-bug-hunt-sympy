### Candidate Bug 49: Matrix.solve methods return malformed results on singular systems

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, `sympy.__file__=$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Matrix

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

A = Matrix([[1, 1], [2, 2]])
b = Matrix([1, 2])

print("rank(A):", A.rank())
print("rank([A|b]):", A.row_join(b).rank())
print("gauss_jordan_solve:", A.gauss_jordan_solve(b))

for method in ["QR", "LDL", "CRAMER"]:
    try:
        sol = A.solve(b, method=method)
        print(method, sol, sol.shape)
    except Exception as exc:
        print(method, type(exc).__name__, exc)
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
rank(A): 1
rank([A|b]): 1
gauss_jordan_solve: (Matrix([
[1 - tau0],
[    tau0]]), Matrix([[tau0]]))
QR Matrix([[1]]) (1, 1)
LDL Matrix([[nan], [nan]]) (2, 1)
CRAMER Matrix([[nan], [nan]]) (2, 1)
```

**Expected output**

For `Matrix.solve`, these method-specific calls should reject the non-unique singular system, as the default `GJ` path does with `NonInvertibleMatrixError`, or otherwise return a documented valid solution representation. They must not return a one-entry vector for a two-unknown system, and must not return `nan` entries.

**Why this is wrong**

The system is

```text
x + y = 1
2*x + 2*y = 2
```

The second equation is exactly twice the first, so the solution set is infinite: `(x, y) = (1 - t, t)`. A one-entry matrix `Matrix([[1]])` cannot be a solution vector for a two-column coefficient matrix. `Matrix([[nan], [nan]])` is also not a solution, because substituting it into `A*x = b` gives `nan` residuals rather than zero.

**Root cause**

The diagnosis report identifies the public `Matrix.solve` dispatcher as sending method-specific calls directly to `QRsolve`, `LDLsolve`, and `cramer_solve` without the singularity and rank guard used by the `GJ`/`GE` path. In `sympy/matrices/solvers.py`, `_solve` checks `gauss_jordan_solve` for parameters at lines 827-838 but directly returns `M.QRsolve(rhs)`, `M.LDLsolve(rhs)`, and `M.cramer_solve(rhs)` at lines 844-851. `_QRsolve` then back-substitutes through the reduced `R` shape and returns a one-row matrix, `_LDLsolve` divides by a zero diagonal entry through `D.diagonal_solve`, and `_cramer_solve` divides by `det_M == 0` at line 774. See `root_cause.md` for the copied diagnosis.

**Independent verification**

`related_bugs.py` uses pure Python arithmetic as an independent oracle. For every case `A = [[1, 1], [a, a]]`, `b = [c, a*c]`, both `(c, 0)` and `(c - 7, 7)` have zero residual, so the system is consistent and non-unique. The script then checks the SymPy result from `QR`, `LDL`, and `CRAMER`: on SymPy 1.14.0, `QR` returns shape `(1, 1)`, while `LDL` and `CRAMER` return `nan` vectors.

**Additional instantiations**

The representative case is `(a, c) = (2, 1)`. Five additional instantiations are included in `related_bugs.py` and mirrored in `pr/tests/test_bug_049_matrix_solve_methods_return_malformed_results_on_singular_sy.py`: `(3, 1)`, `(2, 5)`, `(-1, 4)`, `(4, -2)`, and `(5, 3)`.

**Affected function or subsystem**

Matrices / linear solvers / singular systems. The relevant functions are `MatrixBase.solve` in `sympy/matrices/matrixbase.py:5192`, `_solve` in `sympy/matrices/solvers.py:778`, `_QRsolve` in `sympy/matrices/solvers.py`, `_LDLsolve` in `sympy/matrices/solvers.py:257`, and `_cramer_solve` in `sympy/matrices/solvers.py:711`.

**Severity**

Medium. The bug appears on singular non-unique systems with explicit method choices, but it returns invalid solver outputs rather than raising or giving a valid solution.

**Suggested regression test**

The proposed regression test is in `pr/tests/test_bug_049_matrix_solve_methods_return_malformed_results_on_singular_sy.py`. It is a single parametrized pytest file covering the representative case and five additional instantiations for `QR`, `LDL`, and `CRAMER`.

**Confidence**

95%. The system has a direct hand-derived infinite solution set, the malformed outputs are reproducible, and the source path explains why the guarded `GJ` behavior is bypassed.
