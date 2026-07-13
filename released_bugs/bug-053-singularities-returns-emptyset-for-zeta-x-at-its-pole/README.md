### Candidate Bug 53: singularities returns EmptySet for zeta(x) although x = 1 is a pole

**Status**

Confirmed

**SymPy version**

SymPy version: `1.14.0`

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

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
from sympy.calculus.singularities import singularities

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
result = singularities(zeta(x), x, S.Complexes)
print("singularities(zeta(x), x, S.Complexes) =", result)
print("1 in result =", result.contains(S.One))
print("zeta(1) =", zeta(1))
print("limit(zeta(x), x, 1) =", limit(zeta(x), x, 1))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities(zeta(x), x, S.Complexes) = EmptySet
1 in result = False
zeta(1) = zoo
limit(zeta(x), x, 1) = zoo
```

**Expected output**

The singularity set should contain `1`; for `zeta(x)` over the complex plane the isolated pole is at `x = 1`.

**Why this is wrong**

The Riemann zeta function has a simple pole at `x = 1`. SymPy independently evaluates `zeta(1)` as `zoo` and `limit(zeta(x), x, 1)` as `zoo`, so returning `EmptySet` omits a confirmed singularity.

**Root cause**

The diagnosis localizes the omission to `sympy/calculus/singularities.py:94-108`. `singularities` scans negative powers and a short list of elementary functions, but it does not inspect special functions such as `zeta`; unsupported functions contribute nothing and the accumulator remains `EmptySet`. The `zeta` class itself records the pole behavior in `sympy/functions/special/zeta_functions.py:503-510`, where `zeta(1)` evaluates to complex infinity. See `root_cause.md` for the full call path and mechanism.

**Independent verification**

`related_bugs.py` checks the representative case and five shifted zeta arguments. It also uses high-precision `mpmath.zeta(1 + eps)`, whose magnitude blows up near the pole, as an independent numerical check that the omitted point is singular. On the buggy version it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The same omission is verified for `zeta(x + 1)`, `zeta(x + 2)`, `zeta(x - 1)`, `zeta(x + 3)`, and `zeta(x - 2)`, whose poles are respectively at `0`, `-1`, `2`, `-2`, and `3`.

**Affected function or subsystem**

calculus / singularities / special functions: `sympy/calculus/singularities.py:94-108`, with known pole behavior available in `sympy/functions/special/zeta_functions.py:503-510`.

**Severity**

Medium. SymPy returns a false complete singularity set for a standard special function, omitting a simple pole.

**Suggested regression test**

See `pr/tests/test_bug_053_singularities_returns_emptyset_for_zeta_x_although_x_1_is_a.py`. It is a single parametrized pytest test covering the representative case plus five shifted zeta arguments.

**Confidence**

98%. The mathematical pole is standard, SymPy confirms it through `zeta(1)` and `limit`, and the source diagnosis explains why `singularities` silently misses it.
