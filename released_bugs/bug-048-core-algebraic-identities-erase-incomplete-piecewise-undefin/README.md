# Candidate Bug 48: Core algebraic identities erase incomplete Piecewise undefined branches

**Status**

Confirmed.

**SymPy version**

SymPy version: 1.14.0

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: None available in the supplied checkout.

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Eq, Piecewise, symbols

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x", real=True)
p = Piecewise((1, x > 0))

print("p.subs(x, -1) =", p.subs(x, -1))
print("(p*0).subs(x, -1) =", (p * 0).subs(x, -1))
print("(p-p).subs(x, -1) =", (p - p).subs(x, -1))
print("Eq(p, p).subs(x, -1) =", Eq(p, p).subs(x, -1))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
p.subs(x, -1) = nan
(p*0).subs(x, -1) = 0
(p-p).subs(x, -1) = 0
Eq(p, p).subs(x, -1) = True
```

**Expected output**

The undefined/nan behavior should be preserved, or the identities should be withheld on the implicit undefined region. In particular, at `x = -1`, `p*0` and `p-p` should not become total `0`, and `Eq(p, p)` should not become unconditional `True`.

**Why this is wrong**

`Piecewise((1, x > 0))` has no branch covering `x <= 0`. SymPy itself treats that missing branch as undefined: `p.subs(x, -1)` returns `nan`.

The identities `z*0 = 0`, `z-z = 0`, and `z = z` are valid for ordinary finite values, but they are not valid pointwise where `z` is undefined. Since `p` is undefined at `x = -1`, simplifying these expressions to total values changes the domain and produces false information at a point where the original expression has no finite value.

**Root cause**

The source-level diagnosis in `root_cause.md` locates the responsible behavior in the generic core simplification layer. `sympy/core/mul.py:529-535` drops factors whose exponent is zero and related multiplication simplifications collapse `p*0` to `0`; `sympy/core/relational.py:625-634` uses structural equality through `is_eq` so `Eq(p, p)` becomes `True`. These rules do not ask whether an operand contains an incomplete `Piecewise` with an implicit `nan` region, even though `sympy/functions/elementary/piecewise.py:168-170` documents that missing branches evaluate to `nan`.

**Independent verification**

`related_bugs.py` implements a direct oracle for the incomplete piecewise function: return `a + 1` only when `x > a`, otherwise return Python `math.nan`. For `x = a - 1`, the oracle is undefined; Python `nan * 0` and `nan - nan` remain `nan`, and `nan == nan` is false. SymPy instead returns `0`, `0`, and `True` for the corresponding symbolic expressions.

**Additional instantiations**

Five additional shifted cases are included in `related_bugs.py` and mirrored in the proposed regression test: `Piecewise((a + 1, x > a))` evaluated at `x = a - 1` for `a = 1, 2, 3, 4, 5`.

**Affected function or subsystem**

Core algebra, `Piecewise`, and relational simplification. The diagnosis identifies `sympy/core/mul.py:529-535`, `sympy/core/relational.py:625-634`, and the missing-branch semantics documented in `sympy/functions/elementary/piecewise.py:168-170`.

**Severity**

Medium. SymPy returns mathematically false total values on an implicit undefined branch, but the trigger requires an incomplete `Piecewise`.

**Suggested regression test**

```python
import pytest

from sympy import Eq, Piecewise, S, symbols


@pytest.mark.parametrize("a", [0, 1, 2, 3, 4, 5])
def test_incomplete_piecewise_undefined_branch_survives_core_identities(a):
    x = symbols("x", real=True)
    p = Piecewise((a + 1, x > a))
    bad_point = a - 1

    assert p.subs(x, bad_point) is S.NaN
    assert (p * 0).subs(x, bad_point) is S.NaN
    assert (p - p).subs(x, bad_point) is S.NaN
    assert Eq(p, p).subs(x, bad_point) is not S.true
```

**Confidence**

90%. The result is directly reproducible, agrees with the documented missing-branch semantics of `Piecewise`, and is independently checked against an explicit undefined-value oracle.
