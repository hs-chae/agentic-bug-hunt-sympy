# Candidate Bug 36: integrate returns an antiderivative with the wrong sign on the negative real branch

**Status**

Confirmed.

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, `sympy.__file__=$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)
import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
integrand = 1/(x*sqrt(x**2 + 1))
F = integrate(integrand, x)
dF = diff(F, x)
print("antiderivative:", F)
print("derivative:", dF)
print("integrand at x=-2:", N(integrand.subs(x, -2), 50))
print("derivative at x=-2:", N(dF.subs(x, -2), 50))
print("difference at x=-2:", N((dF - integrand).subs(x, -2), 50))
```

**Actual output**

```text
antiderivative: -asinh(1/x)
derivative: 1/(x**2*sqrt(1 + x**(-2)))
integrand at x=-2: -0.22360679774997896964091736687312762354406183596115
derivative at x=-2: 0.22360679774997896964091736687312762354406183596115
difference at x=-2: 0.44721359549995793928183473374625524708812367192231
```

**Expected output**

An antiderivative whose derivative equals `1/(x*sqrt(x**2 + 1))` on the negative real interval too, or a result carrying the necessary branch condition.

**Why this is wrong**

For `x < 0`, the integrand is negative. Differentiating SymPy's returned `-asinh(1/x)` gives `1/(x**2*sqrt(1 + x**(-2)))`, which is positive at `x = -2`. Therefore the returned expression is not a local antiderivative on that branch.

**Root cause**

The diagnosis narrows the cause to `sympy/integrals/meijerint.py:1736`, in `_meijerint_indefinite_1`. The Meijer integration path effectively uses a substitution through `x**2` while an odd factor `1/x` is present, then hyperexpands to a single expression valid on the positive branch without a sign or branch condition for negative `x`. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` differentiates the returned antiderivative and compares its value at `x = -2` with the original integrand and Python `math.sqrt` for six positive constants.

**Additional instantiations**

The same sign error appears for `1/(x*sqrt(x**2 + a))` with `a` in `[2, 3, 4, 5, 9]`, in addition to the representative `a = 1`.

**Affected function or subsystem**

`sympy/integrals/meijerint.py:1736`, `_meijerint_indefinite_1`; subsystem `integrals / branch cuts`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_036_integrate_returns_an_antiderivative_with_the_wrong_sign_on_t.py`.

**Confidence**

99%. Differentiating an indefinite integral must recover the integrand locally, but the derivative has the opposite sign at a regular negative real point.
