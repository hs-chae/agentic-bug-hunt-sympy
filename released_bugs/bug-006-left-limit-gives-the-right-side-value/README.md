# Candidate Bug 6: left-hand limit of Piecewise jump returns right branch

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, `sympy.__file__=$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

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

x = symbols("x", real=True)
p = Piecewise((0, x < 0), (1, True))
print("limit(Piecewise((0, x < 0), (1, True)), x, 0, dir='-') =", limit(p, x, 0, dir="-"))
print("left sample p.subs(x, -1/10) =", p.subs(x, Rational(-1, 10)))
print("right sample p.subs(x, 1/10) =", p.subs(x, Rational(1, 10)))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
limit(Piecewise((0, x < 0), (1, True)), x, 0, dir='-') = 1
left sample p.subs(x, -1/10) = 0
right sample p.subs(x, 1/10) = 1
```

**Expected output**

The left-hand limit at `0` should be `0`.

**Why this is wrong**

For every sufficiently small negative real `x`, the condition `x < 0` is true, so the expression equals `0`. The one-sided limit from the left is therefore `0`. SymPy instead returns the default branch value at the boundary.

**Root cause**

The diagnosis locates the fault in `sympy/functions/elementary/piecewise.py`, `Piecewise._eval_as_leading_term`, lines 225-228. The method receives `cdir` but ignores it, substitutes the limit variable with `0` in conditions, and so skips the `x < 0` branch for a left-hand limit. See `root_cause.md` for the full call path.

**Independent verification**

`related_bugs.py` checks the representative case plus five constant jump variants. Each case directly samples the expression at `x = -1/10`, confirming the left branch value, and compares it with `limit(..., dir="-")`.

**Additional instantiations**

The five additional branch pairs are `(2, 5)`, `(-3, 7)`, `(4, -2)`, `(11, 13)`, and `(-8, -1)`.

**Affected function or subsystem**

`sympy/functions/elementary/piecewise.py:Piecewise._eval_as_leading_term`, line 225.

**Severity**

High. One-sided limits of discontinuous `Piecewise` expressions can return the value from the wrong side.

**Suggested regression test**

Use `pr/tests/test_bug_006_left_hand_limit_of_piecewise_jump_returns_right_branch.py`. It is a single parametrized pytest covering the representative case plus five additional jumps.

**Confidence**

97%. The left-neighborhood values are explicit constants, and the source-level diagnosis identifies the ignored direction parameter.
