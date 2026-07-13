---
verdict: family_known_specific_new
confidence: 83
---

## Candidate Summary

`solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, S.Complexes)` returns `Complement(Complexes, {0})` in SymPy 1.14.0. This incorrectly includes negative real values such as `x = -1`, where the left side is `I`, the right side is `-I`, and the residual is `2*I`.

## Search Queries

- `SymPy solveset sqrt(1/x) 1/sqrt(x) branch cut bug`
- `site:github.com/sympy/sympy/issues "sqrt(1/x)" "1/sqrt(x)"`
- `site:github.com/sympy/sympy "sqrt(x)*sqrt(1/x)"`
- `site:github.com/sympy/sympy/issues "sqrt(x)*sqrt(1/x)"`
- `SymPy principal sqrt reciprocal branch cut solveset`

## Closest Matches

- SymPy `sqrt` documentation (`https://docs.sympy.org/dev/modules/functions/elementary.html`) says `sqrt` returns the principal square root and explains that square-root identities fail across branches.
- SymPy simplification tutorial (`https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html`) covers analogous power-identity restrictions and warns that identities are not applied unless assumptions justify them.
- Public math discussions about square-root multiplicativity and branch cuts, such as `sqrt(x*y) = sqrt(x)*sqrt(y)` failing for negative or complex values, match the mathematical family but do not report this SymPy `solveset` result.

## Similarity Analysis

The candidate is in the known principal-square-root branch-cut family. The closest public material explains why transformations like distributing square roots over reciprocals are unsafe across the negative real axis.

I found no exact report for `solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, S.Complexes)` returning all nonzero complex numbers, nor a public report using `x = -1` as the invalid included solution for this equation.

## Specific Novelty Assessment

The mathematical branch family is known, but this exact solver behavior appears new. Fixing public documentation or generic explanations about square-root branches would not automatically fix the missing branch exclusion in `solveset`.

## Recommendation

continue_to_artifact_generation
