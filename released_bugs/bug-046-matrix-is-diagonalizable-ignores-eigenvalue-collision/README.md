# Candidate Bug 46: Matrix.is_diagonalizable ignores eigenvalue-collision branch for a parametric matrix

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if SYMPY_CHECKOUT_PATH and not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

a, b = symbols("a b")
M = Matrix([[a, 1], [0, b]])
print("is_diagonalizable:", M.is_diagonalizable())
P, D = M.diagonalize()
print("P:", P)
print("D:", D)
M_equal = M.subs(b, a)
print("specialized matrix:", M_equal)
print("specialized is_diagonalizable:", M_equal.is_diagonalizable())
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
is_diagonalizable: True
P: Matrix([[1, -1/(a - b)], [0, 1]])
D: Matrix([[a, 0], [0, b]])
specialized matrix: Matrix([[a, 1], [0, a]])
specialized is_diagonalizable: False
```

**Expected output**

A conditional result, or refusal/qualification, because the matrix is diagonalizable when a != b but not diagonalizable when a = b.

**Why this is wrong**

When b = a, the matrix is [[a, 1], [0, a]], a nontrivial Jordan block. Its eigenspace has dimension 1 while the algebraic multiplicity is 2, so it is not diagonalizable.

**Root cause**

The diagnosis narrows the fault to the eigenvector/diagonalizability pipeline in sympy/matrices/eigen.py. _is_diagonalizable_with_eigen trusts eigenvects() as an unconditional decomposition and checks each symbolic eigenvalue key independently. It does not record the a != b condition introduced by the eigenvector denominator or split the branch where the eigenvalues collide. See `root_cause.md` for the full diagnosis.

**Independent verification**

For the specialized matrix [[a, c], [0, a]] with c != 0, M - aI has rank 1 and nullity 1, which is insufficient for diagonalization. The runnable `related_bugs.py` checks the representative case plus five shifted or parameterized instantiations and exits with `Incorrect` on SymPy 1.14.0.

**Additional instantiations**

`related_bugs.py` and the PR regression test include 5 additional instantiations of the same error pattern, for 6 total parametrized cases.

**Affected function or subsystem**

matrices / diagonalization and Jordan form for parametric matrices. Affected locations from diagnosis: sympy/matrices/eigen.py:451, sympy/matrices/eigen.py:453-458, sympy/matrices/eigen.py:696-714.

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_046_matrix-is-diagonalizable-ignores-eigenvalue-collision-branch.py`. It is a single parametrized pytest file following SymPy test conventions.

**Confidence**

95%. The reproducer has a direct residual counterexample and the diagnosis identifies the source-level mechanism.
