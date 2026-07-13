---
diagnosis_status: located
confidence: 86
location: sympy/series/gruntz.py:520
---

## Candidate Summary

`limit(lerchphi(x, 1, 1), x, 1, dir="-")` returns the unevaluated endpoint `lerchphi(1, 1, 1)` even though the left-hand limit is `oo`.

## Call Path

`limit(...)` constructs `Limit(lerchphi(x, 1, 1), x, 1, dir="-")` and calls `Limit.doit` in `sympy/series/limits.py`. The ordinary leading-term path cannot expand the shifted expression, so `Limit.doit` calls `gruntz` at `limits.py:380-381`.

`gruntz` converts the left-hand finite limit to an infinite limit by substituting `x = 1 - 1/z`, then calls `limitinf(lerchphi(1 - 1/z, 1, 1), z)`.

## Root Cause

The immediate wrong step is in `sympy/series/gruntz.py:mrv_leadterm`, lines 520-538. For this expression, the generic leading-term machinery treats the special function as having finite leading coefficient at the endpoint:

```text
mrv_leadterm(lerchphi(1 - 1/z, 1, 1), z)
    -> (lerchphi(1, 1, 1), 0)
```

Then `limitinf` sees exponent `0` and returns the coefficient unchanged at `gruntz.py:465-468`.

The special-function side contributes to this because `sympy/functions/special/zeta_functions.py:131-178` has `_eval_expand_func` rules that can expose this case as `polylog(1, x)/x`, and `expand_func(lerchphi(x, 1, 1))` becomes `-log(1 - x)/x`; however `lerchphi` has no `eval`, leading-term, or tractable rewrite hook that the limit path uses automatically near `z = 1`.

## Mechanism

The traced behavior is:

```text
e0 = lerchphi(1 - 1/z, 1, 1)
e0.rewrite("tractable", deep=True, limitvar=z) -> e0
mrv_leadterm(e0, z) -> (lerchphi(1, 1, 1), 0)
limitinf(e0, z) -> lerchphi(1, 1, 1)
```

This is endpoint substitution at a branch/divergence point. If the existing expansion rule is applied first:

```text
expand_func(lerchphi(x, 1, 1)) -> -log(1 - x)/x
limit(-log(1 - x)/x, x, 1, dir="-") -> oo
```

So the limit engine misses the divergent logarithmic behavior because it does not expand or otherwise special-case `lerchphi` at `z = 1, s = 1, a = 1`.

## Suggested Fix Direction

Add a limit/leading-term or tractable rewrite hook for `lerchphi` at `z -> 1`, at least for the `a = 1` specialization that rewrites to `polylog(s, z)/z`, and for `s = 1` to `-log(1 - z)/z`. The generic Gruntz path should not treat `lerchphi(1, 1, 1)` as a finite coefficient.

## Confidence and Caveats

The exact observed result is returned by `mrv_leadterm` and `limitinf`. The underlying fix likely belongs in `lerchphi` special-function expansion/leading-term support rather than in the generic Gruntz code alone.
