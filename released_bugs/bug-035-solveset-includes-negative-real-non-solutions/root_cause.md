---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:1090
---

## Candidate Summary

`solveset(Eq(sqrt(x)*sqrt(1/x), 1), x, S.Complexes)` returns `Complement(Complexes, {0})`, but `x = -1` is not a solution because `sqrt(-1)*sqrt(-1) = -1`.

## Call Path

`solveset` rewrites the equation as `sqrt(x)*sqrt(1/x) - 1`. The direct inverter only moves the constant and cannot solve the radical product, so `_solveset` calls `unrad` and then `_solve_radical`.

`unrad(sqrt(x)*sqrt(1/x) - 1, x)` returns `(0, [])`, because squaring the radical product gives `x*(1/x) - 1 = 0`.

## Root Cause

The responsible code is `sympy/solvers/solveset.py`, `_solve_radical`, lines 1090-1139. `unrad` returns a superset equation, but `_solve_radical` only checks finite candidate sets. Its `check_set` fallback returns broad infinite sets unchanged:

```python
else:
    # XXX: There should be more cases checked here.
    return solutions
```

After denominator removal, this unchecked superset becomes `Complement(Complexes, {0})`.

## Mechanism

The algebraic transformation assumes multiplicative behavior of square roots after clearing radicals. Principal square root is not multiplicative across the negative real branch cut. The radical-free identity is true for all nonzero `x`, but the original equation fails on the negative real axis. Because the solver never validates the infinite candidate set against the original equation, invalid values such as `-1` remain included.

## Suggested Fix Direction

Do not return infinite solution sets from radical removal as final unless the original radical equation has been enforced. A conservative result would be a `ConditionSet` over the candidate set; a complete fix would derive and subtract the principal-branch failure set.

## Confidence and Caveats

High confidence. Direct tracing shows `unrad` producing `(0, [])`, `_solve_radical` returning `Complement(Complexes, {0})`, and substitution at `-1` giving residual `-2`.
