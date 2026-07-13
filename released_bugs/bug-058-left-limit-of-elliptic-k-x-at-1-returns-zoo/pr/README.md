# left limit of elliptic_k(x) at x = 1 returns zoo instead of positive infinity

## Summary

This adds a regression test for `limit(elliptic_k(x), x, 1, dir='-')`. The current result is mathematically wrong:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
sympy_limit = zoo
mpmath_ellipk_1_minus_1e_12 = 15.201804919087715174172185985894590732575028945707
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

import mpmath as mp

x = symbols("x")
print("sympy_limit =", limit(elliptic_k(x), x, 1, dir="-"))
mp.mp.dps = 50
print("mpmath_ellipk_1_minus_1e_12 =", mp.ellipk(1 - mp.mpf("1e-12")))
```

## Expected behavior

The left-hand real limit should be `oo`.

## Evidence

For real `m -> 1-`, the complete elliptic integral `K(m)` diverges through positive real values with logarithmic leading behavior. Returning unsigned complex infinity loses the directional real sign.

The local artifact `related_bugs.py` covers the representative case plus five additional instantiations and performs the independent numerical or direct-definition check.

## Suggested regression test

Add `pr/tests/test_bug_058_left_limit_of_elliptic_k_x_at_x_1_returns_zoo_instead_of_pos.py` or equivalent coverage to SymPy's test suite.
