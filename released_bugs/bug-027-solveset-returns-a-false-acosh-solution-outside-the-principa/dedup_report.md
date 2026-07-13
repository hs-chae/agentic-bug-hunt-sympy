---
verdict: family_known_specific_new
confidence: 76
---

## Candidate Summary

`solveset(Eq(acosh(x), 2*pi*I), x, S.Complexes)` returns `{1}`, but `acosh(1) = 0`, so the residual is `-2*pi*I`. The bug is range-blind inversion of principal `acosh` using `cosh`.

## Search Queries

- `"solveset(Eq(acosh(x), 2*pi*I)"`
- `site:github.com/sympy/sympy/issues solveset acosh(x) 2*pi*I returns 1`
- `SymPy solveset inverse hyperbolic principal branch acosh issue`
- `SymPy _invert_complex inverse hyperbolic principal branch solveset`
- `Stack Overflow SymPy solveset acosh principal branch`

## Closest Matches

- [SymPy solveset documentation](https://docs.sympy.org/latest/modules/solvers/solveset.html) states that returned sets should satisfy the equation and that complex-domain solving has distinct handling.
- [Principal Branches of Inverse Trigonometric and Inverse Hyperbolic Functions](https://arxiv.org/abs/2312.07470) covers the relevant principal-branch mathematics for inverse hyperbolic functions.
- Searches did not find the exact `acosh(x) = 2*pi*I` reproducer or a public SymPy issue naming this false solution.

## Similarity Analysis

The public branch literature is relevant because `cosh` is not a global inverse for principal `acosh`. That is a family-level match only. The duplicate criterion requires a public report or fix that automatically covers this exact behavior; no such match was found.

## Specific Novelty Assessment

Known family: inverse hyperbolic principal-branch range conditions. Specific new behavior: SymPy `solveset` returning `{1}` for `acosh(x) = 2*pi*I`.

## Recommendation

continue_to_artifact_generation
