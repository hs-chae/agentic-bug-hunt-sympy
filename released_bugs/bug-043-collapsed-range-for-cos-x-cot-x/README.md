### Candidate Bug 43: function_range collapses cos(x)/cot(x) to {0} despite nonzero sampled values

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")
from sympy.calculus.util import continuous_domain, function_range

x = symbols("x")
expr = cos(x)/cot(x)
dom = continuous_domain(expr, x, S.Reals)
rng = function_range(expr, x, S.Reals)
print("continuous_domain(cos(x)/cot(x), x, S.Reals) =", dom)
print("function_range(cos(x)/cot(x), x, S.Reals) =", rng)
print("value at pi/3 =", expr.subs(x, pi/3))
print("range contains sqrt(3)/2 =", rng.contains(sqrt(3)/2))
print("value at pi/2 =", expr.subs(x, pi/2))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
continuous_domain(cos(x)/cot(x), x, S.Reals) = Reals
function_range(cos(x)/cot(x), x, S.Reals) = {0}
value at pi/3 = sqrt(3)/2
range contains sqrt(3)/2 = False
value at pi/2 = nan
```

**Expected output**

The real domain should exclude points where cot(x) is undefined or zero, and the range should include values such as sqrt(3)/2.

**Why this is wrong**

Where the quotient is defined, cos(x)/cot(x) equals sin(x). At x = pi/3 this value is sqrt(3)/2, so the range cannot be {0}; x = pi/2 is undefined.

**Root cause**

The diagnosis locates coupled faults in sympy/calculus/singularities.py:95-102 and sympy/calculus/util.py:223-281. singularities rewrites cot through cos/sin and loses the denominator condition cot(x) = 0, then function_range trusts the full real domain and samples a closed period whose endpoints are both 0. See root_cause.md for the full source-level diagnosis.

**Independent verification**

`related_bugs.py` covers the representative case plus five shifted instantiations of the same error pattern. It also checks the singular value by direct substitution and with an independent numerical oracle (`cmath` or Python `math`) where applicable. On SymPy 1.14.0 it prints `Incorrect` and exits with status 1.

**Additional instantiations**

Five additional instantiations are included as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_043_function-range-collapses-cos-x-cot-x-to-0-despite-nonzero-sa.py`.

**Affected function or subsystem**

calculus / continuous_domain and function_range; affected locations from diagnosis: sympy/calculus/singularities.py:95-102, sympy/calculus/util.py:223-281.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_043_function-range-collapses-cos-x-cot-x-to-0-despite-nonzero-sa.py`. It is a single parametrized pytest file following SymPy test conventions and covers the representative case plus the five additional instantiations.

**Confidence**

97%: the reproducer is minimal, the wrong output is deterministic, and the diagnosis identifies a concrete unguarded rewrite or predicate path.
