# Candidate Bug 3: solveset(sec(x), Complexes) returns nan as a zero

## Status

Confirmed.

## SymPy version

- SymPy version: `1.14.0`
- `SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`
- Commit hash: `None`

## Minimal reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import S, cos, sec, solveset, symbols

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
solution = solveset(sec(x), x, domain=S.Complexes)
print("solveset(sec(x), x, domain=S.Complexes) =", solution)
print("sec(nan) =", sec(S.NaN))
print("solveset(1/cos(x), x, domain=S.Complexes) =",
      solveset(1 / cos(x), x, domain=S.Complexes))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset(sec(x), x, domain=S.Complexes) = {nan}
sec(nan) = nan
solveset(1/cos(x), x, domain=S.Complexes) = EmptySet
```

## Expected output

```text
solveset(sec(x), x, domain=S.Complexes) = EmptySet
```

`nan` should never be returned as a solution.

## Why this is wrong

For finite complex `z`, `cos(z)` is finite, so `sec(z) = 1/cos(z)` can never
be equal to `0`. At zeros of `cos(z)`, `sec(z)` has a pole and is undefined or
infinite, not zero. SymPy's reported candidate is `nan`, and direct
substitution gives `sec(nan) = nan`, not `0`.

The equivalent spelling `solveset(1/cos(x), x, domain=S.Complexes)` returns
`EmptySet`, which matches the mathematical result.

## Root cause

The source-level diagnosis locates the bug in `sympy/solvers/solveset.py`.
The public call reaches `_solveset`, which calls `invert_complex(f, 0, symbol,
domain)` at lines 2321-2324. `invert_complex` delegates through
`_invert_complex` to `_invert_trig_hyp_complex`; lines 462-474 treat `sec`
like an ordinary invertible trigonometric function and apply `asec` to the
target value `0`.

For `sec(x) = 0`, this constructs solution families containing `asec(0)`.
In SymPy 1.14.0, `asec(0)` evaluates to `zoo`; arithmetic with that value
inside the image sets collapses to `{nan}`. The inversion code does not guard
against the missing range condition that `sec` and `csc` cannot take the value
`0`, and it does not filter non-finite or `nan` candidates. See
`root_cause.md` for the full call path.

## Independent verification

`related_bugs.py` checks the representative case and five
additional instantiations. It also evaluates the same functions with Python's
`cmath` at a finite complex sample, confirming they are ordinary finite
reciprocals rather than zeros, and evaluates SymPy's reported `nan` candidate
with the independent numeric path, which also produces `nan+nanj`.

Running the verification script on the current checkout prints:

```text
sec(x): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(0.9225238456811932-0.16780855829879304j), nan_candidate_value=(nan+nanj)
sec(x + 1): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(0.7090651450912302-1.6520902669055402j), nan_candidate_value=(nan+nanj)
sec(x - 2): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(-0.2225755988027718+1.8957248754716352j), nan_candidate_value=(nan+nanj)
sec(2*x): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(0.5891336769314588-0.41798941271747064j), nan_candidate_value=(nan+nanj)
sec(3*x + 1): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(-0.2573370886818409-0.37635596078739564j), nan_candidate_value=(nan+nanj)
2*sec(x): solveset={nan}, expected=EmptySet, reciprocal_solveset=EmptySet, sample=(0.375-0.5j), independent_value=(1.8450476913623863-0.3356171165975861j), nan_candidate_value=(nan+nanj)
Incorrect
```

## Additional instantiations

The runnable verification file and the proposed regression test cover the
representative case plus these five additional cases:

- `solveset(sec(x + 1), x, domain=S.Complexes)`
- `solveset(sec(x - 2), x, domain=S.Complexes)`
- `solveset(sec(2*x), x, domain=S.Complexes)`
- `solveset(sec(3*x + 1), x, domain=S.Complexes)`
- `solveset(2*sec(x), x, domain=S.Complexes)`

All currently return `{nan}` and should return `EmptySet`.

## Affected function or subsystem

Subsystem: solvers / trigonometric equations.

Affected source locations from the diagnosis:

- `sympy/solvers/solveset.py:462-474`
- `sympy/solvers/solveset.py:577-578`
- `sympy/solvers/solveset.py:2321-2324`

## Severity

High. SymPy returns a mathematically false solution set containing `nan` for
an equation with no complex solutions.

## Suggested regression test

```python
import pytest

from sympy import S, sec, solveset, symbols


@pytest.mark.parametrize(
    "scale, slope, offset",
    [
        (1, 1, 0),
        (1, 1, 1),
        (1, 1, -2),
        (1, 2, 0),
        (1, 3, 1),
        (2, 1, 0),
    ],
)
def test_solveset_sec_has_no_complex_zero(scale, slope, offset):
    x = symbols("x")
    assert solveset(scale * sec(slope * x + offset), x, domain=S.Complexes) == S.EmptySet
```

This test is also provided as
`pr/tests/test_bug_003_solveset_sec_x_complexes_returns_nan_as_a_zero.py`.

## Confidence

99%. The result is mathematically impossible, direct substitution rejects the
reported candidate, an equivalent reciprocal workflow returns `EmptySet`, and
the source-level diagnosis identifies the exact invalid inverse step.
