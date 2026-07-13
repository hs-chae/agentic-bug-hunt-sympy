### Candidate Bug 9: product returns 0 for a finite product containing an undefined factor

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

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
n = symbols("n")
term = sin(pi*n)/(n - 1)
print("term =", term)
print("product(term, (n, 0, 2)) =", product(term, (n, 0, 2)))
print("term values =", [term.subs(n, i) for i in [0, 1, 2]])
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
term = sin(pi*n)/(n - 1)
product(term, (n, 0, 2)) = 0
term values = [0, nan, 0]
```

**Expected output**

The finite product should be undefined/nan or remain unevaluated with the singular factor exposed.

**Why this is wrong**

The product contains the factor sin(pi)/(1 - 1) = 0/0 = nan. Zero factors at the endpoints do not make multiplication by an undefined factor well-defined.

**Root cause**

The diagnosis locates the fault in sympy/concrete/products.py:251-266. Product.doit replaces the index by an assumption-enriched integer dummy, which simplifies sin(pi*n) to 0 before _eval_product sees the denominator singularity at n = 1. See root_cause.md for the full source-level diagnosis.

**Independent verification**

`related_bugs.py` covers the representative case plus five shifted instantiations of the same error pattern. It also checks the singular value by direct substitution and with an independent numerical oracle (`cmath` or Python `math`) where applicable. On SymPy 1.14.0 it prints `Incorrect` and exits with status 1.

**Additional instantiations**

Five additional instantiations are included as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_009_product-returns-0-for-a-finite-product-containing-an-undefin.py`.

**Affected function or subsystem**

concrete products / finite products; affected locations from diagnosis: sympy/concrete/products.py:251-266, sympy/concrete/summations.py:1631-1659.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_009_product-returns-0-for-a-finite-product-containing-an-undefin.py`. It is a single parametrized pytest file following SymPy test conventions and covers the representative case plus the five additional instantiations.

**Confidence**

92%: the reproducer is minimal, the wrong output is deterministic, and the diagnosis identifies a concrete unguarded rewrite or predicate path.
