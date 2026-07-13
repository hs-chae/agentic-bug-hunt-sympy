---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`solveset(Eq(log(x), 2*pi*I), x, S.Complexes)` returns `{1}` in SymPy 1.14.0. This is invalid for SymPy's principal `log`, because `log(1) = 0` and the principal logarithm has imaginary part in `(-pi, pi]`.

## Search Queries

- `SymPy solveset log(x) 2*pi*I returns 1 principal log bug`
- `site:github.com/sympy/sympy/issues solveset log(x) 2*pi*I`
- `site:github.com/sympy/sympy/pull solveset log principal branch inverse`
- `"log(x)" "2*pi*I" "solveset"`
- `"Eq(log(x), 2*pi*I)"`
- `"principal branch" "sympy" "solveset"`

## Closest Matches

- SymPy elementary-function documentation: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.exponential.log documents that `log` is the principal branch and returns values with complex argument in `(-pi, pi]`.
- SymPy solveset documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.solveset says `solveset` returns values for which the equation is true and claims completeness for returned solution sets.
- SymPy `invert_complex` documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.invert_complex discusses multi-valued complex inversion and valid-domain information for inverse transformations.

## Similarity Analysis

The public documentation confirms the mathematical premise behind the candidate: `log` is single-valued on the principal branch, so exponentiating `log(x) = 2*pi*I` without checking the target branch range is unsound. The `invert_complex` docs are also close to the suspected mechanism because the candidate is an inverse-function solve over `S.Complexes`.

I did not find a public issue, PR, Stack Overflow question, mailing-list thread, or release note that mentions this exact reproducer, the exact wrong output `{1}`, or a solved/fixed issue whose scope clearly includes rejecting `exp(2*pi*I)` as a solution of `log(x) = 2*pi*I`.

## Specific Novelty Assessment

The broad family, principal-branch-aware inverse solving, is known and documented as a source of care. The specific `solveset(Eq(log(x), 2*pi*I), x, S.Complexes) -> {1}` behavior appears new after focused searching.

## Recommendation

continue_to_artifact_generation
