---
diagnosis_status: located
confidence: 92
location: sympy/assumptions/handlers/sets.py:389
---

## Candidate Summary

`ask(Q.extended_real(1/(xr - 1)))` returns `True` for a symbol `xr` declared real.  This is unsound because substituting `xr = 1` gives `zoo`, and `zoo.is_extended_real` is `False`.

## Call Path

The public call is `ask(Q.extended_real(expr))` with `expr = 1/(xr - 1)`.

The expression is a `Pow` with base `xr - 1` and exponent `-1`.  The `ExtendedRealPredicate` handler for `Pow` is registered in `sympy/assumptions/handlers/sets.py:389-391` and delegates to `test_closed_group`.  `test_closed_group` in `sympy/assumptions/handlers/common.py:150-156` checks the predicate on each argument of the expression and returns true if all arguments are extended real.

The scratch tracer showed:

```text
expr.args -> (xr - 1, -1)
ask(Q.extended_real(xr - 1)) -> True
ask(Q.extended_real((xr - 1)**-1)) -> True
```

## Root Cause

The faulty logic is the shared `ExtendedRealPredicate` handler for `Add`, `Mul`, and `Pow` at `sympy/assumptions/handlers/sets.py:389-391`:

```python
@ExtendedRealPredicate.register_many(Add, Mul, Pow)
def _(expr, assumptions):
    return test_closed_group(expr, assumptions, Q.extended_real)
```

This treats the extended reals as closed under arbitrary `Pow` whenever the base and exponent are extended real.  That is false for negative powers unless the base is known nonzero.  Here, `xr - 1` is extended real, and `-1` is extended real, so the group-closure helper proves the reciprocal extended real even though the base can be zero.

## Mechanism

For `xr` real, `xr - 1` is extended real.  The handler then reasons structurally over `(xr - 1, -1)` and concludes `(xr - 1)**-1` is extended real.  It does not add or query `Q.nonzero(xr - 1)`, so it misses the admissible real substitution `xr = 1`.  Under that substitution the expression evaluates to complex infinity `zoo`, which is outside the extended real line, contradicting the predicate result.

## Suggested Fix Direction

Split the `Pow` handling from the simple `Add`/`Mul` closed-group rule.  For negative exponents or reciprocals, require the base to be provably nonzero before returning `True`; otherwise return `None`.  Similar care may be needed for other exponent classes where extended-real closure has side conditions.

## Confidence and Caveats

Confidence is high because the registered handler and helper exactly reproduce the result.  I did not audit every extended-real `Pow` edge case; this diagnosis is scoped to the missing nonzero guard for reciprocals.
