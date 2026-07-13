---
diagnosis_status: located
confidence: 98
location: sympy/functions/elementary/complexes.py:413
---

## Candidate Summary

`sign(1 + I)**2` evaluates to `1`, but the complex sign is `z/Abs(z)` for nonzero complex `z`, so the expected value is `(1 + I)**2/Abs(1 + I)**2 = I`.

## Call Path

The reproducer calls `sign(1 + I)**2`. `sign(1 + I)` remains unevaluated in `sympy.functions.elementary.complexes.sign.eval`, because the argument is neither real nor purely imaginary. The `Pow` construction for `sign(1 + I)**2` then dispatches to `sign._eval_power`.

## Root Cause

The responsible code is `sympy/functions/elementary/complexes.py`, method `sign._eval_power`, lines 413-419:

```python
if (
    fuzzy_not(self.args[0].is_zero) and
    other.is_integer and
    other.is_even
):
    return S.One
```

This applies the real-valued identity `sign(x)**2 = 1` using only a nonzero-argument check and an even-integer exponent check. It does not require `self.args[0]` to be real or purely imaginary in a way that would make the even power equal to `1`.

## Mechanism

For `arg = 1 + I`, `arg.is_zero` is false, and exponent `2` is an even integer. The method returns `S.One` immediately. That bypasses the general complex-sign definition documented just above in the same class, where `sign(z)` is `z/Abs(z)` for nonzero complex `z`. If `sign(1 + I)` is forced through `doit()` or rewritten as `Abs`, its square becomes `(1 + I)**2/2 = I`, confirming that the premature power simplification is the wrong step.

## Suggested Fix Direction

Restrict this `_eval_power` shortcut to real signs, or otherwise to cases where the sign value is known to square to `1`. For general complex arguments, leave the power unevaluated or rewrite through `arg/Abs(arg)`.

## Confidence and Caveats

High confidence. The wrong result is produced directly by this method, and bypassing this shortcut yields the expected complex value.
