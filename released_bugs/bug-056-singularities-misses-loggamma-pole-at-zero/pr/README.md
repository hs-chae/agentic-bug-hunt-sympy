# singularities returns EmptySet for loggamma(x) although x = 0 is singular

## Summary

This adds a regression test for `singularities(loggamma(x), x, S.Complexes)`. The current result is mathematically wrong:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities: EmptySet
contains 0: False
loggamma(0): oo
limit at 0: oo
```

## Reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

from sympy.calculus.singularities import singularities

x = symbols("x")
s = singularities(loggamma(x), x, S.Complexes)
print("singularities:", s)
print("contains 0:", s.contains(0))
print("loggamma(0):", loggamma(0))
print("limit at 0:", limit(loggamma(x), x, 0, dir="+"))
```

## Expected behavior

The singularity set should contain 0; more generally loggamma has singularities at the nonpositive integers.

## Evidence

loggamma(0) evaluates to oo and the right-hand limit at 0 is oo, so x = 0 is a singular point. Returning EmptySet falsely says there are no singularities.

The local artifact `related_bugs.py` covers the representative case plus five additional instantiations and performs the independent numerical or direct-definition check.

## Suggested regression test

Add `pr/tests/test_bug_056_singularities_returns_emptyset_for_loggamma_x_although_x_0_i.py` or equivalent coverage to SymPy's test suite.
