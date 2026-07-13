# Candidate Bug 59: right limit of digamma at zero returns zoo instead of negative infinity

## Status

Confirmed

## SymPy version

- SymPy version: 1.14.0
- SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`

## Minimal reproducer

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

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
limit(polygamma(0, x), x, 0, dir='+') = zoo
value at x=1/10**20 = -100000000000000000000.57721566490153286059006274941392016667755538996377930634212
mpmath digamma(1e-20) = -100000000000000000000.57721566490153286059006274941392016667755538996377930634212
```

## Expected output

limit(polygamma(0, x), x, 0, dir='+') = -oo

## Why this is wrong

The order-zero polygamma is the digamma function. Near zero, psi(x) = -1/x - EulerGamma + O(x), so along x -> 0+ the values decrease without bound. Returning zoo loses the directional sign of a real pole.

## Root cause

The source-level diagnosis locates the omission in sympy/functions/special/gamma_functions.py:790: polygamma._eval_as_leading_term() returns polygamma(0, x) unchanged instead of the finite-pole leading term -1/x. That makes leadterm/gruntz fail, after which sympy/series/limits.py falls back to evaluating polygamma(0, 0), which gamma_functions.py:677-678 represents as zoo. See root_cause.md for the full call path.

## Independent verification

related_bugs.py evaluates positive rescalings polygamma(0, a*x) as x -> 0+ and compares nearby values with mpmath.digamma. The numerical samples are large negative real numbers, while SymPy reports zoo for the symbolic limits.

## Additional instantiations

The verification and regression tests cover scale factors 1, 2, 3, 4, 5, and 6; scale 1 is the representative case and the other five are additional instantiations.

## Affected function or subsystem

series / limits / special functions / gamma functions. Affected locations from the diagnosis: sympy/functions/special/gamma_functions.py:790, sympy/series/limits.py:83-103, sympy/functions/special/gamma_functions.py:677-678.

## Severity

Medium

## Suggested regression test

Assert that right-hand limits of polygamma(0, a*x) at zero are S.NegativeInfinity for positive integer a.

The proposed pytest file is `pr/tests/test_bug_059_right-limit-of-digamma-at-zero-returns-zoo-instead-of-negati.py`.

## Confidence

96%. The reproducer is deterministic, independently checked numerically, and has a located source-level mechanism.
