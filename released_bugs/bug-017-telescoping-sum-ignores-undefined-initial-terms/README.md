# Candidate Bug 17: infinite telescoping Sum ignores undefined initial terms and returns -1

**Status**

Confirmed

**SymPy version**

SymPy version: `1.14.0`

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

k = symbols("k", integer=True)
s = Sum(1/(k*(k - 1)), (k, 0, oo))
print("actual_sum =", s.doit())
print("first_terms =", [s.function.subs(k, i) for i in range(5)])
print("tail_sum_from_2 =", Sum(1/(k*(k - 1)), (k, 2, oo)).doit())
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
actual_sum = -1
first_terms = [zoo, zoo, 1/2, 1/6, 1/12]
tail_sum_from_2 = 1
```

**Expected output**

The sum from k = 0 to infinity should not evaluate to the finite value -1 because the terms at k = 0 and k = 1 are undefined.

**Why this is wrong**

The summand has poles at k = 0 and k = 1, so the requested infinite series is undefined in the ordinary sense. The well-defined tail from k = 2 to infinity sums to 1, not -1.

**Root cause**

The diagnosis locates the faulty telescoping path in `sympy/concrete/summations.py:1163-1171`, with endpoint construction in `telescopic_direct` at `summations.py:946-967` (endpoint `Add` at line 967). The code applies partial-fraction telescoping across singular starting terms without checking that the original summand is finite throughout the summation range; see `root_cause.md` for details.

**Independent verification**

`related_bugs.py` checks six shifted copies of the same telescoping pattern. For each case, a direct integer-denominator oracle finds division by zero in the first two terms, while SymPy returns the finite value -1.

**Additional instantiations**

The representative case plus five additional instantiations are covered as parametrized cases in `related_bugs.py` and mirrored in the PR regression test.

**Affected function or subsystem**

concrete / summation / convergence and singular terms; affected code: sympy/concrete/summations.py:1163-1171, sympy/concrete/summations.py:946-967.

**Severity**

High

**Suggested regression test**

```python
import pytest

from sympy import Sum, oo, symbols


@pytest.mark.parametrize("shift", [0, 1, 2, 3, 4, 5])
def test_telescoping_sum_does_not_ignore_undefined_initial_terms(shift):
    k = symbols("k", integer=True)
    expr = 1/((k - shift)*(k - shift - 1))
    result = Sum(expr, (k, shift, oo)).doit()
    assert result.is_finite is not True
```

**Confidence**

98%, because the wrong output reproduces on the pinned checkout, the source diagnosis identifies the responsible code path, and the independent checks confirm the expected mathematics.
