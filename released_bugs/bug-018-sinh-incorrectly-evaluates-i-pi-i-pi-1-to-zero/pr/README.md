# Fix sinh evaluation for split imaginary pi-period arguments

## Summary

The exact evaluator currently drops the non-pi remainder from a nested addend when reducing `sinh(I*pi + I*(pi - 1))`, producing zero for a nonzero value.

## Reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

import cmath
import math

expr = sinh(I*pi + I*(pi - 1))
combined = sinh(I*(2*pi - 1))
print("sinh(I*pi + I*(pi - 1)) =", expr)
print("sinh(I*(2*pi - 1)) =", combined)
print("difference =", simplify(expr - combined))
print("cmath expected =", cmath.sinh(1j*(2*math.pi - 1)))
```

## Actual behavior

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
sinh(I*pi + I*(pi - 1)) = 0
sinh(I*(2*pi - 1)) = -I*sin(1)
difference = I*sin(1)
cmath expected = -0.8414709848078966j
```

## Expected behavior

`sinh(I*pi + I*(pi - 1))` should equal `-I*sin(1)`, with numerical value about `-0.8414709848078965*I`.

## Evidence

`related_bugs.py` checks offsets 1 through 6. For each, Python `cmath` evaluates `sinh(1j*(2*pi - offset))`, while the exact identity gives `-I*sin(offset)`.

## Suggested regression test

Add `pr/tests/test_bug_018_sinh_falsely_evaluates_a_nonzero_split_imaginary_period_argu.py`, which parameterizes the representative case plus five additional instantiations.
