---
diagnosis_status: located
confidence: 90
location: sympy/concrete/products.py:256
---

## Candidate Summary

`product(sin(pi*n)/(n - 1), (n, 0, 2))` returns `0`, even though the factor at `n = 1` is `nan`.

## Call Path

The public call is `product`, which constructs a `Product` and calls `Product.doit`. At the start of `doit`, SymPy replaces definite-limit product variables with a dummy carrying assumptions inferred from the integer limits. The expression is then re-evaluated with that dummy before `_eval_product` runs.

## Root Cause

The key step is in `sympy/concrete/products.py:251-266`:

```python
for xab in self.limits:
    d = _dummy_with_inherited_properties_concrete(xab)
    if d:
        reps[xab[0]] = d
...
did = self.xreplace(reps).doit(**hints)
```

The helper is imported from `sympy/concrete/summations.py` and defined at `summations.py:1631-1659`. Because the limits are `0` and `2`, it creates an integer/nonnegative/real dummy. Replacing `n` by that dummy causes `sin(pi*_d)` to simplify to `0`, so the product function becomes `0` before `_eval_product` can see the undefined factor at `_d = 1`.

The downstream direct product evaluator at `products.py:398-400` would produce `nan` for the original raw factors, but it is bypassed because the pre-evaluated function is already zero.

## Mechanism

The original factors are `[0, nan, 0]`. Mathematically and in SymPy's raw `Mul`, this product is `nan`. During `Product.doit`, the dummy-assumption replacement makes the general factor simplify as if `sin(pi*n)` were identically zero for all integer `n`, yielding a zero product immediately. The denominator singularity at `n = 1` is erased because the expression has already collapsed to `0`.

## Suggested Fix Direction

Before replacing the index by an assumption-enriched dummy or accepting an identically zero product function, finite products should check the original factor for undefined values on the finite integer range. More generally, assumption strengthening in concrete products should not allow numerator identities to mask denominator singularities.

## Confidence and Caveats

Confidence is high: monkeypatch tracing showed `_eval_product` is entered with term `0`, not with `sin(pi*n)/(n - 1)`. Evaluating `_eval_product_direct` on the original term gives `nan`, confirming the wrong result is introduced before direct multiplication.
