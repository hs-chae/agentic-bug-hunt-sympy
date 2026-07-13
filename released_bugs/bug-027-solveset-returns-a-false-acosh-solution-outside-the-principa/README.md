# Candidate Bug 27: solveset returns 1 for acosh(x) = 2*pi*I outside the principal acosh range

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
eq = Eq(acosh(x), 2*pi*I)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
for s in sol:
    print("residual at", s, "=", N(acosh(s) - 2*pi*I, 80))

```

**Actual output**

```text
solution = {1}
residual at 1 = -6.283185307179586476925286766559005768394338798750211641949889184615632812572418*I
```

**Expected output**

EmptySet; the principal value acosh(1) is 0, not 2*pi*I.

**Why this is wrong**

Principal acosh is not inverted globally by cosh. The target 2*pi*I is outside the principal value branch, so cosh(2*pi*I)=1 is only a solution of the composed equation. The principal acosh is not 2*pi*I at x=1; direct substitution gives acosh(1)=0. The numerical residual is -2*pi*I to 80 digits, so the returned set contains a false solution.

**Root cause**

sympy/solvers/solveset.py:_invert_complex, lines 550-557, maps targets through acosh(x).inverse() = cosh without preserving principal-branch range conditions. The full diagnosis, including call path and mechanism, is in `root_cause.md`.

**Independent verification**

`related_bugs.py` runs the representative case plus 5 additional instantiations. It substitutes SymPy's returned candidate into the original equation and compares the principal value against Python `cmath`; on this checkout it reports nonzero residuals and exits with `Incorrect`.

**Additional instantiations**

The parametrized cases are in `related_bugs.py` and mirrored in `pr/tests/test_bug_027_solveset_returns_1_for_acosh_x_2_pi_i_outside_the_principal_.py`.

**Affected function or subsystem**

solvers.solveset / inverse hyperbolic functions; affected locations: sympy/solvers/solveset.py:550-557, sympy/solvers/solveset.py:1313, sympy/functions/elementary/hyperbolic.py:1555.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_027_solveset_returns_1_for_acosh_x_2_pi_i_outside_the_principal_.py`. It asserts that `solveset` must not return the false candidate and that any returned candidate satisfies the original equation.

**Confidence**

96%, because direct substitution, high-precision residuals, independent principal-value evaluation, and source-level diagnosis all agree.
