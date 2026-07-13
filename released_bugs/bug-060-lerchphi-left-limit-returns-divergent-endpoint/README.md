### Candidate Bug 60: left limit of lerchphi(x, 1, 1) at x = 1 returns an unevaluated divergent endpoint

**Status**

Confirmed

**SymPy version**

- SymPy version: 1.14.0
- SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`

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

x = symbols("x")

expr = lerchphi(x, 1, 1)
closed = -log(1 - x)/x
print("limit =", limit(expr, x, 1, dir="-"))
for v in [Rational(9, 10), Rational(999, 1000)]:
    print("sample", v, "lerchphi =", N(expr.subs(x, v), 50), "closed_form =", N(closed.subs(x, v), 50))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
limit = lerchphi(1, 1, 1)
sample 9/10 lerchphi = 2.5584278811044952044644349496492935640012238762542 closed_form = 2.5584278811044952044644349496492935640012238762542
sample 999/1000 lerchphi = 6.9146699489310681201741485125656582810843888547411 closed_form = 6.9146699489310681201741485125656582810843888547411
```

**Expected output**

oo. For 0 < x < 1, lerchphi(x, 1, 1) = sum_{n>=0} x**n/(n + 1) = -log(1 - x)/x, which diverges to +oo as x -> 1-.

**Why this is wrong**

The returned endpoint expression represents the divergent defining series at x = 1, not the left-hand limit. Applying expand_func first gives -log(1 - x)/x for the representative case, whose left limit at 1 is oo.

**Root cause**

The diagnosis locates the immediate wrong step in sympy/series/gruntz.py:mrv_leadterm, lines 520-538. Gruntz treats lerchphi(1 - 1/z, 1, 1) as having finite coefficient lerchphi(1, 1, 1) and exponent 0 instead of exposing the logarithmic divergence. See root_cause.md.

**Independent verification**

`related_bugs.py` runs the representative case plus five additional instantiations and includes an independent numerical/domain check for each case. On this checkout it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The verification and regression tests cover a = 1, 2, 3, 4, 5, and 6; a = 1 is the representative case and the other five are additional instantiations.

**Affected function or subsystem**

series / limits / special functions / Lerch transcendent. Affected locations from the diagnosis: sympy/series/gruntz.py:520-538, sympy/series/gruntz.py:465-468, sympy/functions/special/zeta_functions.py:131-178.

**Severity**

Medium

**Suggested regression test**

The proposed pytest file is `pr/tests/test_bug_060_left-limit-of-lerchphi-x-1-1-at-x-1-returns-an-unevaluated-d.py`; it contains one parametrized test covering the representative case plus the five additional instantiations.

**Confidence**

92%. The reproducer is deterministic, independently checked, and has a source-level diagnosis.
