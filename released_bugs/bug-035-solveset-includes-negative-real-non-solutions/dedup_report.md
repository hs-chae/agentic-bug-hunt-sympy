---
verdict: family_known_specific_new
confidence: 83
---

## Candidate Summary

`solveset(Eq(sqrt(x)*sqrt(1/x), 1), x, S.Complexes)` returns `Complement(Complexes, {0})` in SymPy 1.14.0. This includes `x = -1`, where `sqrt(-1)*sqrt(-1) = -1`, so the residual is `-2`.

## Search Queries

- `SymPy solveset sqrt(1/x) 1/sqrt(x) branch cut bug`
- `site:github.com/sympy/sympy "sqrt(x)*sqrt(1/x)"`
- `site:github.com/sympy/sympy/issues "sqrt(x)*sqrt(1/x)"`
- `SymPy sqrt(x)*sqrt(1/x) equals 1 branch cut`
- `SymPy principal sqrt product reciprocal solveset`

## Closest Matches

- SymPy `sqrt` documentation (`https://docs.sympy.org/dev/modules/functions/elementary.html`) documents principal-square-root behavior and warns that identities such as `sqrt(x**2) = x` fail in general.
- SymPy solveset documentation (`https://docs.sympy.org/latest/modules/solvers/solveset.html`) states that the solver should represent the set of values for which the equation is true, and discusses preserving validity conditions.
- Public math discussions about square-root product identities and branch cuts, e.g. `sqrt(x*y) = sqrt(x)*sqrt(y)` not holding generally, cover the same mathematical family but not this SymPy solver result.

## Similarity Analysis

The public material establishes the same branch-cut rule: principal square roots are not multiplicative over arbitrary complex products. The candidate is the concrete SymPy `solveset` equation `sqrt(x)*sqrt(1/x) = 1` and the overly broad solution set.

I found no public issue, PR, release note, Stack Overflow report, or mailing-list discussion that states this exact equation returns `Complement(Complexes, {0})` or that `-1` is incorrectly included.

## Specific Novelty Assessment

This is a known square-root branch family with a specific new solver reproducer. A fix to a public discussion or documentation entry would not automatically resolve the candidate unless the solver path stops simplifying the product as `1` without branch restrictions.

## Recommendation

continue_to_artifact_generation
