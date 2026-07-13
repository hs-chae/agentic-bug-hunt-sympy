### Candidate Bug 37: integrate returns an antiderivative with the wrong sign for 1/(x*sqrt(x**2 - 1)) on negative reals

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
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if SYMPY_CHECKOUT_PATH and not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
integrand = 1/(x*sqrt(x**2 - 1))
F = integrate(integrand, x)
dF = diff(F, x)
print("antiderivative =", F)
print("derivative =", dF)
print("integrand at x=-3:", N(integrand.subs(x, -3), 50))
print("derivative at x=-3:", N(dF.subs(x, -3), 50))
print("difference:", N((dF - integrand).subs(x, -3), 50))

```

The same code is stored as `reproduce_bug.py`.

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
antiderivative = Piecewise((I*acosh(1/x), 1/Abs(x**2) > 1), (-asin(1/x), True))
derivative = Piecewise((-I/(x**2*sqrt(-1 + 1/x)*sqrt(1 + 1/x)), 1/Abs(x**2) > 1), (1/(x**2*sqrt(1 - 1/x**2)), True))
integrand at x=-3: -0.11785113019775792073347406035080817321413932294808
derivative at x=-3: 0.11785113019775792073347406035080817321413932294808
difference: 0.23570226039551584146694812070161634642827864589616
```

**Expected output**

The derivative of the returned antiderivative should equal 1/(x*sqrt(x**2 - 1)); at x=-3 it should be approximately -0.11785113019775792, not +0.11785113019775792.

**Why this is wrong**

An indefinite integral must differentiate back to the integrand on ordinary points of the branch. At x=-3 the integrand is a real negative number, while the derivative of SymPy's returned expression is the positive opposite. This is a concrete nonsingular real point, not an endpoint or pole.

**Root cause**

The diagnosis narrows the source to the Meijer-G indefinite integration path in sympy/integrals/meijerint.py:1653-1777. The rewrite/hyperexpand/unpolarify sequence returns a fallback -asin(1/x) branch that conflates x > 1 and x < -1, losing the negative-real sign. See root_cause.md for details.

**Independent verification**

`related_bugs.py` is checkout-pinned, prints the SymPy environment, exercises the representative case plus five additional instantiations, and includes a direct-definition or high-precision numerical oracle. On the current buggy version it prints `Incorrect` and exits nonzero.

**Additional instantiations**

Five additional instantiations of the same error pattern are included as parametrized cases in `related_bugs.py` and mirrored in the single regression test under `pr/tests/`.

**Affected function or subsystem**

sympy/integrals/meijerint.py:1653-1777; meijerint_indefinite branch handling

**Related issues**

This is a new instance of a known failure mode. The closest public precedents in the same `sqrt(x**2 - 1)` integration family are:

- sympy/sympy#20982 (closed): "integrate(1 / (x ** 2 * sqrt(x ** 2 - 1))) gives wrong integral (lost sign when x < 0)" — same negative-real sign-loss symptom on a sibling integrand. https://github.com/sympy/sympy/issues/20982
- sympy/sympy#23566 (open): "integrate(1/sqrt(x**2-1)) shouldn't be acosh(x)" — same Meijer-G `Piecewise(acosh, asin)` branch handling. https://github.com/sympy/sympy/issues/23566

No public issue or PR targets the exact `1/(x*sqrt(x**2 - 1))` indefinite integral having the wrong sign on negative reals, so this specific counterexample is new.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_037_integrate-returns-an-antiderivative-with-the-wrong-sign-for-.py`. It is a single parametrized pytest file using SymPy test-suite conventions: plain SymPy imports, no checkout path manipulation, and no environment prints.

**Confidence**

96%, because the reproducer gives a concrete wrong output, the verification file checks additional cases with an independent oracle, and the diagnosis report identifies the source-level mechanism.
