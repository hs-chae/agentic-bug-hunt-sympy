---
verdict: family_known_specific_new
confidence: 82
---

## Candidate Summary

`function_range(sqrt(x**2), x, S.Reals)` returns `EmptySet` in SymPy 1.14.0. Over the real line, `sqrt(x**2)` equals `Abs(x)`, so the expected range is `Interval(0, oo)` and values such as `0`, `2`, and `3` are directly attained.

## Search Queries

- `site:github.com/sympy/sympy "function_range" "sqrt(x**2)"`
- `site:github.com/sympy/sympy "function_range(sqrt(x**2)"`
- `"function_range" "sqrt(x**2)" "SymPy"`
- `"function_range" "Abs(x)" "EmptySet" "SymPy"`
- `site:github.com/sympy/sympy/issues "function_range" "EmptySet"`
- `site:stackoverflow.com SymPy function_range sqrt(x**2) EmptySet`

## Closest Matches

- SymPy calculus docs for `function_range`: https://docs.sympy.org/latest/modules/calculus/index.html#sympy.calculus.util.function_range show the API and examples, including ranges over `S.Reals`.
- SymPy refine docs: https://docs.sympy.org/latest/modules/assumptions/refine.html#sympy.assumptions.refine.refine show the related identity `refine(sqrt(x**2), Q.real(x)) -> Abs(x)`.
- General SymPy elementary-function docs: https://docs.sympy.org/latest/modules/functions/elementary.html document `sqrt`/`Abs` as elementary functions, relevant to the expression being ranged.

No public report was found for the exact `function_range(sqrt(x**2), x, S.Reals)` returning `EmptySet` symptom. However, the same `function_range` / `Abs`-cusp failure family is publicly documented in sympy/sympy issues #16469 (CLOSED), #21956 (OPEN), and #20101 (OPEN); see the Specific Novelty Assessment below.

## Similarity Analysis

The closest public material is API documentation and related real-domain simplification behavior. It confirms that `function_range` is supposed to compute ranges on real domains and that `sqrt(x**2)` can be refined to `Abs(x)` under real assumptions.

I did not find a public issue or discussion identifying `function_range` losing the range of `sqrt(x**2)` specifically. Similar branch/simplification issues around `sqrt(x**2)` in other subsystems would not automatically resolve this `calculus.util.function_range` failure.

## Specific Novelty Assessment

The underlying failure family is publicly known, even though the exact `sqrt(x**2) -> EmptySet` symptom was not found in a public report. Over the reals `sqrt(x**2) = Abs(x)`, and the root cause is `function_range`'s critical-point search missing the non-differentiable cusp of `Abs` at `x = 0`. That mechanism is already documented in public SymPy issues:

- https://github.com/sympy/sympy/issues/16469 — "`function_range` and `continuous_domain` showing unexpected results" (CLOSED): reports `function_range(abs(x), x, S.Reals)` failing, returning the correct `[0, oo)` only with `Symbol("x", real=True)`. Same `function_range`/`Abs`-cusp root cause as `sqrt(x**2) = Abs(x)`.
- https://github.com/sympy/sympy/issues/21956 — "NotImplementedError: Unable to find critical points for Abs(f(x))" (OPEN): `function_range`/`maximum` cannot find critical points of an `Abs` because the derivative is undefined at the cusp — the exact mechanism here.
- https://github.com/sympy/sympy/issues/20101 — "can't get abs of sin" (OPEN): maximum of an `Abs` expression fails; same Abs-cusp family.

So this is a specific new instance (the `sqrt(x**2)` spelling that collapses to `EmptySet` instead of raising) of the already-known Abs-cusp / `function_range` failure family; it is not a wholly novel failure mode with no public precedent.

## Recommendation

continue_to_artifact_generation
