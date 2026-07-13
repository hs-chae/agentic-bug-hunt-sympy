---
diagnosis_status: located
confidence: 88
location: sympy/solvers/solveset.py:284
---

## Candidate Summary

`solveset(Eq(x**Rational(1, 3), -1), x, S.Reals)` returns `{-1}`. In SymPy, `x**Rational(1, 3)` is the principal complex power, so at `x = -1` the left hand side is not `-1`; it is the principal cube root of `-1`.

## Call Path

The public call enters `sympy/solvers/solveset.py:2337` (`solveset`). Because the domain is real, the symbol is recast to a real dummy at `solveset.py:2485-2501`, then the expression is passed to `_solveset(..., _check=True)` at `solveset.py:2517`.

`_solveset` handles the `Eq` by rewriting it as `x**(1/3) + 1` at `solveset.py:1299-1300`. It then calls `_invert` from `solveset.py:1313`; `_invert` dispatches to `_invert_real`, and `_invert_real` handles the `Pow` at `solveset.py:256-291`.

## Root Cause

The responsible code is `sympy/solvers/solveset.py`, function `_invert_real`, especially `solveset.py:284-291`:

```python
if den % 2 == 1:
    root = Lambda(n, real_root(n, expo))
    res = imageset(root, g_ys)
    ...
    return _invert_real(base, res, symbol)
```

For a rational power with an odd denominator, `_invert_real` uses `real_root` semantics. That is correct for equations written with `real_root`, but it is not equivalent to SymPy's principal `Pow` for negative real bases.

The later `_check=True` pass does not catch the error. `_solveset` filters finite solutions with `domain_check` at `solveset.py:1394-1398`, but `domain_check` only checks finiteness/definedness (`solveset.py:632-696`). It does not re-evaluate whether the original equation is true.

## Mechanism

For `x**(1/3) + 1 = 0`, `_invert_real` inverts the odd-denominator power by applying `real_root(n, 1/3)` to the target set `{-1}`. This produces `{-1}` as the preimage for the base `x`.

That is the real cube-root inverse of the real-valued function, not the inverse of the principal complex power expression. Substituting `x = -1` into the original SymPy expression gives `(-1)**(1/3) + 1`, a finite complex nonzero value. Since `domain_check` regards it as finite, the candidate remains in the result.

## Suggested Fix Direction

Restrict the odd-denominator `real_root` inversion branch to expressions whose semantics are actually real-root semantics, or add a principal-branch/domain guard for non-integer rational powers over real domains. A second defensive improvement would be for the `_check=True` finite-set filtering path to verify equation truth, not just expression finiteness, when inversion used branch-sensitive transformations.

## Confidence and Caveats

The traced `_invert` result is `(x, {-1})`, and `_solveset(..., _check=True)` still returns `{-1}` because `domain_check` returns `True` at `-1`. The specific faulty transformation is located. The exact final fix may need coordination with other historical uses of `_invert_real` that intentionally model real radicals.
