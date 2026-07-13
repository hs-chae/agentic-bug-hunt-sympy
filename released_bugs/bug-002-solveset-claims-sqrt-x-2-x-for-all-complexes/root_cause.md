---
diagnosis_status: located
confidence: 86
location: sympy/solvers/solveset.py:1094
---

## Candidate Summary

`solveset(Eq(sqrt(x**2), x), x, domain=S.Complexes)` returns `Complexes`, but `x = -1` is a counterexample because `sqrt((-1)**2) = 1`.

## Call Path

`solveset` rewrites the equation to `sqrt(x**2) - x = 0` and enters `_solveset`. Direct inversion cannot reduce it, so `_solveset` calls `unrad(f, x)` and then `_solve_radical`.

For this input, `unrad(sqrt(x**2) - x, x)` returns `(0, [])`. `_solve_radical` then solves the unradicalized equation `0 = 0`, which gives the full domain `Complexes`.

## Root Cause

The immediate faulty step is in `sympy/solvers/solveset.py`, `_solve_radical`, lines 1094-1096 and 1119-1135:

```python
if not cov:
    result = solveset_solver(eq, symbol) - ...
...
else:
    return solutions
```

`unrad` returns a superset equation, not an equivalent equation. Here it squares `sqrt(x**2) = x`, obtaining `x**2 = x**2`, i.e. `0 = 0`. `_solve_radical` then accepts the non-finite result `Complexes`; its checker only validates `FiniteSet`, `Union`, and `Complement` cases. The fallback at lines 1133-1135 returns unvalidated set results unchanged.

## Mechanism

The principal square root is branch-sensitive. Squaring both sides of `sqrt(x**2) = x` loses the condition that `x` must be on the branch where the principal square root of `x**2` equals `x`. The unradicalized equation becomes tautological, so `_solve_radical` returns the whole complex domain.

Because `Complexes` is not a finite set, `_solve_radical.check_set` does not test any sample or attach the original equation as a condition. The counterexample `x=-1` remains included.

## Suggested Fix Direction

When radical removal returns a non-finite solution set, `_solve_radical` should not return it unconditionally. It should either intersect with a `ConditionSet(symbol, Eq(original_f, 0), result)` or derive the branch conditions introduced by the radical-clearing step. For this case, the result must encode the principal-square-root branch restriction rather than `Complexes`.

## Confidence and Caveats

High confidence for the immediate source-level cause. The deeper mathematical cause is branch loss during radical clearing, but the concrete acceptance of `Complexes` happens because `_solve_radical` does not validate non-finite supersets.
