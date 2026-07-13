---
diagnosis_status: located
confidence: 88
location: sympy/core/mul.py:529 and sympy/core/relational.py:625
---

## Candidate Summary

`Piecewise((1, x > 0))` has an implicit undefined region. Substitution at `x = -1` gives `nan`, but algebraic identities simplify `p*0` to `0`, `p-p` to `0`, and `Eq(p, p)` to `True` before the undefined region can be observed.

## Call Path

`Piecewise((1, x > 0))` is constructed in `sympy/functions/elementary/piecewise.py:131-154`; because there is no final `True` branch, it remains an incomplete `Piecewise`. `p*0` enters `Mul` simplification in `sympy/core/mul.py`; `p-p` enters `Add`/`Mul` combination in `sympy/core/add.py` and `sympy/core/mul.py`; `Eq(p, p)` enters `Equality.__new__` in `sympy/core/relational.py:625-636`, which delegates to structural equality through `is_eq`.

## Root Cause

The responsible logic is the core algebra simplification layer, especially `sympy/core/mul.py:529-535`, where any collected factor with zero exponent is discarded as `x**0 -> 1`, and `sympy/core/relational.py:625-634`, where `Eq(lhs, rhs)` evaluates structurally identical operands to `True`.

Those rules are valid for ordinary total finite expressions, but they do not test whether an expression is partial through an incomplete `Piecewise`. `Piecewise.eval` documents the missing-branch behavior as undefined/nan (`sympy/functions/elementary/piecewise.py:168-170`), but the generic `Mul`, `Add`, and `Equality` simplifiers do not preserve that domain information.

## Mechanism

For `p*0`, multiplication canonically treats the `Piecewise` factor as removable because the numeric coefficient is zero; the result is the scalar `0`. Substitution then sees only `0`, not the original `Piecewise`, so `x = -1` no longer reaches the implicit `nan` branch.

For `p-p`, terms with the same symbolic object are combined to zero in `Add`/`Mul`, again erasing the fact that evaluating either occurrence at `x = -1` is undefined. For `Eq(p, p)`, structural identity is enough for `Equality.__new__` to return `True`, even though pointwise equality is not meaningful where both sides are undefined.

## Suggested Fix Direction

Core identity simplifications that collapse an expression containing an incomplete `Piecewise` to a total scalar should either preserve the undefined condition, for example by folding to an explicit `Piecewise`, or decline the simplification when the operand can evaluate to `nan` on part of its domain.

## Confidence and Caveats

High confidence for the mechanism and source area. The exact fix may belong in a shared predicate such as "can this expression be undefined on a branch" rather than in each individual simplifier.
