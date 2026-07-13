---
verdict: family_known_specific_new
confidence: 84
---

## Candidate Summary

`function_range(sqrt(tan(x)**2), x, Interval(-1, 1))` returns `{tan(1)}` even though the expression is `Abs(tan(x))` on the real interval and takes the interior value `0` at `x = 0`. The expected range is `Interval(0, tan(1))`.

## Search Queries

- `site:github.com/sympy/sympy "function_range" "sqrt(tan(x)**2)"`
- `site:github.com/sympy/sympy "sqrt(tan(x)**2)"`
- `"function_range(sqrt(tan(x)**2)"`
- `"function_range" "sqrt(tan" "Interval(-1, 1)"`
- `site:github.com/sympy/sympy/issues "function_range" "sqrt" "tan"`
- `" {tan(1)}" "function_range" SymPy`
- GitHub issue search: `repo:sympy/sympy "function_range" "sqrt(tan"`

## Closest Matches

- https://github.com/sympy/sympy/issues/26518 reports `function_range` raising a `TypeError` for an `Abs(log(x)**(1/3))` expression when critical points are a `ConditionSet`.
- https://github.com/sympy/sympy/issues/22070 reports a wrong inverse-trig simplification with sign and singularity problems.
- https://github.com/sympy/sympy/issues/28486 discusses `function_range(tan(x)**2 + tan(3*x)**2 + 1, x, S.Reals)` being slow, not wrong.
- No result described `sqrt(tan(x)**2)` on `[-1, 1]`, the singleton output `{tan(1)}`, or the missing interior cusp value `0`.

## Similarity Analysis

The public material shows known fragility around `function_range`, absolute values, trigonometric expressions, and derivative/critical-point handling. However, the known reports involve exceptions, performance, or different simplification bugs. Fixing those specific issues would not automatically make `function_range` include derivative-undefined-but-continuous cusp points such as `x = 0` here.

## Specific Novelty Assessment

The exact minimal reproducer and wrong singleton range appear new. This is best treated as a new concrete instance in a known family: `function_range` missing critical values when the derivative is undefined but the function is continuous.

## Recommendation

continue_to_artifact_generation
