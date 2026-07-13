---
verdict: family_known_specific_new
confidence: 84
---

## Candidate Summary

`solveset(Eq(x**Rational(2, 3), 4), x, S.Reals)` returns `{-8, 8}`. The negative value is not a solution under SymPy's principal-power semantics: substituting `-8` gives a nonzero complex residual.

## Search Queries

- `site:github.com/sympy/sympy/issues solveset x**(2/3) 4 -8 8 SymPy`
- `site:github.com/sympy/sympy/issues "x**(2/3)" solveset "S.Reals"`
- `site:github.com/sympy/sympy/issues "Rational(2, 3)" solveset real power`
- `"solveset(Eq(x**Rational(2, 3), 4)"`
- `SymPy fractional powers solveset principal branch negative solutions`
- `Stack Overflow SymPy solveset x**(2/3) -8 8`

## Closest Matches

- SymPy solveset documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.solveset documents the set-returning solver interface.
- SymPy elementary-function documentation: https://docs.sympy.org/latest/modules/functions/elementary.html describes principal-branch machinery and branch-sensitive elementary functions.
- Public mathematical background on exponentiation explains that negative bases with rational/non-integer exponents are branch-sensitive: https://en.wikipedia.org/wiki/Exponentiation.
- I found no public issue, PR, Stack Overflow question, mailing-list thread, or release note for `x**(2/3) = 4` returning `-8` from real-domain `solveset`.

## Similarity Analysis

The closest material is family-level: real solving with fractional powers must respect principal complex-power semantics. That is similar to the candidate's mechanism, but it does not establish that an existing public fix would cover this exact equation or that the exact false solution `-8` is publicly described.

## Specific Novelty Assessment

The exact minimized reproducer, returned set `{-8, 8}`, and failing residual at `-8` appear publicly new. A broad principal-branch or radical-solving fix might cover it, but I found no public report with such scope.

## Recommendation

continue_to_artifact_generation
