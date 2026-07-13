# Candidate Bug 58: left limit of elliptic_k(x) at x = 1 returns zoo instead of positive infinity

**Status**

Confirmed

**SymPy version**

SymPy version: `1.14.0`

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

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
sympy_limit = zoo
mpmath_ellipk_1_minus_1e_12 = 15.201804919087715174172185985894590732575028945707
```

**Expected output**

The left-hand real limit should be `oo`.

**Why this is wrong**

For real `m -> 1-`, the complete elliptic integral `K(m)` diverges through positive real values with logarithmic leading behavior. Returning unsigned complex infinity loses the directional real sign.

**Root cause**

The diagnosis locates the missing branch-point expansion in `sympy/functions/special/elliptic_integrals.py` around lines 82-84. `elliptic_k._eval_nseries` delegates `elliptic_k(1 - w)` to a hypergeometric nseries that returns `nan`, so the limit machinery falls back to unsigned `zoo` instead of the positive logarithmic divergence. See `root_cause.md` for the full call path and source-level diagnosis.

**Independent verification**

`related_bugs.py` checks shifted left limits `limit(elliptic_k(x - a), x, a + 1, dir='-')` for `a = 0, 1, 2, 3, 4, 5` and compares with high-precision positive `mpmath.ellipk(1 - eps)` values. On the current buggy checkout it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The representative case plus five additional instantiations are covered as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_058_left_limit_of_elliptic_k_x_at_x_1_returns_zoo_instead_of_pos.py`.

**Affected function or subsystem**

series / limits / elliptic integrals; affected code: sympy/functions/special/elliptic_integrals.py:82-84.

**Severity**

Medium

**Suggested regression test**

```python
import pytest

from sympy import elliptic_k, limit, oo, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_left_limit_elliptic_k_at_one_is_positive_infinity(a):
    x = symbols("x")
    assert limit(elliptic_k(x - a), x, a + 1, dir="-") == oo
```

**Confidence**

90%, because the wrong output reproduces on the pinned checkout and the independent check confirms the mathematical expected behavior.
