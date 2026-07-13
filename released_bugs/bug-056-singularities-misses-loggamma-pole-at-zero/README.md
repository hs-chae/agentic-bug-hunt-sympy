# Candidate Bug 56: singularities returns EmptySet for loggamma(x) although x = 0 is singular

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

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

from sympy.calculus.singularities import singularities

x = symbols("x")
s = singularities(loggamma(x), x, S.Complexes)
print("singularities:", s)
print("contains 0:", s.contains(0))
print("loggamma(0):", loggamma(0))
print("limit at 0:", limit(loggamma(x), x, 0, dir="+"))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities: EmptySet
contains 0: False
loggamma(0): oo
limit at 0: oo
```

**Expected output**

The singularity set should contain 0; more generally loggamma has singularities at the nonpositive integers.

**Why this is wrong**

loggamma(0) evaluates to oo and the right-hand limit at 0 is oo, so x = 0 is a singular point. Returning EmptySet falsely says there are no singularities.

**Root cause**

The source-level diagnosis locates the false negative in sympy/calculus/singularities.py around lines 94-108. The detector only scans selected structural forms such as negative powers and log atoms, and it has no branch or function hook for loggamma. Since loggamma(x) is not rewritten to log(gamma(x)), the initialized EmptySet is returned unchanged. See `root_cause.md` for the full call path and diagnosis.

**Independent verification**

`related_bugs.py` checks `loggamma(x - a)` for `a = 0, 1, 2, 3, 4, 5`. It uses `mpmath.log(mpmath.gamma(eps))` near `eps = 0+`, whose large value independently confirms the pole that the singularity detector misses. On the current buggy checkout it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The representative case plus five additional instantiations are covered as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_056_singularities_returns_emptyset_for_loggamma_x_although_x_0_i.py`.

**Affected function or subsystem**

calculus / singularities / special functions; affected code: sympy/calculus/singularities.py:94-108, sympy/functions/special/gamma_functions.py:979-984.

**Severity**

Medium

**Suggested regression test**

```python
import pytest

from sympy import S, loggamma, symbols
from sympy.calculus.singularities import singularities


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_singularities_loggamma_contains_shifted_zero(a):
    x = symbols("x")
    s = singularities(loggamma(x - a), x, S.Complexes)
    assert s.contains(a) is S.true
```

**Confidence**

92%, because the wrong output reproduces on the pinned checkout and the independent check gives the mathematically expected behavior.
