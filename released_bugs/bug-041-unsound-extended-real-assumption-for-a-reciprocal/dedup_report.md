---
verdict: family_known_specific_new
confidence: 83
---

## Candidate Summary

Candidate 106 reports that `ask(Q.extended_real(1/(xr - 1)))` returns `True` for an arbitrary real symbol `xr`, even though substituting `xr = 1` gives `zoo`, and `zoo.is_extended_real` is `False`.

## Search Queries

- `site:github.com/sympy/sympy/issues "extended_real" "zoo" "ask"`
- `site:github.com/sympy/sympy/issues "Q.extended_real" "denominator"`
- `"Q.extended_real" "zoo" "sympy/sympy"`
- `"ask(Q.extended_real" "zoo"`
- `"extended_real" "1/(x - 1)" "SymPy"`
- `"ExtendedRealPredicate" "zoo" "SymPy"`

## Closest Matches

- SymPy predicate docs define `Q.extended_real(x)` as true exactly for real numbers and `{-oo, oo}`: https://docs.sympy.org/latest/modules/assumptions/predicates.html
- The same docs identify `ExtendedRealPredicate` and `ExtendedRealHandler` as the relevant assumptions machinery: https://docs.sympy.org/latest/modules/assumptions/predicates.html

No public report was found for the *exact* query `ask(Q.extended_real(1/(xr - 1)))` returning `True`, or for this specific denominator-zero/`zoo` counterexample with a symbolic base. However, the same root-cause family is publicly tracked: the assumptions handlers unsoundly proving real-ness of a reciprocal with a possibly-zero denominator.

- https://github.com/sympy/sympy/issues/28150 — `ask(Q.real(Pow(0, -1, evaluate=False)))` gives `True` (OPEN). Same conceptual unsoundness in the assumptions handlers (reciprocal with zero base proved real).
- https://github.com/sympy/sympy/pull/28164 — "Fix incorrect result from Q.real() for Pow(0, negative exponent)" (CLOSED), Fixes #28150.
- https://github.com/sympy/sympy/pull/28377 — "[assumptions] Fix real predicate for Pow(0, -1)" (OPEN), Fixes #28150.

These cover the `Q.real(Pow(0, -1))` reciprocal-zero-denominator family that the original searches (which only used `extended_real`/`zoo` phrasings) missed. The present bug is nonetheless a **distinct, still-unfixed manifestation**: it uses a *symbolic* base via the `register_many(Add, Mul, Pow)` → `test_closed_group` path and triggers `Q.extended_real` rather than `Q.real`. The #28164/#28377 fixes only touch concrete-number bases through `_RealPredicate_number`, so they would not fix this; indeed on stable `ask(Q.real(1/(xr - 1)))` already returns `None`, and only `Q.extended_real` is wrongly `True`.

## Similarity Analysis

The broad risk is familiar for assumptions handlers: proving a property of a rational expression without checking denominator nonzero can be unsound. However, the searches did not identify a public SymPy issue or PR specifically covering `Q.extended_real` on reciprocals/powers with possible `zoo`.

The public predicate docs confirm that `zoo` is outside the extended real set because only real numbers and signed infinities are included, but they are not duplicate bug reports.

## Specific Novelty Assessment

This belongs to a known family rather than being wholly novel. The reciprocal-zero-denominator unsoundness in the assumptions handlers is publicly tracked as issue #28150 (OPEN) with PRs #28164 (CLOSED) and #28377 (OPEN). The specific `Q.extended_real` + symbolic-base + closed-group `Pow` manifestation here is distinct and remains unfixed by those PRs, so it is best classified as a known family with a specific new manifestation.

## Recommendation

continue_to_artifact_generation
