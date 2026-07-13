---
verdict: family_known_specific_new
confidence: 78
---

## Candidate Summary

`solveset(Eq(acos(x), 2*pi), x, S.Complexes)` returns `{1}`, but `acos(1) = 0`, so the returned point has residual `-2*pi`. The bug is a missing principal-range check when inverting `acos` by applying `cos`.

## Search Queries

- `"solveset(Eq(acos(x), 2*pi)"`
- `site:github.com/sympy/sympy/issues solveset acos(x) 2*pi returns 1`
- `SymPy solveset inverse trigonometric principal branch acos atan issue`
- `SymPy _invert_complex inverse trigonometric functions principal branch solveset`
- `Stack Overflow SymPy solveset acos atan principal branch`

## Closest Matches

- [SymPy solveset documentation](https://docs.sympy.org/latest/modules/solvers/solveset.html) says `solveset` returns a set of solutions satisfying the equation and documents separate real/complex-domain solving. This is relevant expected behavior, not a bug report for this reproducer.
- [Principal Branches of Inverse Trigonometric and Inverse Hyperbolic Functions](https://arxiv.org/abs/2312.07470) discusses principal branches for inverse trig/hyperbolic functions. This is mathematical background, not a SymPy issue.
- General web/GitHub/Stack Overflow searches for the exact reproducer and output did not find a public report.

## Similarity Analysis

The public principal-branch material covers the mathematical reason that `acos` cannot be inverted globally by `cos` without range restrictions. The SymPy documentation establishes that `solveset` should return actual satisfying values. Neither source describes `solveset(Eq(acos(x), 2*pi), x, S.Complexes)` returning `{1}` or a specific SymPy fix that would necessarily cover this case.

## Specific Novelty Assessment

The broad family, inverse-function solving must respect principal branches, is known. The exact SymPy minimized reproducer, wrong output `{1}`, and residual `-2*pi` were not found in public issue, PR, Stack Overflow, mailing-list, or release-note searches.

## Recommendation

continue_to_artifact_generation
