# Candidate Bug 13: nonlinsolve returns a solution where the original rational equation is undefined

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

x, y = symbols("x y")
eqs = [(x*y - x)/(x - 1) - y, y - 1]
sol = nonlinsolve(eqs, [x, y])
print("nonlinsolve result =", sol)
for candidate in sol:
    print("residuals =", [eq.subs({x: candidate[0], y: candidate[1]}) for eq in eqs])
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
nonlinsolve result = {(1, 1)}
candidate = (1, 1)
residuals = [nan, 0]
direct left side at (1, 1) = nan
direct equation at (1, 1) = False
cleared numerator equation = -x + y
denominator at (1, 1) = 0
```

**Expected output**

The solution set should be `EmptySet`.

**Why this is wrong**

A point solves a rational equation only if all original denominators are nonzero. Substituting `(x, y) = (1, 1)` into `(x*y - x)/(x - 1) - y` gives `nan`, so it is not a solution.

Algebraically, the second equation forces `y = 1`. Multiplying the first equation by `x - 1` gives `y - x = 0`, but that multiplication is valid only under `x != 1`. Combining the cleared equation with `y = 1` forces exactly the excluded point `x = 1`, so no valid solution remains.

**Root cause**

The diagnosis located the fault in `sympy/solvers/solveset.py:4105-4108`, in `nonlinsolve`'s early return for a fully solved polynomial subsystem. The call path is `nonlinsolve` -> `_separate_poly_nonpoly` -> `_simple_dens` denominator recording -> numerator extraction -> `_handle_poly` -> the `if not remaining` return.

`_separate_poly_nonpoly` correctly records the denominator `x - 1`, then clears the rational equation to `-x + y`. `_handle_poly` solves the polynomial system and returns `(1, 1)`, but the `not remaining` path returns it directly as `FiniteSet(*map(to_tuple, poly_sol))`, bypassing the recorded denominator exclusions. See `root_cause.md` for the detailed trace.

**Independent verification**

`related_bugs.py` checks the returned solutions by direct substitution into the original rational equations and includes the hand algebra showing the expected set is empty. It covers the representative case plus five shifted systems.

**Additional instantiations**

The same pattern is tested for:

```text
[(x*y - a*x)/(x - a) - y, y - a]
```

with `a = 1, 2, 3, 4, 5, 6`. The representative case is `a = 1`; the other five are additional instantiations in both `related_bugs.py` and `pr/tests/test_bug_013_nonlinsolve_returns_a_solution_where_the_original_rational_e.py`.

**Affected function or subsystem**

Solvers / nonlinear systems. Located diagnosis: `sympy/solvers/solveset.py:4105-4108`, with denominator collection around `sympy/solvers/solveset.py:3782-3796`.

**Severity**

High. SymPy returns a concrete solution that makes the original equation undefined.

**Suggested regression test**

```python
import pytest

from sympy import EmptySet, nonlinsolve, symbols


@pytest.mark.parametrize("a", [1, 2, 3, 4, 5, 6])
def test_nonlinsolve_rejects_zero_denominator_solution(a):
    x, y = symbols("x y")
    eqs = [(x*y - a*x)/(x - a) - y, y - a]
    assert nonlinsolve(eqs, [x, y]) == EmptySet
```

**Confidence**

98%. Direct substitution shows the returned point is invalid, the hand derivation gives an empty solution set, and the diagnosis identifies the exact early return that bypasses denominator filtering.
