---
verdict: family_known_specific_new
confidence: 77
---

## Candidate Summary

`integrate(1/(x*sqrt(x**2 + 1)), x)` returns `-asinh(1/x)` in SymPy 1.14.0. Its derivative has the wrong sign on the negative real branch, e.g. at `x = -2`.

## Search Queries

- `SymPy integrate 1/(x*sqrt(x**2+1)) -asinh(1/x) bug`
- `site:github.com/sympy/sympy/issues "1/(x*sqrt(x**2 + 1))"`
- `"-asinh(1/x)" "SymPy" "integrate"`
- `"1/(x*sqrt(x**2 + 1))"`
- `"1/(x*sqrt(x**2+1))"`
- `"-asinh(1/x)" "integrate"`

## Closest Matches

- SymPy integrals documentation: https://docs.sympy.org/latest/modules/integrals/integrals.html#sympy.integrals.integrals.integrate documents indefinite integration and the optional Meijer G-function integration path.
- SymPy `Integral.transform` documentation: https://docs.sympy.org/latest/modules/integrals/integrals.html#sympy.integrals.integrals.Integral.transform warns that quadratic substitutions are acceptable only when the resulting integrand does not depend on the sign of the solutions.
- Euler substitution reference: https://en.wikipedia.org/wiki/Euler_substitution gives related radical-integration formulas and branch-restricted antiderivative contexts, but not this SymPy output.

## Similarity Analysis

The public docs contain a relevant family warning: substitutions through quadratic expressions can be invalid when sign branches matter. That is close to the diagnosed mechanism, where the Meijer path effectively loses the sign distinction between positive and negative `x`.

I did not find a public SymPy issue/PR/comment, Stack Overflow report, mailing-list post, or release note mentioning this exact integrand, the output `-asinh(1/x)`, or the derivative sign mismatch at a negative real point.

## Specific Novelty Assessment

The branch-loss family is known, but the specific indefinite integral `1/(x*sqrt(x**2 + 1))` returning a one-branch antiderivative appears new after focused searching.

## Recommendation

continue_to_artifact_generation
