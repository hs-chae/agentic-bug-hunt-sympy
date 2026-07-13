# Candidate Bug 34: solveset says negative numbers satisfy sqrt(1/x) = 1/sqrt(x)

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

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
sol = solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, domain=S.Complexes)
print("solution:", sol)
print("contains -1:", sol.contains(S.NegativeOne))
print("lhs at -1:", sqrt(1/x).subs(x, -1))
print("rhs at -1:", (1/sqrt(x)).subs(x, -1))
print("residual at -1:", (sqrt(1/x) - 1/sqrt(x)).subs(x, -1))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: Complement(Complexes, {0})
contains -1: True
lhs at -1: I
rhs at -1: -I
residual at -1: 2*I
```

## Expected output

The returned solution set must not include negative real values. At minimum, `sol.contains(-1)` should be false. The correct complex-domain solution excludes `0` and the negative real axis.

## Why this is wrong

SymPy's `sqrt` is the principal square root. Principal square roots do not satisfy `sqrt(1/x) = 1/sqrt(x)` on the negative real branch cut. For `x = -1`, the left side is `sqrt(-1) = I`, while the right side is `1/sqrt(-1) = 1/I = -I`. The residual is therefore `2*I`, not zero, so `-1` is not a solution.

## Root cause

The diagnosis in `root_cause.md` locates the source-level fault in `sympy/solvers/solveset.py`, inside `_solve_radical` around lines 1090-1139. The call path is `solveset` -> `_solveset` -> `unrad` -> `_solve_radical`; `unrad` reduces the cleared radical equation to an identity, after which `_solve_radical` returns `Complement(Complexes, {0})`. Finite candidate sets are validated with `checksol`, but the broad infinite `Complement` is not rechecked against the original branch-sensitive equation, so the negative real axis remains incorrectly included.

## Independent verification

`related_bugs.py` checks the representative value and five additional negative real values. For each value it compares SymPy's returned set membership against a direct numerical evaluation using Python's independent `cmath.sqrt`, which uses the principal square-root branch. On every tested negative real value, the numerical residual is nonzero while SymPy claims the value is a solution.

## Additional instantiations

The verification and regression tests cover the representative case `x = -1` plus five additional invalid negative real values: `-2`, `-3`, `-1/2`, `-5`, and `-7/3`.

## Affected function or subsystem

Solvers / radical equation solving: `sympy/solvers/solveset.py`, `_solve_radical`, especially the complement/infinite-set handling around lines 1090-1139.

## Severity

High. SymPy returns a mathematically false solution set for a simple equation over `S.Complexes`, and direct substitution disproves the included solutions.

## Suggested regression test

The proposed regression test is in `pr/tests/test_bug_034_solveset_says_negative_numbers_satisfy_sqrt_1_x_1_sqrt_x.py`. It is a single parametrized pytest test covering the representative case plus the five additional negative-real instantiations.

## Confidence

94%. The result is contradicted by exact substitution and by an independent principal-square-root numerical oracle, and the source-level diagnosis identifies the unchecked infinite-set path that admits the invalid solutions.
