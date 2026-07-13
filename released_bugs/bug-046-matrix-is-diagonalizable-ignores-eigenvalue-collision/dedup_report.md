---
verdict: family_known_specific_new
confidence: 74
---

## Candidate Summary

For `M = Matrix([[a, 1], [0, b]])`, `M.is_diagonalizable()` returns `True` and `M.diagonalize()` returns a matrix containing `-1/(a - b)`. After substituting `b = a`, the matrix becomes `Matrix([[a, 1], [0, a]])`, a non-diagonalizable Jordan block.

## Search Queries

- `"Matrix([[a, 1], [0, b]])" "is_diagonalizable"`
- `"Matrix([[a, 1], [0, b]])" "SymPy"`
- `site:github.com/sympy/sympy/issues "is_diagonalizable" "symbolic" "diagonalize"`
- `site:github.com/sympy/sympy/issues "diagonalize" "a - b" "is_diagonalizable"`
- `SymPy Matrix diagonalize symbolic eigenvalues a b diagonalizable issue`
- `SymPy is_diagonalizable symbolic matrix parameters eigenvalue collision`

## Closest Matches

- SymPy matrix documentation says `diagonalize()` returns `(P, D)` where `D = P^-1 * M * P`: https://docs.sympy.org/latest/modules/matrices/matrices.html#sympy.matrices.matrixbase.MatrixBase.diagonalize
- SymPy matrix documentation says `is_diagonalizable()` returns true if a matrix is diagonalizable and gives a non-diagonalizable nilpotent Jordan-block example: https://docs.sympy.org/latest/modules/matrices/matrices.html#sympy.matrices.matrixbase.MatrixBase.is_diagonalizable
- General diagonalizable-matrix references state that diagonalizability requires enough independent eigenvectors and that nontrivial Jordan blocks are not diagonalizable.
- No exact public SymPy issue, PR, Stack Overflow post, mailing-list thread, or release-note entry was found for this `Matrix([[a, 1], [0, b]])` parameter-collision case.

## Similarity Analysis

The public documentation and linear-algebra references are close mathematically: they establish that the `b = a` specialization is a defective Jordan block and that a returned `P` should be invertible. They do not report this SymPy parametric matrix, the unconditional `True`, or the singular transform containing `1/(a - b)`.

This is a known family in symbolic linear algebra: generic results over parameters can become invalid on exceptional parameter branches. The exact SymPy matrix and diagonalizability result were not found publicly.

## Specific Novelty Assessment

The broad parameter-branch/eigenvalue-collision family is known, but this minimized SymPy `is_diagonalizable`/`diagonalize` behavior appears specific and publicly new.

## Recommendation

continue_to_artifact_generation
