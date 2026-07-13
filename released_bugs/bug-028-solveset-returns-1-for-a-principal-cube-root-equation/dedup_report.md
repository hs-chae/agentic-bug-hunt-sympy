---
verdict: family_known_specific_new
confidence: 76
---

## Candidate Summary

`solveset(Eq(x**Rational(1, 3), -1), x, S.Reals)` returns `{-1}` in SymPy 1.14.0. Substituting the returned value gives `(-1)**(1/3)`, the principal complex cube root, so the residual is `1 + (-1)**(1/3)` and is numerically nonzero. The complex-domain result is `EmptySet`.

## Search Queries

- `site:github.com/sympy/sympy solveset x**Rational(1,3) -1 principal branch cube root real domain`
- `site:github.com/sympy/sympy "x**(1/3)" "solveset" "-1"`
- `site:github.com/sympy/sympy "(-1)**(1/3)" "solveset"`
- `site:github.com/sympy/sympy/issues "principal branch" "root" "solveset"`
- `site:github.com/sympy/sympy/issues "real_root" "solveset"`
- `site:stackoverflow.com sympy solveset x**(1/3) -1`
- `site:groups.google.com/g/sympy "x**(1/3)" "solveset"`

## Closest Matches

- SymPy solveset documentation: https://docs.sympy.org/latest/modules/solvers/solveset.html documents that `solveset` uses the explicit domain argument and should return values for which the target equation is true.
- SymPy elementary-function documentation: https://docs.sympy.org/latest/modules/functions/elementary.html documents principal-branch concepts for elementary complex functions and distinguishes branch-aware behavior from real-root interpretation.
- Local/public SymPy documentation and broad web searches found related principal-branch and rational-power material, but no public issue, PR, Stack Overflow question, mailing-list thread, or release-note entry for `solveset(Eq(x**Rational(1, 3), -1), x, S.Reals)` returning `{-1}`.

## Similarity Analysis

The broad bug family is known: rational powers and principal branches are a recurring source of incorrect solver transformations, and SymPy has separate real-root functionality. The closest public material establishes the mathematical context but does not describe this exact equation or a public fix that would necessarily reject `-1` for the principal cube-root equation.

This candidate is also adjacent to other real-domain rational-power solver issues, but a fix for a missed-root case such as `(x**2)**Rational(1, 3) = 1` would not automatically imply filtering the extraneous real value in `x**Rational(1, 3) = -1`.

## Specific Novelty Assessment

I found no exact public match for the minimized reproducer, the wrong output `{-1}`, or the residual `1 + (-1)**(1/3)`. The family is known, but this specific real-domain solveset behavior appears publicly new.

## Recommendation

continue_to_artifact_generation
