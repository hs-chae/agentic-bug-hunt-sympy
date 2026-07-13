### Candidate Bug 41: ask incorrectly proves 1/(xr - 1) is extended real for an arbitrary real xr

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, checkout from `SYMPY_CHECKOUT_PATH`, `sympy.__file__` observed as `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

See `reproduce_bug.py`.

**Actual output**

`ask(Q.extended_real(expr)) = True; expr.subs(xr, 1) = zoo; substituted value is_extended_real = False`

**Expected output**

`ask(Q.extended_real(expr))` should not be `True`; it should be `False` or unknown because an allowed real substitution gives `zoo`.

**Why this is wrong**

A predicate proven for an arbitrary real symbol must hold for every compatible real substitution. Substituting `xr=1` gives complex infinity `zoo`, and `zoo.is_extended_real` is `False`.

**Root cause**

The diagnosis locates the source-level cause in `sympy/assumptions/handlers/sets.py:389-391`: `ExtendedRealPredicate` uses a generic closed-group rule for `Pow`, so `(xr - 1)**-1` is treated as extended real because its base and exponent are extended real. The handler does not require the reciprocal base to be nonzero. See `root_cause.md`.

**Independent verification**

`related_bugs.py` checks the representative denominator and five shifted denominators. Each case substitutes the zero of the denominator and observes `zoo.is_extended_real == False`.

**Additional instantiations**

The additional shifts are `0, -1, 2, 3, -2`.

**Affected function or subsystem**

`assumptions / extended-real predicates`; affected location `sympy/assumptions/handlers/sets.py:389-391`.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_041_ask_incorrectly_proves_1_xr_1_is_extended_real_for_an_arbitr.py`.

**Confidence**

97%. The counterexample substitution is exact and directly contradicts the proven predicate.
