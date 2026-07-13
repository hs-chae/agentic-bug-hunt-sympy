---
diagnosis_status: located
confidence: 96
location: sympy/solvers/solveset.py:462-474
---

## Candidate Summary

`solveset(sec(x), x, domain=S.Complexes)` returns `{nan}`. The equation `sec(x) = 0` has no finite complex solution, and `nan` is not a solution.

## Call Path

The public call `solveset(sec(x), x, domain=S.Complexes)` reaches `_solveset` in `sympy/solvers/solveset.py`. The fallback inversion path calls `invert_complex(f, 0, symbol, domain)` at `sympy/solvers/solveset.py:2321-2324`.

`invert_complex` delegates to `_invert_complex`, which recognizes `sec(x)` as a trigonometric function at `sympy/solvers/solveset.py:577-578` and calls `_invert_trig_hyp_complex`.

## Root Cause

`_invert_trig_hyp_complex` treats `sec` like an ordinary invertible trig function and does not exclude values outside the range of `sec`.

The bad logic is in `sympy/solvers/solveset.py:462-466`:

For `(cos, sec)`, it selects `acos` for `cos` and `asec` for `sec`, then returns the families `2*n*pi + F(a)` and `2*n*pi - F(a)`.

For the equation `sec(x) = 0`, this applies `asec(0)`. In SymPy 1.14.0, `asec(0)` evaluates to `zoo`; the generated image-set expressions contain `2*n*pi +/- zoo`, which simplify through set construction to `{nan}`. There is no guard that `sec` can only take nonzero finite values, and no post-filter removing non-finite or `nan` candidates.

## Mechanism

The inversion path transforms the impossible equation `sec(x) = 0` into:

`x = 2*n*pi +/- asec(0)`

Since `asec(0)` is not a finite inverse value, arithmetic with `zoo` produces `nan`. `_invert_complex` then returns `(x, {nan})`, and `_solveset` returns that set directly.

Mathematically, `sec(x) = 1/cos(x)`. For finite complex `x`, `cos(x)` is finite, so `1/cos(x)` is never zero. At poles, `sec` is undefined/infinite, not zero.

## Suggested Fix Direction

Add range/singularity guards in `_invert_trig_hyp_complex` for reciprocal trig functions. For `sec` and `csc`, exclude `0` from `g_ys` before applying `asec`/`acsc`; if the finite set becomes empty, return `S.EmptySet`. A defensive cleanup could also discard `nan`, `oo`, `-oo`, and `zoo` from finite solution sets.

## Confidence and Caveats

The reproducer's `invert_complex(sec(x), 0, x)` directly returns `(x, {nan})`, and `asec(0)` directly returns `zoo`, so the source-level mechanism is exact.
