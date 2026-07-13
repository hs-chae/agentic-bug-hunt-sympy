---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:1090
---

## Candidate Summary

`solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, S.Complexes)` returns `Complement(Complexes, {0})`, but `x = -1` is not a solution because the two principal square roots are `I` and `-I`.

## Call Path

`solveset` turns the equation into `sqrt(1/x) - 1/sqrt(x)`. Direct inversion fails, then `_solveset` calls `unrad` and `_solve_radical`. After denominator clearing, `unrad` reduces the numerator `sqrt(x)*sqrt(1/x) - 1` to `(0, [])`.

`_solve_radical` solves the radical-free identity as all complex numbers and subtracts denominator singularities, producing `Complexes \ {0}`.

## Root Cause

The source-level fault is the unchecked infinite-set handling in `sympy/solvers/solveset.py`, `_solve_radical`, lines 1090-1139. The helper validates finite candidate sets with `checksol`, but for complements it only checks the left side of the complement and then falls through for broad sets:

```python
elif isinstance(solutions, Complement):
    A, B = solutions.args
    return Complement(check_set(A), B)
...
else:
    return solutions
```

Since `check_set(Complexes)` returns `Complexes`, the branch-invalid negative real axis remains.

## Mechanism

Removing radicals proves only that any true solution lies in the radical-free solution set. Here the radical-free equation is identically zero away from the denominator, but the original equation still has a square-root branch condition. `_solve_radical` subtracts only `x = 0` from denominators and never rechecks the original equation over the infinite candidate set, so `-1` is included.

## Suggested Fix Direction

When radical removal yields `Complexes`, intervals, complements, or other infinite sets, preserve the original equation as a condition unless the branch constraints can be solved explicitly. For this case the solution should exclude the negative real axis as well as zero.

## Confidence and Caveats

High confidence. Tracing shows `unrad` returning `(0, [])`, `_solve_radical` returning `Complement(Complexes, {0})`, and `checksol` rejecting `x = -1`.
