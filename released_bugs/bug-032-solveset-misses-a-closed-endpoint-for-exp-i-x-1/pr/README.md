# Fix solveset misses the endpoint 2*pi for exp(I*x) = 1 on a closed interval

## Summary

This regression test captures a correctness bug in solvers.solveset / periodic exponential equations over intervals.

## Reproducer

```python
solveset(Eq(exp(I*x), 1), x, Interval(0, 2*pi))
```

## Expected behavior

On the closed interval [0, 2*pi], exp(I*x)=1 at both endpoints, so the expected solution set is {0, 2*pi}.

## Actual behavior

```text
solution: {0}
2*pi in solution: False
residual at 2*pi: 0
```

## Evidence

The artifact bundle contains `reproduce_bug.py` and `related_bugs.py`. The verification script covers the minimal case plus five related instantiations and exits with `Incorrect` on the current buggy version.

## Suggested regression test

Add `pr/tests/test_bug_032_solveset-misses-the-endpoint-2-pi-for-exp-i-x-1-on-a-closed-.py` to the relevant SymPy test module or fold its parametrized test into the existing tests for the affected subsystem.
