---
diagnosis_status: located
confidence: 88
location: sympy/solvers/recurr.py:816
---

## Candidate Summary

`rsolve(y(n + 2) - (n + 2)*y(n + 1) + y(n), y(n), {y(0): 1, y(1): 1})` returns `0`. The returned zero sequence violates both supplied initial conditions.

## Call Path

Public call: `sympy.rsolve(...)`.

Internal path:

- `sympy/solvers/recurr.py:rsolve`
- coefficient extraction from the recurrence into `coeffs = [1, -(n + 2), 1]`
- `rsolve_hyper(coeffs, 0, n, symbols=True)` at `recurr.py:806`
- initial-condition handling at `recurr.py:816-841`

A pinned trace showed `rsolve_hyper([1, -(n + 2), 1], 0, n, symbols=True)` returns `(0, [])`, so `rsolve` has a candidate solution with no arbitrary constants.

## Root Cause

The faulty logic is in `sympy/solvers/recurr.py:rsolve`, around lines `816-841`.

Initial conditions are only applied under:

```python
if symbols and init is not None:
```

When the recurrence solver returns a constant-free expression, `symbols` is empty. In this reproducer that expression is `0`, so the initial-condition block is skipped entirely. There is no fallback validation that a constant-free solution satisfies the provided initial values.

## Mechanism

For this recurrence, `rsolve_hyper(..., symbols=True)` does not find a nonzero kernel and returns `solution = 0`, `symbols = []`. Because `symbols` is empty, `rsolve` never builds the equations `solution.subs(n, 0) - 1` and `solution.subs(n, 1) - 1`.

The function then returns `solution` unchanged. Substituting `n = 0` or `n = 1` into `0` gives `0`, contradicting the requested values `1` and `1`.

## Suggested Fix Direction

When `init` is provided, `rsolve` should validate constant-free solutions too. If `symbols` is empty, it can directly check all supplied initial conditions and return `None` or raise the same unsolved-IC failure when any condition is false.

## Confidence and Caveats

Confidence is high for the bad return path. I did not diagnose why `rsolve_hyper` fails to find the nonzero solution family for this recurrence; that may be a separate solver limitation. The correctness bug here is that `rsolve` accepts and returns the constant-free candidate without checking the initial conditions.
