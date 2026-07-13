---
verdict: family_known_specific_new
confidence: 76
---

## Candidate Summary

`singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals)` returns `EmptySet` in SymPy 1.14.0, even though substituting `x = 1` or `x = -1` gives `zoo`.

## Search Queries

- `site:github.com/sympy/sympy "singularities" "(x**2)**(1/3)"`
- `site:github.com/sympy/sympy "singularities" "Rational(1, 3)" "x**2"`
- `"singularities(1/((x**2)**Rational(1, 3) - 1)"`
- `"singularities" "1/((x**2)**Rational(1, 3) - 1)"`
- `SymPy "singularities" "fractional power" bug`
- `site:stackoverflow.com/questions "singularities" "sympy" "Rational"`

## Closest Matches

- SymPy singularities documentation: https://docs.sympy.org/latest/modules/calculus/index.html#sympy.calculus.singularities.singularities documents `singularities` as returning the set of values where an expression has a singularity, with `EmptySet` meaning no singularities in the domain.
- SymPy principal-root documentation: https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.miscellaneous.sqrt documents that root/power identities are branch-sensitive.
- General CAS-family literature: https://arxiv.org/abs/1203.1350 discusses the broad class of fractional-power simplification hazards.

## Similarity Analysis

The closest public material establishes the intended API and the broad principal-power risk, but it does not report missing poles for `1/((x**2)**(1/3) - 1)` or any equivalent singularities example. The failure also depends on the calculus singularity routine, likely through equation solving of the denominator, rather than only on expression simplification.

## Specific Novelty Assessment

No exact public duplicate was found. The bug family is known because fractional powers of powers are branch-sensitive, but this specific real singularity miss for poles at `{-1, 1}` appears publicly new.

## Recommendation

continue_to_artifact_generation
