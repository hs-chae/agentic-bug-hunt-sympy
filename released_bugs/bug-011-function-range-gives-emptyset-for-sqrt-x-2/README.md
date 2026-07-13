# Candidate Bug 11: function_range returns EmptySet for sqrt(x**2) over the reals

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
from sympy.calculus.util import function_range

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
r = function_range(sqrt(x**2), x, S.Reals)
print("range:", r)
print("values:", sqrt((-2)**2), sqrt(0**2), sqrt(3**2))
print("contains 0:", r.contains(0))
print("contains 2:", r.contains(2))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
range: EmptySet
values: 2 0 3
contains 0: False
contains 2: False
```

**Expected output**

`Interval(0, oo)`, because `sqrt(x**2) = Abs(x)` for real `x` and every nonnegative real value is attained.

**Why this is wrong**

For every real `x`, `sqrt(x**2)` equals `|x|`. Its range over the real line is `[0, infinity)`. SymPy returns `EmptySet`, which excludes directly attained values such as `0` at `x = 0` and `2` at `x = -2`.

**Root cause**

The diagnosis locates the cause in `sympy/calculus/util.py:253-281`, especially the critical-point search at line 260. `function_range` samples interval endpoint limits and points where `f.diff(x) == 0`, but it does not sample interior points where the derivative is undefined while the function remains continuous. For `sqrt(x**2)`, the minimum occurs at the cusp `x = 0`; missing that point leaves only infinite endpoint values and the constructed range collapses to `EmptySet`. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` compares SymPy's range with the direct real formula `sqrt((x + a)**2) = abs(x + a)` using Python `math.sqrt`, and checks concrete attained values for each shifted case.

**Additional instantiations**

The representative case plus five shifted cusp cases use `a` in `[0, 1, -1, 2, -2, 3]`. These are parametrized in `related_bugs.py` and the PR regression test.

**Affected function or subsystem**

`sympy/calculus/util.py:253-281`, `function_range`; critical-point search at line 260.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_011_function_range_returns_emptyset_for_sqrt_x_2_over_the_reals.py`.

**Confidence**

98%. The expected range follows immediately from the real identity `sqrt(y**2) = |y|`, and direct sample values contradict `EmptySet`.
