---
diagnosis_status: located
confidence: 82
location: sympy/functions/special/elliptic_integrals.py:82
---

## Candidate Summary

`limit(elliptic_k(x), x, 1, dir="-")` returns `zoo`, but the real left-hand limit of the complete elliptic integral `K(m)` is positive infinity.

## Call Path

The public `limit` call enters `Limit.doit` in `sympy/series/limits.py`, then `gruntz` in `sympy/series/gruntz.py`. Gruntz converts the left approach to a small-positive dummy and asks for a leading term. That reaches `elliptic_k._eval_nseries` in `sympy/functions/special/elliptic_integrals.py`.

The trace showed:

```text
elliptic_k._eval_nseries self=elliptic_k(1 - _w)
hyper._eval_nseries self=hyper((1/2, 1/2), (1,), 1 - _w)
hyper._eval_nseries -> nan
elliptic_k._eval_nseries -> nan
limit -> zoo
```

## Root Cause

`sympy/functions/special/elliptic_integrals.py:82-84` delegates the local series of complete `elliptic_k` entirely to the hypergeometric rewrite:

```python
return hyperexpand(self.rewrite(hyper)._eval_nseries(x, n=n, logx=logx))
```

For `elliptic_k(1 - w)`, the correct leading behavior is logarithmic and positive for `w -> 0+`. The delegated hypergeometric nseries cannot represent this branch-point expansion and returns `nan`. The limit machinery then loses the one-sided real sign information and reports unsigned complex infinity.

The exact value table also returns `S.ComplexInfinity` at `m = 1` in `elliptic_integrals.py:65-66`, which is fine for the singular point itself but not enough for a directional real limit.

## Mechanism

The left limit needs the leading term `-log(1 - m)/2 + O(1)`, which tends to `+oo` as `m -> 1-`. Because the elliptic function class does not provide that expansion and the generic hypergeometric nseries returns `nan`, `gruntz` cannot infer a positive real divergence. It falls back to the unsigned singular classification `zoo`.

## Suggested Fix Direction

Implement a branch-aware leading term or nseries for complete `elliptic_k` near `m = 1`, using the real approach direction when available. At minimum, for `m = 1 - w` with `w` positive, return the logarithmic leading behavior so the limit code can produce `oo`.

## Confidence and Caveats

Good confidence on the faulty path. The final `zoo` is produced by the limit machinery after the elliptic/hypergeometric nseries returns `nan`; the precise fallback branch inside `Limit.doit`/`gruntz` is less important than the missing branch-point expansion in `elliptic_k`.
