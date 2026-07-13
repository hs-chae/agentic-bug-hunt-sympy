### Candidate Bug 38: integrate adds a spurious imaginary part to the divergent real integral of 1/Abs(x)

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

x = symbols("x", real=True)
val = integrate(1/Abs(x), (x, -1, 0))
print("integral =", val)
print("truncated eps=1/10:", integrate(1/Abs(x), (x, -1, -Rational(1, 10))))
print("truncated eps=1/100:", integrate(1/Abs(x), (x, -1, -Rational(1, 100))))

```

The same code is stored as `reproduce_bug.py`.

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
integral = oo + I*pi
truncated eps=1/10: log(10)
truncated eps=1/100: log(100)
```

**Expected output**

The improper real integral should diverge to positive real infinity, oo, with no imaginary I*pi term.

**Why this is wrong**

For x in [-1, 0), 1/Abs(x) = -1/x. The truncated integral from -1 to -epsilon is -log(epsilon), which tends to positive real infinity as epsilon -> 0+. The integrand is real and positive on the interval, so a finite imaginary component is mathematically spurious.

**Root cause**

The diagnosis locates the fault in endpoint evaluation through sympy/core/expr.py:_eval_interval, used by Piecewise._eval_interval. A finite endpoint is substituted into -log(x), keeping the principal-log constant -I*pi even though the real branch of the antiderivative on x < 0 should have no imaginary residue. See root_cause.md for details.

**Independent verification**

`related_bugs.py` is checkout-pinned, prints the SymPy environment, exercises the representative case plus five additional instantiations, and includes a direct-definition or high-precision numerical oracle. On the current buggy version it prints `Incorrect` and exits nonzero.

**Additional instantiations**

Five additional instantiations of the same error pattern are included as parametrized cases in `related_bugs.py` and mirrored in the single regression test under `pr/tests/`.

**Related issue**

This is a specific new instance of the already-reported defect in open issue sympy/sympy#23337, "Spurious I*pi in improper definite integral" (https://github.com/sympy/sympy/issues/23337). That issue describes the same root cause: a logarithmic antiderivative contributes a principal-log I*pi branch constant at a finite endpoint that fails to cancel during definite interval evaluation. This bug should be cross-referenced against #23337 rather than filed as fully novel.

**Affected function or subsystem**

sympy/core/expr.py:962-991 and sympy/functions/elementary/piecewise.py:454-582; _eval_interval / Piecewise interval evaluation

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_038_integrate-adds-a-spurious-imaginary-part-to-the-divergent-re.py`. It is a single parametrized pytest file using SymPy test-suite conventions: plain SymPy imports, no checkout path manipulation, and no environment prints.

**Confidence**

88%, because the reproducer gives a concrete wrong output, the verification file checks additional cases with an independent oracle, and the diagnosis report identifies the source-level mechanism.
