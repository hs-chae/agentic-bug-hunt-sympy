---
verdict: novel
confidence: 82
---

## Candidate Summary

`singularities(polylog(1, x), x, S.Complexes)` returns `EmptySet`, although `polylog(1, x) = -log(1 - x)` and has a singularity at `x = 1`.

## Search Queries

- `SymPy singularities polylog(1, x) x=1 EmptySet`
- `site:github.com/sympy/sympy/issues singularities polylog 1 x`
- `site:github.com/sympy/sympy/issues polylog(1, x) singularities`
- `site:stackoverflow.com SymPy singularities polylog(1,x)`
- `"polylog(1, x)" "zoo" "sympy"`
- `"polylog" "singularity" "SymPy" "GitHub"`

## Closest Matches

- https://docs.sympy.org/latest/modules/calculus/index.html - SymPy calculus docs for `singularities`, including the general API and caveat that not all singularity types are found.
- https://devdoc.net/python/sympy-1.0/_modules/sympy/calculus/singularities.html - Older public source docs state that supported singularity detection was limited mainly to rational functions.
- https://doc.sagemath.org/html/en/reference/functions/sage/functions/log.html - External Sage docs note `polylog(1, x)` rewrites to `-log(-x + 1)` and discuss the polylog branch cut, but this is not a SymPy bug report.

## Similarity Analysis

The public docs establish that `singularities` has limited coverage, and external CAS docs confirm the mathematical identity behind the expected singularity. I found no public SymPy issue, PR, Stack Overflow report, release note, or mailing-list discussion describing `singularities(polylog(1, x), x, S.Complexes) -> EmptySet` or the missed `x = 1` singularity.

## Specific Novelty Assessment

This appears specific-new rather than a duplicate. The broad limitation of `singularities` is documented, but no public material I found reports this exact special-function case or a fix that would automatically add the `polylog(1, x)` rewrite before singularity detection.

## Recommendation

continue_to_artifact_generation
