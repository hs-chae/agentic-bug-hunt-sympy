---
verdict: family_known_specific_new
confidence: 82
---

## Candidate Summary

`solveset(Eq(sqrt(x**2), x), x, S.Complexes)` returns `Complexes` in SymPy 1.14.0. This is false because `x = -1` gives `sqrt((-1)**2) = 1`, not `-1`.

## Search Queries

- `SymPy solveset sqrt(x**2) x Complexes bug`
- `site:github.com/sympy/sympy/issues "sqrt(x**2)" "solveset"`
- `site:github.com/sympy/sympy/issues "sqrt(x**2)" "Complexes"`
- `"solveset" "sqrt(x**2)" "sympy"`
- `"Eq(sqrt(x**2), x)" "SymPy"`
- `"sqrt(x**2) = x" "SymPy"`

## Closest Matches

- SymPy `sqrt` documentation: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.miscellaneous.sqrt explicitly says `sqrt(x**2)` does not simplify to `x`, gives `Eq(sqrt(x**2), x).subs(x, -1)` as `False`, and explains that `sqrt` computes the principal square root.
- SymPy solveset documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.solveset states that returned sets contain values satisfying the given equation.
- General square-root reference: https://en.wikipedia.org/wiki/Square_root notes the real identity `sqrt(x**2) = |x|`, not `x`, for arbitrary real `x`.

## Similarity Analysis

The SymPy docs are a very close mathematical match: they use the same expression `Eq(sqrt(x**2), x)` and the same counterexample `x = -1`. However, the public documentation is not a bug report for `solveset`, and it does not mention `solveset(..., S.Complexes)` returning all complex numbers.

Fixing the documented simplification behavior would not automatically fix the candidate, because the docs already say SymPy should not simplify `sqrt(x**2)` to `x`. The candidate is specifically that the solver nevertheless treats the equation as universally true.

## Specific Novelty Assessment

The mathematical pitfall is definitely public and known in SymPy documentation. The specific solver correctness bug, `solveset(Eq(sqrt(x**2), x), x, S.Complexes) -> Complexes`, appears new.

## Recommendation

continue_to_artifact_generation
