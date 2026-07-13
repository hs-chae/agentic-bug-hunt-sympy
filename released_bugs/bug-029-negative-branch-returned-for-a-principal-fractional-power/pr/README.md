# PR draft: solveset over the reals returns a negative solution for principal x**(2/3) = 4

## Summary

This adds a regression test for a correctness bug in solvers.solveset / real-domain fractional powers. The current result is mathematically false under SymPy's documented expression semantics.

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
sol = solveset(Eq(x**Rational(2, 3), 4), x, S.Reals)
print("solution =", sol)
for s in sol:
    residual = (x**Rational(2, 3) - 4).subs(x, s)
    print("residual at", s, "=", simplify(residual))
    print("numeric residual at", s, "=", N(residual, 50))
```

## Actual behavior

solveset(Eq(x**Rational(2, 3), 4), x, S.Reals) returns {-8, 8}; substituting -8 gives -6 + 3.4641016151377546*I.

## Expected behavior

The real-domain solution set should be {8}; -8 is not a solution for SymPy principal powers.

## Evidence

The artifact's `related_bugs.py` checks the representative case plus five additional instantiations and compares against an independent oracle/direct finite computation. It fails on SymPy 1.14.0 with `Incorrect`.

## Suggested regression test

Add `pr/tests/test_bug_029_solveset-over-the-reals-returns-a-negative-solution-for-prin.py` to the appropriate SymPy test module, or adapt the parametrized test into the nearest existing subsystem test file.
