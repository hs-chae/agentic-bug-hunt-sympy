---
diagnosis_status: located
confidence: 91
location: sympy/functions/elementary/piecewise.py:225
---

## Candidate Summary

`limit(Piecewise((0, x < 0), (1, True)), x, 0, dir="-")` returns `1`, but the left-hand limit is `0`.

I reran the reproducer against the pinned checkout and confirmed the result.

## Call Path

Public call:

`limit(p, x, 0, dir="-")`

Relevant path:

`sympy/series/limits.py:15-66` constructs `Limit(...).doit(deep=False)`.

`sympy/series/limits.py:201-394` computes the directed limit. For finite `z0`, it sets `cdir = -1` at lines 262-266, then tries leading-term based evaluation.

The expression-specific leading term for `Piecewise` is `sympy/functions/elementary/piecewise.py:225-228`, `Piecewise._eval_as_leading_term`.

Instrumentation confirmed that `Piecewise((0, x < 0), (1, True))._eval_as_leading_term(x, None, S.NegativeOne)` returns `1`.

## Root Cause

The faulty code is `sympy/functions/elementary/piecewise.py`, `Piecewise._eval_as_leading_term`, lines 225-228:

```python
def _eval_as_leading_term(self, x, logx, cdir):
    for e, c in self.args:
        if c == True or c.subs(x, 0) == True:
            return e.as_leading_term(x)
```

The method receives `cdir`, but ignores it. It substitutes `x = 0` into the branch condition instead of testing which branch holds as `x` approaches `0` from the requested direction.

For the condition `x < 0`, `c.subs(x, 0)` is `False`, so the method skips the left branch even when `cdir == -1`. It then reaches the default `True` branch and returns the leading term of `1`.

## Mechanism

The limit engine shifts a finite limit point to `0` and carries the approach direction as `cdir`. For a left-hand limit, a sufficiently small negative `x` satisfies `x < 0`, so the branch value should be `0`.

Because `_eval_as_leading_term` checks only the exact boundary point `x = 0`, it treats the first branch as inactive at the limit point and chooses the fallback branch. The selected expression is then the constant `1`, which the limit engine returns as the left-hand limit.

## Suggested Fix Direction

Make `Piecewise._eval_as_leading_term` direction-aware. For relational conditions involving the limit variable, it should evaluate branch truth in a punctured neighborhood according to `cdir`, for example by substituting a positive dummy with sign `cdir` or by using set/interval containment rather than direct boundary substitution.

## Confidence and Caveats

Confidence is high. This diagnosis is specific to the leading-term path for finite directed limits; other Piecewise limit paths may also need consistent directional condition selection, but this reproducer is explained by the ignored `cdir` in `_eval_as_leading_term`.
