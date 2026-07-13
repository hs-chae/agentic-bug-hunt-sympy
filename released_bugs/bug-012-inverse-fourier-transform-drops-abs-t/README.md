### Candidate Bug 12: inverse_fourier_transform drops the absolute value in the Lorentzian transform pair

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

t, w = symbols("t w", real=True)
F = 2/(1 + 4*pi**2*w**2)
inv = inverse_fourier_transform(F, w, t)
print("inverse =", inv)
print("at t=-1:", inv.subs(t, -1))
print("expected at t=-1:", exp(-1))
print("difference:", simplify(inv.subs(t, -1) - exp(-1)))

```

The same code is stored as `reproduce_bug.py`.

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
inverse = exp(-t)
at t=-1: E
expected at t=-1: exp(-1)
difference: 2*sinh(1)
```

**Expected output**

inverse_fourier_transform(2/(1 + 4*pi**2*w**2), w, t) should be exp(-Abs(t)); at t=-1 it should be exp(-1), not E.

**Why this is wrong**

With SymPy's Fourier convention, the Fourier transform of exp(-Abs(t)) is 2/(1 + 4*pi**2*w**2). The inverse transform is therefore the even function exp(-Abs(t)). SymPy returns exp(-t), which agrees only for t >= 0 and is wrong on negative real t.

**Root cause**

The diagnosis locates the fault in sympy/integrals/transforms.py:_fourier_transform, especially lines 945-961. The transform integral returns a Piecewise branch valid only for t > 0; the wrapper selects that first branch and inverse_fourier_transform drops the condition under noconds=True, producing exp(-t) globally. See root_cause.md for the call path and mechanism.

**Independent verification**

`related_bugs.py` is checkout-pinned, prints the SymPy environment, exercises the representative case plus five additional instantiations, and includes a direct-definition or high-precision numerical oracle. On the current buggy version it prints `Incorrect` and exits nonzero.

**Additional instantiations**

Five additional instantiations of the same error pattern are included as parametrized cases in `related_bugs.py` and mirrored in the single regression test under `pr/tests/`.

**Affected function or subsystem**

sympy/integrals/transforms.py:945-961; _fourier_transform / inverse_fourier_transform

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_012_inverse-fourier-transform-drops-the-absolute-value-in-the-lo.py`. It is a single parametrized pytest file using SymPy test-suite conventions: plain SymPy imports, no checkout path manipulation, and no environment prints.

**Confidence**

98%, because the reproducer gives a concrete wrong output, the verification file checks additional cases with an independent oracle, and the diagnosis report identifies the source-level mechanism.
