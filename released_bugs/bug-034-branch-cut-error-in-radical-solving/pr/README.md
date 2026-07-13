# Fix solveset branch handling for sqrt(1/x) = 1/sqrt(x)

## Summary

`solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, domain=S.Complexes)` currently returns `Complement(Complexes, {0})`. That set incorrectly includes negative real values, where the principal square-root branches differ.

## Reproducer

```python
from sympy import Eq, S, sqrt, solveset, symbols

x = symbols("x")
sol = solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, domain=S.Complexes)
print(sol)
print(sol.contains(S.NegativeOne))
print((sqrt(1/x) - 1/sqrt(x)).subs(x, -1))
```

Current output:

```text
Complement(Complexes, {0})
True
2*I
```

## Expected behavior

The solution set should exclude the negative real axis as well as `0`. In particular, `-1` must not be reported as a solution.

## Evidence

For `x = -1`, `sqrt(1/x) = sqrt(-1) = I`, while `1/sqrt(x) = 1/I = -I`. The residual is `2*I`, so `-1` is not a solution. The same branch error occurs for other negative real values.

## Suggested regression test

Add the parametrized test in `pr/tests/test_bug_034_solveset_says_negative_numbers_satisfy_sqrt_1_x_1_sqrt_x.py`. It checks the representative value and five additional negative-real values that the current solver incorrectly includes.
