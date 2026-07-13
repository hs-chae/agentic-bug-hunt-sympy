# Fix solveset radical branch validation for sqrt(x)*sqrt(1/x) = 1

## Summary

`solveset` currently returns `Complement(Complexes, {0})` for:

```python
solveset(Eq(sqrt(x)*sqrt(1/x), 1), x, domain=S.Complexes)
```

That set includes negative real values such as `x = -1`, where the original equation is false under the principal square root.

## Reproducer

```python
from sympy import Eq, S, sqrt, solveset, symbols

x = symbols("x")
lhs = sqrt(x) * sqrt(1/x)
sol = solveset(Eq(lhs, 1), x, domain=S.Complexes)

print(sol)
print(sol.contains(S.NegativeOne))
print(lhs.subs(x, -1))
```

Current output:

```text
Complement(Complexes, {0})
True
-1
```

## Expected behavior

`-1` should not be included in the solution set. In general, the solution set over the principal complex square root should exclude zero and the negative real axis.

## Evidence

At `x = -1`,

```text
sqrt(x)*sqrt(1/x) = sqrt(-1)*sqrt(-1) = I*I = -1
```

so the equation `sqrt(x)*sqrt(1/x) = 1` is false. The proposed regression test checks this representative value plus five additional negative real values.

The source-level diagnosis points to `_solve_radical` in `sympy/solvers/solveset.py`. `unrad` produces a radical-free superset, and the current non-finite-set fallback returns that superset without checking the original equation.

## Suggested regression test

Add `pr/tests/test_bug_035_solveset_says_every_nonzero_complex_number_satisfies_sqrt_x.py`, which contains one parametrized test covering:

```text
-1, -2, -3, -1/2, -5, -7/3
```
