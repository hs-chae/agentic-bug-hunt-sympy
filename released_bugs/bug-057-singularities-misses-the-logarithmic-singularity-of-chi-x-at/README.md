# Candidate Bug 57: singularities misses the logarithmic singularity of Chi(x) at zero

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
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

import mpmath as mp
from sympy.calculus.singularities import singularities

mp.mp.dps = 50
x = symbols("x")
s = singularities(Chi(x), x, S.Complexes)
print("actual_singularities =", s)
print("expected_contains_zero =", s.contains(0))
print("Chi(0) =", Chi(0))
print("right_limit =", limit(Chi(x), x, 0, dir="+"))
print("mpmath_chi_1e_20 =", mp.chi(mp.mpf("1e-20")))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
actual_singularities = EmptySet
expected_contains_zero = False
Chi(0) = zoo
right_limit = -oo
mpmath_chi_1e_20 = -45.474486194979380819753317003604881720979845436636
```

**Expected output**

A set containing `0`, for example `{0}`.

**Why this is wrong**

The hyperbolic cosine integral has the local form Chi(x) = EulerGamma + log(x) + analytic terms near x = 0. The logarithm is singular at the origin; SymPy also evaluates `Chi(0)` to `zoo`.

**Root cause**

The diagnosis locates the limitation in `sympy/calculus/singularities.py:97-107`. The routine only scans explicit negative powers, logs, and a few inverse hyperbolic atoms, so opaque `Chi(x)` contributes no candidates even though `Chi._atzero` and `_eval_as_leading_term` in `sympy/functions/special/error_functions.py` expose the singularity. See `root_cause.md` for details.

**Independent verification**

`related_bugs.py` checks shifted cases `singularities(Chi(x - a), x, S.Complexes)` for `a = 0, 1, 2, 3, 4, 5` and samples high-precision `mpmath.chi(eps)`, which diverges downward as `eps -> 0+`. On the current buggy checkout it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The representative case plus five additional instantiations are covered as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_057_singularities_misses_the_logarithmic_singularity_of_chi_x_at.py`.

**Affected function or subsystem**

calculus / singularities / special functions; affected code: sympy/calculus/singularities.py:97-107, sympy/functions/special/error_functions.py:2286, sympy/functions/special/error_functions.py:2307-2320.

**Severity**

Medium

**Suggested regression test**

```python
import pytest

from sympy import Chi, S, singularities, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_singularities_chi_includes_logarithmic_origin(a):
    x = symbols("x")
    result = singularities(Chi(x - a), x, S.Complexes)
    assert result.contains(S(a)) is S.true
```

**Confidence**

93%, because the wrong output reproduces on the pinned checkout and the independent check confirms the mathematical expected behavior.
