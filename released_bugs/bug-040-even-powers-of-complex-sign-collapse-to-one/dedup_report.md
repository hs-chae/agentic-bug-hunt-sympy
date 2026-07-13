---
verdict: family_known_specific_new
confidence: 84
---

## Candidate Summary

`sign(1 + I)**2` evaluates to `1` in SymPy 1.14.0, but SymPy documents complex `sign` as a unit complex direction: `sign(1 + I)` remains unevaluated symbolically and numerically evaluates to `(1 + I)/sqrt(2)`. Squaring that value should give `I`, not `1`.

Suspected cause: `sign._eval_power` applies the real-valued identity `sign(x)**2 = 1` to a non-real complex argument.

## Search Queries

- `SymPy sign(1+I)**2 1 instead of I sign _eval_power`
- `site:github.com/sympy/sympy sign(1 + I)**2 sign _eval_power`
- `SymPy sign complex even power returns 1`
- `"sign(1 + I)**2" SymPy`
- `site:github.com/sympy/sympy/issues "sign" "Abs" "complex" "power"`
- `SymPy docs sign complex sign z Abs z`

## Closest Matches

- [SymPy elementary functions documentation](https://docs.sympy.org/latest/modules/functions/elementary.html) describes `sign` for complex expressions and shows `sign(1 + I)` remains symbolic while `evalf()` gives a complex unit direction. This confirms the expected semantics but is not a bug report.
- [Stack Overflow: result in SymPy depends on sign of a complex number](https://stackoverflow.com/questions/67023298/result-in-sympy-depends-on-sign-of-a-complex-number) reports a `gruntz`/limit failure involving `sign` of a complex expression. It is a public discussion of SymPy's incomplete handling of complex `sign`, but it is not about powers of `sign`.
- Searches of SymPy GitHub issues/PRs and public web results did not find `sign(1 + I)**2`, `sign._eval_power`, or the exact wrong result `1 instead of I`.

## Similarity Analysis

The Stack Overflow report is in the same broad area: SymPy has difficulty reasoning about `sign` for complex-valued expressions. However, the reported behavior there is a `NotImplementedError` during limit computation, not an algebraic simplification that rewrites an even power of complex `sign` to `1`.

The SymPy documentation is relevant because it establishes that `sign(1 + I)` represents the complex direction rather than a real sign. It does not describe the candidate failure or a fix.

## Specific Novelty Assessment

No public result found describes the exact candidate `sign(1 + I)**2 -> 1`, the overbroad `sign._eval_power` rule, or an even-power collapse of non-real complex signs. Fixing the Stack Overflow limit issue would not necessarily change `sign._eval_power`, and fixing the candidate would not automatically resolve that older limit failure.

## Recommendation

continue_to_artifact_generation
