# Fix solveset returns 0 for atan2(x, 1) = pi over the reals

## Summary

SymPy currently returns a mathematically wrong result for `solveset(Eq(atan2(x, 1), pi), x, S.Reals)`. The attached regression test captures the representative case and five additional instances of the same pattern.

## Reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")


x = symbols("x")
eq = Eq(atan2(x, 1), pi)
sol = solveset(eq, x, S.Reals)
print("solveset(Eq(atan2(x, 1), pi), x, S.Reals) =", sol)
print("residual at returned value 0 =", (eq.lhs - eq.rhs).subs(x, 0))
print("atan2(0, 1) =", atan2(0, 1))
```

## Actual Behavior

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset(Eq(atan2(x, 1), pi), x, S.Reals) = {0}
residual at returned value 0 = -pi
atan2(0, 1) = 0
```

## Expected Behavior

EmptySet. For real x, atan2(x, 1) lies strictly between -pi/2 and pi/2.

## Evidence

The bundle's `related_bugs.py` includes direct residual, numerical, or definition-based evidence and fails on the current checkout with `Incorrect`.

## Suggested Regression Test

Add `pr/tests/test_bug_051_solveset-returns-0-for-atan2-x-1-pi-over-the-reals.py` to the appropriate SymPy test module, or move its parametrized test into the nearest existing test file for this subsystem.
