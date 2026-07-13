# Candidate Bug 8: summation of k-weighted alternating binomial coefficients misses the n = 1 exception

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

n = symbols("n", integer=True, nonnegative=True)
k = symbols("k", integer=True)
closed = summation((-1)**k*k*binomial(n, k), (k, 0, n))
direct_n1 = sum(((-1)**j)*j*binomial(1, j) for j in range(0, 2))
print("closed form =", closed)
print("closed at n=1 =", closed.subs(n, 1))
print("direct finite sum at n=1 =", direct_n1)
print("difference =", closed.subs(n, 1) - direct_n1)

```

**Actual output**

```text
closed form = 0
closed at n=1 = 0
direct finite sum at n=1 = -1
difference = 1
```

**Expected output**

A conditional result with value -1 at n = 1 and 0 for n > 1.

**Why this is wrong**

Differentiating (1+t)^n gives sum k*C(n,k)*t^(k-1)=n*(1+t)^(n-1). At t=-1 this is 0 only for n>1; at n=1 the finite sum is -1. For n=1 the finite sum is 0*binomial(1,0) - 1*binomial(1,1) = -1. The identity sum (-1)^k k C(n,k)=0 follows from differentiating (1+t)^n at t=-1 and is valid only when n>1; the endpoint n=1 must be handled separately.

**Root cause**

sympy/concrete/gosper.py:214 uses a Gosper certificate with denominator n - 1 and simplifies the generic endpoint result to 0 before preserving the excluded parameter n = 1. The full diagnosis, including call path and mechanism, is in `root_cause.md`.

**Independent verification**

`related_bugs.py` runs the representative case plus 5 additional instantiation(s) as parametrized cases and includes a direct independent mathematical check. On this checkout it prints mismatches and exits with `Incorrect`.

**Additional instantiations**

The parametrized cases are in `related_bugs.py` and mirrored in `pr/tests/test_bug_008_summation_of_k_weighted_alternating_binomial_coefficients_mi.py`.

**Affected function or subsystem**

concrete summation / combinatorics; affected locations: sympy/concrete/gosper.py:214, sympy/concrete/summations.py:1236-1256.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_008_summation_of_k_weighted_alternating_binomial_coefficients_mi.py`. It is a single parametrized pytest test covering the representative case and additional cases.

**Confidence**

98%, because direct evaluation, independent derivation, and source-level diagnosis agree.
