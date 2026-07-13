# right limit of digamma at zero returns zoo instead of negative infinity

## Summary

The order-zero polygamma is the digamma function. Near zero, psi(x) = -1/x - EulerGamma + O(x), so along x -> 0+ the values decrease without bound. Returning zoo loses the directional sign of a real pole.

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

x = symbols("x")

import mpmath as mp
mp.mp.dps = 80

expr = polygamma(0, x)
print("limit(polygamma(0, x), x, 0, dir='+') =", limit(expr, x, 0, dir="+"))
print("value at x=1/10**20 =", N(expr.subs(x, Rational(1, 10)**20), 80))
print("mpmath digamma(1e-20) =", mp.digamma(mp.mpf("1e-20")))
```

## Current behavior

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
limit(polygamma(0, x), x, 0, dir='+') = zoo
value at x=1/10**20 = -100000000000000000000.57721566490153286059006274941392016667755538996377930634212
mpmath digamma(1e-20) = -100000000000000000000.57721566490153286059006274941392016667755538996377930634212
```

## Expected behavior

limit(polygamma(0, x), x, 0, dir='+') = -oo

## Evidence

related_bugs.py evaluates positive rescalings polygamma(0, a*x) as x -> 0+ and compares nearby values with mpmath.digamma. The numerical samples are large negative real numbers, while SymPy reports zoo for the symbolic limits.

## Root cause summary

The source-level diagnosis locates the omission in sympy/functions/special/gamma_functions.py:790: polygamma._eval_as_leading_term() returns polygamma(0, x) unchanged instead of the finite-pole leading term -1/x. That makes leadterm/gruntz fail, after which sympy/series/limits.py falls back to evaluating polygamma(0, 0), which gamma_functions.py:677-678 represents as zoo. See root_cause.md for the full call path.

## Suggested regression test

Add `pr/tests/test_bug_059_right-limit-of-digamma-at-zero-returns-zoo-instead-of-negati.py`, which covers the representative case plus five additional instantiations.
