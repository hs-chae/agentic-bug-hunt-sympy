# Fix Matrix.is_diagonalizable ignores eigenvalue-collision branch for a parametric matrix

## Summary

This adds a regression test for a SymPy 1.14.0 correctness bug in `matrices / diagonalization and Jordan form for parametric matrices`.

## Reproducer

```python
a, b = symbols("a b")
M = Matrix([[a, 1], [0, b]])
print("is_diagonalizable:", M.is_diagonalizable())
P, D = M.diagonalize()
print("P:", P)
print("D:", D)
M_equal = M.subs(b, a)
print("specialized matrix:", M_equal)
print("specialized is_diagonalizable:", M_equal.is_diagonalizable())
```

Current output:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
is_diagonalizable: True
P: Matrix([[1, -1/(a - b)], [0, 1]])
D: Matrix([[a, 0], [0, b]])
specialized matrix: Matrix([[a, 1], [0, a]])
specialized is_diagonalizable: False
```

## Expected behavior

A conditional result, or refusal/qualification, because the matrix is diagonalizable when a != b but not diagonalizable when a = b.

## Evidence

When b = a, the matrix is [[a, 1], [0, a]], a nontrivial Jordan block. Its eigenspace has dimension 1 while the algebraic multiplicity is 2, so it is not diagonalizable. The accompanying artifact `related_bugs.py` also checks five additional instantiations and an independent numerical or definition-based oracle.

## Suggested regression test

Add `pr/tests/test_bug_046_matrix-is-diagonalizable-ignores-eigenvalue-collision-branch.py` or adapt its parametrized test into the relevant SymPy test module.
