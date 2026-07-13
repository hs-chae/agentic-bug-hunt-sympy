# Candidate Bug 20: density(given(Uniform(0, 1), U > 1/2)) has the wrong support and total mass

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0. Verified with `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, SymPy file `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *
from sympy.stats import Uniform, given, density, P

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
U = Uniform("U", 0, 1)
Y = given(U, U > S.Half)
d = density(Y)(x)
print("density:", d)
print("total mass:", integrate(d, (x, -oo, oo)))
print("mass below 1/2 from density:", integrate(d, (x, 0, S.Half)))
print("P(Y < 1/2):", P(Y < S.Half))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3

density: 2*Piecewise((1, (x >= 0) & (x <= 1)), (0, True))
total mass: 2
mass below 1/2 from density: 1
P(Y < 1/2): 0
```

**Expected output**

The conditional density of `U | U > 1/2` should be `2` on `[1/2, 1]` and `0` elsewhere. Its total mass should be `1`, and its mass below `1/2` should be `0`.

**Why this is wrong**

For `U ~ Uniform(0, 1)`, conditioning on `U > 1/2` restricts the support to `[1/2, 1]` and divides by `P(U > 1/2) = 1/2`. SymPy applies the normalization factor but keeps the unconditional support `[0, 1]`, so the returned density is not a probability density and contradicts `P(Y < 1/2) = 0`.

**Root cause**

The diagnosis located the source-level cause in `sympy/stats/crv.py`, especially `ContinuousPSpace.conditional_space` around lines 446-462 and `ContinuousPSpace.compute_density` around lines 333-340. `conditional_space` builds the correct `ConditionalContinuousDomain` and normalizer, but stores only `self.pdf / norm` as the new density. When `density(Y)` asks for the same variable, `compute_density` has no variables to marginalize, so the conditional domain is never applied to the returned density. See `root_cause.md` for the full call path and mechanism.

**Independent verification**

`related_bugs.py` checks the representative threshold plus five additional thresholds. For each threshold `t`, a direct oracle says the conditional density is `1/(1-t)` only for `t < x <= 1` and `0` below `t`; SymPy instead returns positive density below `t` and total mass greater than `1`.

**Additional instantiations**

The same error is exercised for `t = 1/3, 1/4, 2/3, 3/4, 1/5` in `related_bugs.py` and the proposed regression test.

**Affected function or subsystem**

`sympy.stats` conditional continuous random variables: `sympy/stats/crv.py:333-340` and `sympy/stats/crv.py:446-462`.

**Severity**

High. SymPy returns a mathematically invalid probability density with total mass greater than one.

**Suggested regression test**

See `pr/tests/test_bug_020_density_given_uniform_0_1_u_1_2_has_the_wrong_support_and_to.py`.

**Confidence**

98%. The returned density directly violates normalization and support, while SymPy's own conditional probability path gives the expected zero probability below the condition threshold.
