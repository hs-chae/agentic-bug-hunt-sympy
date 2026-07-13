# Candidate Bug 18: sinh falsely evaluates a nonzero split imaginary-period argument to zero

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0.

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

**Minimal reproducer**

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

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
sinh(I*pi + I*(pi - 1)) = 0
sinh(I*(2*pi - 1)) = -I*sin(1)
difference = I*sin(1)
cmath expected = -0.8414709848078966j
```

**Expected output**

`sinh(I*pi + I*(pi - 1))` should equal `-I*sin(1)`, with numerical value about `-0.8414709848078965*I`.

**Why this is wrong**

The two arguments `I*pi + I*(pi - 1)` and `I*(2*pi - 1)` are algebraically identical. `sinh` is entire, so no branch convention can make the split expression zero while the combined expression is nonzero.

**Root cause**

The diagnosis located the source issue in `sinh.eval` in `sympy/functions/elementary/hyperbolic.py`, through `_peeloff_pi` in `sympy/functions/elementary/trigonometric.py:154-159`. _peeloff_pi in sympy/functions/elementary/trigonometric.py peels the pi coefficient out of the nested addend pi - 1 but drops the non-pi remainder -1. The hyperbolic evaluator rewrites sinh(I*pi + I*(pi - 1)) to I*sin(pi + (pi - 1)), and the dropped remainder makes sin see an apparent 2*pi. See `root_cause.md` for the full call path and mechanism.

**Independent verification**

`related_bugs.py` checks offsets 1 through 6. For each, Python `cmath` evaluates `sinh(1j*(2*pi - offset))`, while the exact identity gives `-I*sin(offset)`.

**Additional instantiations**

Offsets 2 through 6 are included in `related_bugs.py` and mirrored in the regression test.

**Affected function or subsystem**

`sinh.eval` in `sympy/functions/elementary/hyperbolic.py`, through `_peeloff_pi` in `sympy/functions/elementary/trigonometric.py:154-159`.

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_018_sinh_falsely_evaluates_a_nonzero_split_imaginary_period_argu.py`.

**Confidence**

98%. The mismatch is exact, numerically confirmed, and the source diagnosis explains the dropped additive remainder.
