# Candidate Bug 33: solveset represents the unsatisfiable equation tan(x) = I by infinities

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0; `SYMPY_CHECKOUT_PATH` supplied by the harness; observed `sympy.__file__` is `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`; Python executable `python3`.

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
eq = Eq(tan(x), I)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
print("contains finite 0?", sol.contains(0))
print("residual at 0 =", N(tan(0) - I, 80))

```

**Actual output**

```text
solution = ImageSet(Lambda(_n, _n*pi + oo*I), Integers)
contains finite 0? False
residual at 0 = -1.0*I
```

**Expected output**

EmptySet; tan(z) = I and tan(z) = -I have no finite complex solutions.

**Why this is wrong**

For finite z, tan(z) = -I*(exp(2*I*z)-1)/(exp(2*I*z)+1). The equations tan(z)=I and tan(z)=-I force exp(2*I*z) to be 0 or require an infinite exponential value, impossible for finite complex z. Using tan(z) = -I*(exp(2*I*z)-1)/(exp(2*I*z)+1), the equation tan(z)=I implies exp(2*I*z)=0, impossible for finite complex z. SymPy instead returns an ImageSet containing oo*I, which is not a finite complex solution.

**Root cause**

sympy/solvers/solveset.py:_invert_trig_hyp_complex, lines 467-473, inserts atan(a) into a periodic ImageSet without rejecting non-finite inverse values; atan(I) evaluates to oo*I. The full diagnosis, including call path and mechanism, is in `root_cause.md`.

**Independent verification**

`related_bugs.py` runs the representative case plus 1 additional instantiation(s) as parametrized cases and includes a direct independent mathematical check. On this checkout it prints mismatches and exits with `Incorrect`.

**Additional instantiations**

The parametrized cases are in `related_bugs.py` and mirrored in `pr/tests/test_bug_033_solveset_represents_the_unsatisfiable_equation_tan_x_i_by_in.py`.

**Affected function or subsystem**

solvers.solveset / trigonometric equations over Complexes; affected locations: sympy/solvers/solveset.py:467-473, sympy/functions/elementary/trigonometric.py:2681-2684.

**Severity**

Medium

**Suggested regression test**

Use `pr/tests/test_bug_033_solveset_represents_the_unsatisfiable_equation_tan_x_i_by_in.py`. It is a single parametrized pytest test covering the representative case and additional cases.

**Confidence**

93%, because direct evaluation, independent derivation, and source-level diagnosis agree.
