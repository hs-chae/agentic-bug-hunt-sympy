### Candidate Bug 5: integrate(sqrt(x**2 + 1)/x, x) has the wrong derivative sign on negative reals

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: None

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

x = symbols("x")
integrand = sqrt(x**2 + 1)/x
F = integrate(integrand, x)
residual = diff(F, x) - integrand
print("antiderivative:", F)
print("integrand at -2:", integrand.subs(x, -2))
print("derivative at -2:", diff(F, x).subs(x, -2))
print("residual at -2:", simplify(residual.subs(x, -2)))
print("numeric residual:", N(residual.subs(x, -2), 50))

```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
antiderivative: x/sqrt(1 + x**(-2)) - asinh(1/x) + 1/(x*sqrt(1 + x**(-2)))
integrand at -2: -sqrt(5)/2
derivative at -2: sqrt(5)/2
residual at -2: sqrt(5)
numeric residual: 2.2360679774997896964091736687312762354406183596115
```

**Expected output**

The derivative of an antiderivative must equal sqrt(x**2 + 1)/x on every interval where the integrand is defined; at x=-2 it should be -sqrt(5)/2.

**Why this is wrong**

The returned antiderivative differentiates to the positive branch sqrt(1 + x**(-2)) on negative real x, but the original integrand equals -sqrt(1 + x**(-2)) there.

**Root cause**

The diagnosis locates the branch loss in the Meijer-G indefinite integration path around sympy/integrals/meijerint.py:1736. A rewrite through an x**2 argument and powdenest/unpolarification produces a formula valid on the positive branch but missing the sign(x) factor needed on negative reals. See `root_cause.md` for the full call path and source-level analysis.

**Independent verification**

`related_bugs.py` checks the representative case plus five additional instantiations. It also evaluates the critical point with an independent numerical oracle (`math`, `cmath`, or direct complex arithmetic as appropriate). On SymPy 1.14.0 it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The bundle uses `k = 5` additional instantiations, included as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_005_integrate-sqrt-x-2-1-x-x-has-the-wrong-derivative-sign-on-ne.py`.

**Affected function or subsystem**

integrals / indefinite integration / branch cuts; affected locations from diagnosis: sympy/integrals/meijerint.py:1736, sympy/integrals/integrals.py:1105.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_005_integrate-sqrt-x-2-1-x-x-has-the-wrong-derivative-sign-on-ne.py`.

**Confidence**

96%: the reproducer has an exact symbolic counterexample, a numerical cross-check, and a source-level diagnosis matching the observed failure.
