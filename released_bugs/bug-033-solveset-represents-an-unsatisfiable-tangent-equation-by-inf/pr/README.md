# Fix solveset represents the unsatisfiable equation tan(x) = I by infinities

## Summary

`solveset(Eq(tan(x), I), x, domain=S.Complexes)` produces an incorrect mathematical result on SymPy 1.14.0.

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
eq = Eq(tan(x), I)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
print("contains finite 0?", sol.contains(0))
print("residual at 0 =", N(tan(0) - I, 80))

```

## Expected behavior

EmptySet; tan(z) = I and tan(z) = -I have no finite complex solutions.

## Evidence

The artifact's `related_bugs.py` contains direct finite checks / branch checks and fails on the current checkout.

## Regression test

A single parametrized pytest file is included under `pr/tests/`.
