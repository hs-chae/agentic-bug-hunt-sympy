# Candidate Bug 47: linsolve misses the a = 0 branch of a*x - a = 0

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

x, a = symbols("x a")
sol = linsolve([a*x - a], [x])
print("solution:", sol)
print("equation at a=0, x=2:", (a*x - a).subs({a: 0, x: 2}))
print("reported contains x=2 after a=0:", (S(2),) in sol.subs(a, 0))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: {(1,)}
equation at a=0, x=2: 0
reported contains x=2 after a=0: False
```

**Expected output**

A conditional solution: x = 1 when a != 0, and all x when a = 0.

**Why this is wrong**

The equation is a*(x - 1) = 0. If a != 0 then x = 1, but if a = 0 the equation becomes 0 = 0 and every x is a solution.

**Root cause**

The diagnosis narrows the fault to the sparse linear-solver domain/RREF pipeline. _linsolve constructs the coefficient domain as the rational-function field ZZ(a), where a is treated as invertible, and sdm_irref divides by a. The returned generic solution x = 1 carries no a != 0 condition and misses the a = 0 branch. See `root_cause.md` for the full diagnosis.

**Independent verification**

Direct substitution with a = 0 and x = 2 gives 0, proving that the omitted branch contains values outside the returned {(1,)}. The runnable `related_bugs.py` checks the representative case plus five shifted or parameterized instantiations and exits with `Incorrect` on SymPy 1.14.0.

**Additional instantiations**

`related_bugs.py` and the PR regression test include 5 additional instantiations of the same error pattern, for 6 total parametrized cases.

**Related issue**

This is an instance of the known, long-standing symbolic-coefficient missing-`a=0`-branch problem tracked in open issue sympy/sympy#16861, "Proper solution of linear equations with symbolic coefficients" (https://github.com/sympy/sympy/issues/16861). That issue raises the same problem for `a*x = b` (this bug's `a*x - a` is the `b=a` case), notes the returned solutions "are not valid for a=0", and proposes a conditional `linsolve` variant that carries the `a=0` branch.

**Affected function or subsystem**

solvers.solveset / linear systems with symbolic parameters. Affected locations from diagnosis: sympy/polys/matrices/linsolve.py:120-136, sympy/polys/matrices/linsolve.py:86, sympy/solvers/solveset.py:3105-3108.

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_047_linsolve-misses-the-a-0-branch-of-a-x-a-0.py`. It is a single parametrized pytest file following SymPy test conventions.

**Confidence**

88%. The reproducer has a direct residual counterexample and the diagnosis identifies the source-level mechanism.
