# Candidate Bug 31: solveset finds real solutions for acos(cos(x)) = -1 even though the left side is never negative

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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

u = symbols("u")
eq = Eq(acos(cos(u)), -1)
sol = solveset(eq, u, S.Reals)
print("solveset =", sol)
for value in [1, -1]:
    print(f"residual at {value} =", simplify(acos(cos(value)) + 1))
    print(f"numeric residual at {value} =", N(acos(cos(value)) + 1, 50))
print("sample value acos(cos(0)) =", acos(cos(0)))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset = Union(ImageSet(Lambda(_n, 2*_n*pi + 1), Integers), ImageSet(Lambda(_n, 2*_n*pi - 1 + 2*pi), Integers))
residual at 1 = 2
numeric residual at 1 = 2.0000000000000000000000000000000000000000000000000
residual at -1 = 2
numeric residual at -1 = 2.0000000000000000000000000000000000000000000000000
sample value acos(cos(0)) = 0
```

**Expected output**

EmptySet.

**Why this is wrong**

For real u, cos(u) lies in [-1, 1] and principal acos maps that interval into [0, pi]. Therefore acos(cos(u)) is never negative, so equality to -1 is impossible.

**Root cause**

_invert_real applies acos.inverse(), namely cos, to the target -1 before checking whether -1 lies in acos's principal real range [0, pi]. The later trig solver correctly solves the transformed equation but not the original one. See root_cause.md.

**Independent verification**

`related_bugs.py` exercises the representative case plus five additional instantiations and includes an independent numerical or definition-level oracle. On SymPy 1.14.0 it prints `Incorrect` and exits nonzero because the reported solution or membership result disagrees with direct substitution or the independent oracle.

**Additional instantiations**

The verification file and proposed regression test cover six total cases: the representative case and five additional instantiations of the same pattern.

**Affected function or subsystem**

solvers / solveset / trigonometric composition branch handling; affected locations from diagnosis: sympy/solvers/solveset.py:230, sympy/solvers/solveset.py:410.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_031_solveset-finds-real-solutions-for-acos-cos-x-1-even-though-t.py`. It is a single parametrized pytest covering the representative case plus five additional instantiations.

**Confidence**

97%, because the result is directly falsified by substitution or membership witnesses and the diagnosis identifies the source branch producing the bad output.
