# Candidate Bug 26: solveset returns a false solution for acot(x) = -pi/2

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, SymPy file `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

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

x = symbols("x")
sol = solveset(Eq(acot(x), -pi/2), x, S.Reals)
print("solution:", sol)
print("residual at 0:", simplify(acot(0) + pi/2))
print("acot(0):", acot(0))
```

**Actual output**

```text
solution: {0}
residual at 0: pi
acot(0): pi/2
```

**Expected output**

`EmptySet`.

**Why this is wrong**

SymPy's principal `acot` has `acot(0) = pi/2`. The equation asks for `acot(x) = -pi/2`, so substituting the returned value gives residual `pi`, not zero.

**Root cause**

The diagnosis locates the faulty inversion in `_invert_real` in `sympy/solvers/solveset.py:230-238`, together with `acot.inverse()` in `sympy/functions/elementary/trigonometric.py:2992-2996`. The solver applies `cot` to `-pi/2` without checking that `-pi/2` belongs to the principal real range of `acot`, then returns `0`. See `root_cause.md`.

**Independent verification**

`related_bugs.py` covers the representative equation and five shifted equations `acot(x - a) = -pi/2`. It compares the returned witness with SymPy's residual and an independent real principal-acot convention where `acot(0) = pi/2`.

**Additional instantiations**

Five additional shifted instances are included in `related_bugs.py` and mirrored in the proposed regression test.

**Affected function or subsystem**

`sympy.solvers.solveset._invert_real`, `sympy/solvers/solveset.py:230-238`; `acot.inverse`, `sympy/functions/elementary/trigonometric.py:2992-2996`.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_026_solveset_returns_0_for_acot_x_pi_2_although_acot_0_pi_2.py`.

**Confidence**

95%. The returned point directly fails substitution into the original equation.

