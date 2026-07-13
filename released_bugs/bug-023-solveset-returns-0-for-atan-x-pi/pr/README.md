# Fix solveset false solution for solveset returns 0 for atan(x) = pi outside the principal atan range

## Summary

`solveset(Eq(atan(x), pi), x, domain=S.Complexes)` returns a set containing a value that does not satisfy the original equation. The solver is inverting a principal inverse function as if its elementary inverse were global.

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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
eq = Eq(atan(x), pi)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
for s in sol:
    print("residual at", s, "=", N(atan(s) - pi, 80))

```

## Expected behavior

EmptySet; the principal value atan(0) is 0, not pi.

## Evidence

The artifact's `related_bugs.py` covers the representative case and additional branch targets, using direct residual checks and independent `cmath` principal-value evaluation.

## Regression test

A single parametrized pytest file is included under `pr/tests/`.
