# Fix rsolve validation for constant-free solutions with initial conditions

## Summary

`rsolve` can return a constant-free expression that violates supplied initial conditions. For `y(n + 2) - (n + 2)*y(n + 1) + y(n) = 0` with `y(0)=1`, `y(1)=1`, SymPy 1.14.0 returns `0`.

## Reproducer

```python
n = symbols("n", integer=True)
y = Function("y")
rec = y(n + 2) - (n + 2)*y(n + 1) + y(n)
rsolve(rec, y(n), {y(0): 1, y(1): 1})
```

Actual result is `0`, whose values at `n=0` and `n=1` are both `0`.

## Expected Behavior

The returned expression must satisfy all supplied initial conditions, or `rsolve` should report that it cannot solve the recurrence with those conditions.

## Evidence

Forward recurrence from the supplied initial values gives `[1, 1, 1, 2, 7, 33]`, so the zero sequence is not the requested solution.

## Suggested Regression Test

See `tests/test_bug_019_rsolve_returns_a_solution_that_violates_supplied_initial_con.py`.
