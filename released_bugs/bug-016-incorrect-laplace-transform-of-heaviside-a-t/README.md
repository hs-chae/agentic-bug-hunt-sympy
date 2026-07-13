# Candidate Bug 16: Laplace transform of Heaviside(a - t) uses the wrong cutoff

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

t = symbols("t", real=True)
s = symbols("s", positive=True)
a = symbols("a")

symbolic_transform = laplace_transform(Heaviside(a - t), t, s, noconds=True)
print(symbolic_transform)
print(symbolic_transform.subs(a, 2))
print(integrate(exp(-s*t), (t, 0, 2)))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
laplace_transform(Heaviside(a - t), t, s, noconds=False) = (exp(-a*s)/s, 0, (a > 0) & (a < 0) & Ne(1/a, 0))
laplace_transform(Heaviside(a - t), t, s, noconds=True) = exp(-a*s)/s
after substituting a = 2 = exp(-2*s)/s
direct integral from 0 to 2 = 1/s - exp(-2*s)/s
difference = -1/s + 2*exp(-2*s)/s
matches expected = False
```

**Expected output**

For `a = 2`, the transform should be `(1 - exp(-2*s))/s`, equivalently `1/s - exp(-2*s)/s`. For symbolic `a`, SymPy should preserve the condition distinguishing positive and negative `a` rather than returning an unconditional expression that specializes incorrectly.

**Why this is wrong**

For positive `a`, `Heaviside(a - t)` is one on `0 <= t < a` and zero for `t > a`; the endpoint value at `t = a` does not affect the integral. Therefore

```text
Laplace(Heaviside(a - t)) = integral_0^a exp(-s*t) dt = (1 - exp(-a*s))/s
```

for `a > 0` and `s > 0`. The returned `exp(-a*s)/s` is instead the transform of an opening step at `t = a`, not a window closing at `t = a`. Substituting `a = 2` gives a concrete contradiction with the defining integral.

**Root cause**

The diagnosis located the source-level cause in `sympy/integrals/laplace.py`. The Heaviside simple-rule table at `sympy/integrals/laplace.py:351-354` contains separate opening-step and closing-step rules, but the symbolic `Heaviside(a - t)` case falls through and later returns `(exp(-a*s)/s, 0, (a > 0) & (a < 0) & Ne(1/a, 0))`. `LaplaceTransform.doit` then drops the contradictory condition at `sympy/integrals/laplace.py:1317-1318` when `noconds=True`, exposing the wrong formula. See `root_cause.md` for the full call path and mechanism.

**Independent verification**

The file `related_bugs.py` compares SymPy's symbolic transform after substituting positive cutoffs against the direct formula `(1 - exp(-a*s))/s` and against an independent high-precision `mpmath` quadrature of `integral_0^a exp(-s*t) dt` at `s = 3/2`. On the current checkout, every case reports a nonzero symbolic and numerical discrepancy.

**Additional instantiations**

The merged verification file covers the representative cutoff plus five additional positive cutoffs:

```text
a = 2
a = 1
a = 3
a = 4
a = 5
a = 6
```

Each case uses the same symbolic transform first, then substitutes the positive cutoff.

**Affected function or subsystem**

`integrals / Laplace transform / Heaviside conditions`, specifically `sympy/integrals/laplace.py:351-354`, `sympy/integrals/laplace.py:1033-1042`, `sympy/integrals/laplace.py:1236-1241`, and `sympy/integrals/laplace.py:1317-1318`.

**Severity**

High

SymPy returns a mathematically false Laplace transform expression through a public API, and the wrong expression remains wrong under ordinary positive numeric specialization.

**Suggested regression test**

```python
import pytest

from sympy import Heaviside, exp, laplace_transform, simplify, symbols


@pytest.mark.parametrize("cutoff", [2, 1, 3, 4, 5, 6])
def test_laplace_transform_symbolic_heaviside_closing_step_after_substitution(cutoff):
    t = symbols("t", real=True)
    s = symbols("s", positive=True)
    a = symbols("a")

    symbolic_transform = laplace_transform(Heaviside(a - t), t, s, noconds=True)
    actual = symbolic_transform.subs(a, cutoff)
    expected = (1 - exp(-cutoff*s))/s

    assert simplify(actual - expected) == 0
```

This test is also provided at `pr/tests/test_bug_016_laplace_transform_of_heaviside_a_t_uses_the_wrong_cutoff.py`.

**Confidence**

90%. The wrong output is reproducible, the correct transform follows directly from the defining Laplace integral, and the diagnosis identifies the condition-dropping path that exposes the bad formula.
