# Candidate Bug 2: solveset over Complexes claims sqrt(x**2) = x holds for every complex x

**Status**

Confirmed.

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

x = symbols("x")
eq = Eq(sqrt(x**2), x)
sol = solveset(eq, x, domain=S.Complexes)
print("solveset result:", sol)
print("residual at x = -1:", simplify(eq.lhs.subs(x, -1) - eq.rhs.subs(x, -1)))
print("numeric residual:", N(eq.lhs.subs(x, -1) - eq.rhs.subs(x, -1), 50))
```

**Actual output**

```text
solveset result: Complexes
residual at x = -1: 2
numeric residual: 2.0000000000000000000000000000000000000000000000000
```

**Expected output**

A proper subset of `Complexes`; at minimum it must exclude `x = -1`. Over the reals the solution is `Interval(0, oo)`.

**Why this is wrong**

The principal square root does not satisfy `sqrt(x**2) = x` for arbitrary complex `x`. At `x = -1`, the left side is `sqrt(1) = 1`, while the right side is `-1`.

**Root cause**

The diagnosis locates the immediate cause in `sympy/solvers/solveset.py:1094`, in `_solve_radical`. `unrad` turns the equation into the tautology `0 = 0`; `_solve_radical` then returns the non-finite set `Complexes` without validating it against the original branch-sensitive equation. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` tests the representative expression and five shifted variants `sqrt((x + a)**2) = x + a`. Each has an explicit negative-branch counterexample checked against Python `cmath.sqrt`.

**Additional instantiations**

The additional cases use `a` in `[1, 2, 3, 4, 5]` with counterexample `x = -a - 1`; these are included in `related_bugs.py` and the PR regression test.

**Affected function or subsystem**

`sympy/solvers/solveset.py:1094`, `_solve_radical`; subsystem `solvers.solveset / powers and radicals`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_002_solveset_over_complexes_claims_sqrt_x_2_x_holds_for_every_co.py`.

**Confidence**

99%. The solver returns all complex numbers while a single direct substitution gives a contradiction.
