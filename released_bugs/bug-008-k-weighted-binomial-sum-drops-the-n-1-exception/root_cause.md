---
diagnosis_status: located
confidence: 88
location: sympy/concrete/gosper.py:214
---

## Candidate Summary

`summation((-1)**k*k*binomial(n, k), (k, 0, n))` returns `0` for nonnegative integer `n`, but at `n = 1` the direct finite sum is `-1`.

## Call Path

`summation` constructs a `Sum` and calls `.doit()`, which reaches `sympy/concrete/summations.py:eval_sum`. Since the range length is symbolic, `eval_sum` calls `eval_sum_symbolic` at `summations.py:1057`. `eval_sum_symbolic` tries Gosper summation at `summations.py:1236`.

For the expanded summand, `gosper_term` in `sympy/concrete/gosper.py` returns the certificate `-(k - 1)/(n - 1)`. Then `gosper_sum` computes the definite sum using the endpoint formula at `gosper.py:214`.

## Root Cause

The immediate faulty step is `sympy/concrete/gosper.py:214`:

```python
result = (f*(g + 1)).subs(k, b) - (f*g).subs(k, a)
```

For this summand, the Gosper certificate `g = -(k - 1)/(n - 1)` has a pole at the parameter value `n = 1`. `gosper_sum` substitutes the symbolic upper and lower bounds and factors the result without recording that the certificate is invalid at `n = 1`. The caller only wraps results in a `Piecewise` for visible denominators in `Mul`/`Add` results (`summations.py:1238-1256`), but here the endpoint expression has already simplified to the scalar `0`, so the exceptional parameter is lost.

## Mechanism

For generic `n`, Gosper's telescoping certificate gives a zero endpoint difference. At `n = 1`, the certificate denominator `n - 1` is zero, so the telescoping proof is not valid. The original sum is `0*binomial(1,0) - 1*binomial(1,1) = -1`, but `gosper_sum` returns the generic value `0`, and `eval_sum_symbolic` returns it unchanged.

## Suggested Fix Direction

Track parameter denominators introduced by `gosper_term`/`gosper_sum` and emit a `Piecewise` or fall back to direct evaluation at excluded parameter values. In this case the result needs a branch for `n = 1`.

## Confidence and Caveats

Confidence is high. A trace showed `gosper_term((-1)**k*k*binomial(n,k), k) = -(k - 1)/(n - 1)` and `gosper_sum(..., (k, 0, n)) = 0`, matching the lost `n = 1` exception.
