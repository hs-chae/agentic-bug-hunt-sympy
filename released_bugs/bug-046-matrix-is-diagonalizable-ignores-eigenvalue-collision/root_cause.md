---
diagnosis_status: narrowed
confidence: 84
location: sympy/matrices/eigen.py:451
---

## Candidate Summary

For `M = Matrix([[a, 1], [0, b]])`, `M.is_diagonalizable()` returns `True` and `M.diagonalize()` returns a change-of-basis matrix containing `-1/(a - b)`. If `b = a`, the matrix becomes a nontrivial Jordan block `[[a, 1], [0, a]]`, which is not diagonalizable.

## Call Path

The public call `M.is_diagonalizable()` dispatches through `MatrixBase.is_diagonalizable` to `_is_diagonalizable` in `sympy/matrices/eigen.py`. `_is_diagonalizable` calls `_is_diagonalizable_with_eigen` at line 515. `_is_diagonalizable_with_eigen` computes `M.eigenvects(simplify=True)` at line 451 and then checks each reported eigenvalue independently at lines 453-458.

`M.diagonalize()` calls `_diagonalize`, which also calls `_is_diagonalizable_with_eigen` at lines 696-697, then uses the returned eigenvectors directly to build `P` and `D` at lines 705-714.

## Root Cause

The cause is localized to the eigenvector/diagonalizability pipeline in `sympy/matrices/eigen.py`. `_is_diagonalizable_with_eigen` at line 451 trusts `eigenvects()` as an unconditional decomposition of the symbolic-parameter matrix. For this matrix, `eigenvects()` reports two eigenvalues:

```text
(a, 1, [Matrix([[1], [0]])])
(b, 1, [Matrix([[-1/(a - b)], [1]])])
```

The code at lines 453-458 only checks whether each listed eigenvalue's algebraic multiplicity equals the number of eigenvectors for that listed eigenvalue. It does not check whether distinct symbolic eigenvalue keys can collide under parameter specializations, and it does not record the nonzero condition introduced by the eigenvector denominator `a - b`.

I did not pin the single lower-level line that first introduces the `1/(a - b)` assumption. It comes from the eigenspace calculation `_eigenspace(M, eigenval, ...)` at lines 284-287, which computes a nullspace over generic symbolic expressions and treats `a - b` as invertible.

## Mechanism

For generic parameters with `a != b`, the matrix has two distinct eigenvalues and is diagonalizable. The nullspace for eigenvalue `b` solves `(M - bI)v = 0`, producing a vector with `1/(a - b)`. That vector is valid only when `a - b != 0`.

`_is_diagonalizable_with_eigen` then sees two separate eigenvalue entries, each with multiplicity `1` and one basis vector, so it returns `True`. When `b = a`, those two symbolic eigenvalues collapse to a single eigenvalue of algebraic multiplicity `2`, while the eigenspace has dimension `1`. The generic eigenvector containing `1/(a - b)` is invalid on that branch, but the code has no mechanism to represent or test that condition.

## Suggested Fix Direction

Symbolic diagonalization needs to carry parameter conditions from eigenvalue distinctness and from denominators introduced while computing eigenvectors. At minimum, if eigenvalues are symbolic and pairwise equality is undecidable, `is_diagonalizable` should not return unconditional `True`; it should return a conditional result, raise/return unknown, or require assumptions such as `Ne(a, b)`.

## Confidence and Caveats

Confidence is moderate-high for the localized area but not for a single exact line. The public wrong result is fully explained by `_is_diagonalizable_with_eigen` accepting generic `eigenvects()` output unconditionally. The lower-level nullspace computation is a general symbolic linear algebra behavior rather than an isolated special-case bug in `diagonalize`.
