## Title

Reject non-unique singular systems in Matrix.solve method-specific solvers

## Summary

`Matrix.solve(rhs, method=...)` correctly rejects non-unique singular systems on the default `GJ` path, but the `QR`, `LDL`, and `CRAMER` paths bypass that guard. For a consistent rank-deficient 2-by-2 system, `QR` returns a one-entry matrix and `LDL`/`CRAMER` return `nan` vectors.

## Reproducer

```python
from sympy import Matrix

A = Matrix([[1, 1], [2, 2]])
b = Matrix([1, 2])

for method in ["QR", "LDL", "CRAMER"]:
    print(method, A.solve(b, method=method))
```

Current output:

```text
QR Matrix([[1]])
LDL Matrix([[nan], [nan]])
CRAMER Matrix([[nan], [nan]])
```

## Expected behavior

These calls should reject the non-unique singular system, matching the default `GJ` behavior, or otherwise return a documented valid solution representation. A one-row result for two unknowns and `nan` vectors are invalid.

## Evidence

The system is `x + y = 1`, `2*x + 2*y = 2`, so `(x, y) = (1 - t, t)`. The proposed regression test covers this case plus five more singular consistent systems of the same form.

## Suggested regression test

See `tests/test_bug_049_matrix_solve_methods_return_malformed_results_on_singular_sy.py`.
