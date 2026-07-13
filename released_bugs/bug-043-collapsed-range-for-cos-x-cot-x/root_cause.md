---
diagnosis_status: located
confidence: 86
location: sympy/calculus/singularities.py:95 and sympy/calculus/util.py:223
---

## Candidate Summary

For `f = cos(x)/cot(x)`, `continuous_domain(f, x, S.Reals)` returns `Reals` and `function_range(f, x, S.Reals)` returns `{0}`. This is impossible because `f.subs(x, pi/3) = sqrt(3)/2`, while points such as `pi/2` are undefined.

## Call Path

The public calls are `continuous_domain` and `function_range` from `sympy/calculus/util.py`. `continuous_domain` applies function-specific constraints and then subtracts `singularities(f, x, domain)`. `function_range` computes the period, replaces the infinite real domain with one period (`Interval(0, 2*pi)`), calls `continuous_domain`, samples interval endpoints, solves `f.diff(x) = 0`, and builds an interval/range from those values.

## Root Cause

There are two coupled faulty steps:

1. `sympy/calculus/singularities.py:95-102` rewrites trig functions before searching negative powers:

```python
e = expression.rewrite([sec, csc, cot, tan], cos)
...
for i in e.atoms(Pow):
    if i.exp.is_negative:
        sings += solveset(i.base, symbol, domain)
```

For `cos(x)/cot(x)`, this rewrite changes `cot(x)` to `cos(x)/sin(x)`, so the quotient becomes effectively `sin(x)`. The denominator condition `cot(x) = 0` is lost, and `singularities` returns `EmptySet`.

2. `sympy/calculus/util.py:223-233` reduces an infinite periodic domain to `Interval(0, period)`, then `function_range` at lines `253-281` samples only endpoints and critical points from that interval. With the missed singularities, the interval is closed, endpoint values are both `0`, and `solveset(f.diff(x), x, Interval(0, 2*pi))` returns `EmptySet`; the range is therefore constructed as `{0}`.

## Mechanism

The natural domain must exclude zeros and poles of `cot(x)`, including `pi/2 + k*pi`. Instead, the singularity finder rewrites through an identity that is only valid away from those same points and sees no negative powers. `continuous_domain` therefore returns the full real line. `function_range` then works on a single closed period with no detected discontinuities or critical points. Since both endpoints evaluate to `0`, it concludes that the only value is `0`, missing interior values such as `sqrt(3)/2`.

## Suggested Fix Direction

`singularities` should not erase denominator constraints when rewriting reciprocal trig functions. It should collect singularities from the original denominator, or add explicit zero/pole sets for `tan`, `cot`, `sec`, and `csc` before applying simplifying rewrites. `function_range` would also be more robust if it treated undefined points inside periodic intervals as domain cuts before endpoint/critical-value sampling.

## Confidence and Caveats

Confidence is high that the bad domain comes from `singularities` losing `cot(x) = 0`, and that the bad range follows from `function_range` trusting that domain. I did not fully inspect why `solveset` returns no critical points for the unsimplified derivative, but even perfect critical-point solving would still depend on the missing discontinuities.
