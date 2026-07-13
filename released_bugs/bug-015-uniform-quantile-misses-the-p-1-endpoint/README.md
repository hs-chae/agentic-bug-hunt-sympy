# Candidate Bug 15: Uniform quantile misses the p = 1 endpoint

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
from sympy import FiniteSet, S
from sympy.stats import P, Uniform, cdf, quantile

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

U = Uniform("U", 0, 1)
actual = quantile(U)(S.One)
expected = FiniteSet(S.One)

print('quantile(Uniform("U", 0, 1))(1) =', actual)
print('cdf(Uniform("U", 0, 1))(1) =', cdf(U)(S.One))
print("P(U <= 1) =", P(U <= 1))
print("expected p=1 quantile =", expected)
print("matches expected =", actual == expected)
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
quantile(Uniform("U", 0, 1))(1) = EmptySet
cdf(Uniform("U", 0, 1))(1) = 1
P(U <= 1) = 1
expected p=1 quantile = {1}
matches expected = False
```

**Expected output**

The `p = 1` quantile of `Uniform(0, 1)` should be the upper endpoint, returned consistently with the existing set-valued quantile API as `{1}`.

**Why this is wrong**

SymPy documents quantile as

```text
Q(p) = inf{x in (-oo, oo) : p <= F(x)}
```

For `U ~ Uniform(0, 1)`, the CDF is less than `1` for every `x < 1` and is exactly `1` at `x = 1`. Therefore the infimum of `{x : 1 <= F(x)}` is `1`. Returning `EmptySet` contradicts the documented definition and SymPy's own `cdf(U)(1) == 1` and `P(U <= 1) == 1` results.

**Root cause**

The diagnosis located the source-level cause in `sympy/stats/crv.py:285-291`, inside `SingleContinuousDistribution.compute_quantile`. The generic implementation computes a CDF expression and then solves `F(x) = p` over `self.set`; for `Uniform(0, 1)`, this produces `Intersection({_p}, Interval.Ropen(0, 1))`, so substituting `p = 1` drops the right endpoint. This equality-solving implementation does not implement the documented infimum definition in `sympy/stats/rv.py:1198-1203`; see `root_cause.md` for the full call path and mechanism.

**Independent verification**

The file `related_bugs.py` implements the Uniform CDF directly using rational arithmetic. For each interval `(a, b)`, it verifies that a point just below `b` has CDF less than `1`, while `b` itself has CDF exactly `1`; hence the definition gives `Q(1) = b`. On the current SymPy checkout, the same file reports `EmptySet` instead of `{b}` for all cases.

**Additional instantiations**

The merged verification file covers the representative interval plus five additional cases:

```text
Uniform(0, 1)
Uniform(-2, 3)
Uniform(2, 5)
Uniform(1/3, 7/3)
Uniform(-5/2, -1/2)
Uniform(-1, 0)
```

**Affected function or subsystem**

`stats / continuous distributions / quantile`, specifically `sympy/stats/crv.py:285-291` in `SingleContinuousDistribution.compute_quantile`, reached from the public `sympy.stats.quantile` API.

**Severity**

Medium

The result is mathematically false at an important endpoint of a basic continuous distribution, but it is localized to an endpoint case.

**Suggested regression test**

```python
import pytest

from sympy import FiniteSet, Rational, S
from sympy.stats import Uniform, quantile


@pytest.mark.parametrize(
    "name,a,b",
    [
        ("unit_interval", S.Zero, S.One),
        ("shifted_interval", S(-2), S(3)),
        ("positive_interval", S(2), S(5)),
        ("rational_interval", Rational(1, 3), Rational(7, 3)),
        ("negative_interval", Rational(-5, 2), Rational(-1, 2)),
        ("ending_at_zero", S(-1), S.Zero),
    ],
)
def test_uniform_quantile_at_one_returns_upper_endpoint(name, a, b):
    U = Uniform("U_" + name, a, b)
    assert quantile(U)(S.One) == FiniteSet(b)
```

This test is also provided at `pr/tests/test_bug_015_uniform_quantile_misses_the_p_1_endpoint.py`.

**Confidence**

90%. The reproducer is minimal, the endpoint result follows directly from the documented quantile definition, and the diagnosis identifies the exact generic equality-solving step that excludes the endpoint.
