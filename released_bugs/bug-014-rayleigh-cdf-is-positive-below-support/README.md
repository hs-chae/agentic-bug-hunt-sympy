# Candidate Bug 14: Rayleigh CDF is positive below support

## Status

Confirmed.

## SymPy version

- SymPy version: 1.14.0
- `SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`
- Commit hash: None

## Minimal reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *
from sympy.stats import P, Rayleigh, cdf

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

R = Rayleigh("R", 1)
print("cdf(R)(-1):", cdf(R)(-1))
print("P(R <= -1):", P(R <= -1))
print("expected cdf below support:", 0)
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
cdf(R)(-1): 1 - exp(-1/2)
P(R <= -1): 0
expected cdf below support: 0
incorrect: True
```

## Expected output

`cdf(R)(-1)` should be `0`. More generally, the Rayleigh CDF must be `0` for
every argument below the lower support endpoint `0`.

## Why this is wrong

The Rayleigh distribution has support `[0, oo)`. For any `z < 0`, the event
`R <= z` is empty because no Rayleigh-distributed value can be negative.
Therefore `F(z) = P(R <= z) = 0`. The expression `1 - exp(-z**2/(2*sigma**2))`
is the Rayleigh CDF only for `z >= 0`; extending it to negative `z` gives a
positive value that is not a probability of the distribution.

## Root cause

The diagnosis in `root_cause.md` identifies the source-level fault as
`RayleighDistribution` declaring nonnegative support while its custom `_cdf`
returns an unguarded formula. Source inspection locates this in
`sympy/stats/crv_types.py`: `RayleighDistribution.set = Interval(0, oo)` at
line 3798, but `_cdf` at lines 3808-3810 returns
`1 - exp(-(x**2/(2*sigma**2)))` without a `Piecewise` branch for `x < 0`.
`SingleContinuousDistribution.cdf` in `sympy/stats/crv.py` lines 205-211 uses a
non-`None` custom `_cdf` directly, bypassing the generic `compute_cdf` support
guard.

## Independent verification

`related_bugs.py` checks the representative case and five additional
instantiations. For each case it compares SymPy's CDF with an independent
piecewise Rayleigh CDF implementation: `0` below `0`, otherwise
`1 - exp(-z*z/(2*sigma*sigma))`. On every negative-support case, the independent
oracle returns `0` while SymPy returns a positive value. The script also prints
`P(R <= z)`, which returns `0` and demonstrates an internal inconsistency with
the direct `cdf` result.

## Additional instantiations

The verification and regression tests cover the representative case
`sigma = 1, z = -1` plus five additional cases: `(2, -1)`, `(1, -2)`,
`(3, -5)`, `(1/2, -1)`, and `(sqrt(2), -3)`.

## Affected function or subsystem

Stats / continuous distributions / Rayleigh CDF:
`sympy/stats/crv_types.py:3808-3810 RayleighDistribution._cdf`, together with
`sympy/stats/crv.py:205-211 SingleContinuousDistribution.cdf`.

## Severity

High. A CDF query returns a mathematically false positive probability below the
distribution support, and it contradicts SymPy's own probability query
`P(R <= z)`.

## Suggested regression test

The proposed regression test is in
`pr/tests/test_bug_014_rayleigh_cdf_is_positive_below_support.py`. It is a
single parametrized pytest test covering the representative case plus the five
additional instantiations.

## Confidence

95%. The support argument is definitive, the result is reproducible on the
local checkout, independent numerical checks agree with the expected value, and
the source-level path explains how the guard is bypassed.
