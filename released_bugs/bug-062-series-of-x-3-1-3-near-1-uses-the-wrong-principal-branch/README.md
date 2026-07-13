# Candidate Bug 62: series of (x**3)**(1/3) near -1 uses the wrong principal branch

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

expr = (x**3)**Rational(1, 3)
ser = series(expr, x, -1, 2)
print("series((x**3)**(1/3), x, -1, 2) =", ser)
print("value at x=-9/10 =", N(expr.subs(x, Rational(-9, 10)), 80))
print("series polynomial at x=-9/10 =", N(ser.removeO().subs(x, Rational(-9, 10)), 80))
print("limit at x=-1 =", limit(expr, x, -1))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
series((x**3)**(1/3), x, -1, 2) = x
value at x=-9/10 = 0.45 + 0.77942286340599478208735085367764256512426236421467128262511314075336985760896002*I
series polynomial at x=-9/10 = -0.90000000000000000000000000000000000000000000000000000000000000000000000000000000
limit at x=-1 = exp(I*pi/3)
```

## Expected output

The expansion near x = -1 must use the principal cube-root branch, with center value exp(I*pi/3), not -1.

## Why this is wrong

For negative real x, x**3 is negative real and the principal cube root has argument pi/3. Thus (x**3)**(1/3) is complex near -1, while the returned series x is real and has center value -1.

## Root cause

The diagnosis identifies sympy/core/power.py:1500-1503. Pow._eval_nseries() calls powdenest(self, force=True).trigsimp(), which rewrites ((t - 1)**3)**(1/3) to t - 1 after shifting the expansion point. That denesting is invalid on the principal branch near the negative real axis, so the later series expands the wrong expression. See root_cause.md.

## Independent verification

related_bugs.py checks odd powers 3, 5, 7, 9, 11, and 13. For each, the returned series has center value -1, while the principal value is exp(I*pi/n), and Python complex powers agree with the complex principal value at nearby negative samples.

## Additional instantiations

The verification and regression tests cover odd powers 3, 5, 7, 9, 11, and 13; power 3 is the representative case and the other five are additional instantiations.

## Affected function or subsystem

series / powers / branch cuts. Affected locations from the diagnosis: sympy/core/power.py:1500-1503.

## Severity

Medium

## Suggested regression test

Assert that the series center value for (x**n)**(1/n) at x = -1 is exp(I*pi/n) for odd n.

The proposed pytest file is `pr/tests/test_bug_062_series-of-x-3-1-3-near-1-uses-the-wrong-principal-branch.py`.

## Confidence

95%. The reproducer is deterministic, independently checked numerically, and has a located source-level mechanism.
