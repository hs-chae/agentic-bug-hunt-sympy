---
diagnosis_status: located
confidence: 93
location: sympy/concrete/summations.py:1170
---

## Candidate Summary

`Sum(1/(k*(k - 1)), (k, 0, oo)).doit()` returns `-1`, even though the terms at `k = 0` and `k = 1` are undefined.

## Call Path

The public call is `Sum(...).doit()`. `Sum.doit` calls `eval_sum(f, (k, 0, oo))` at `sympy/concrete/summations.py:268`. `eval_sum` calls `eval_sum_symbolic(f.expand(), ...)`. `eval_sum_symbolic` applies `apart`, splits the Add into two terms, and calls `telescopic` at `summations.py:1163-1171` (`eval_sum_symbolic` is at line 1129).

## Root Cause

The faulty logic is the telescoping path in `sympy/concrete/summations.py:1163-1171`, with endpoint construction in `telescopic_direct` at `summations.py:946-967` (endpoint `Add` at line 967).

For this summand, `apart(1/(k*(k - 1)), k)` gives `1/(k - 1) - 1/k`. `telescopic` recognizes `-1/k` as the shifted negative of `1/(k - 1)` and immediately returns the endpoint expression via `telescopic_direct`. There is no check that the original summand, or the decomposed telescoping terms used for cancellation, are finite throughout the summation range.

## Mechanism

For limits `(k, 0, oo)`, `telescopic_direct` returns `L.subs(k, 0) + R.subs(k, oo)` for shift `1`, giving `-1 + 0 = -1`.

That endpoint formula assumes all interior terms exist and cancel pairwise. Here the original summand has poles at `k = 0` and `k = 1`, and the partial-fraction terms contain the singular pieces that the telescoping shortcut skips. The undefined initial terms are therefore hidden by the closed form.

## Suggested Fix Direction

Before accepting a telescoping result, check for poles of the original summand in the summation range, especially finite starting terms for infinite sums. If singular terms are present, return an unevaluated sum, `zoo`, or another undefined result rather than applying telescopic cancellation.

## Confidence and Caveats

Confidence is high: the probe showed `telescopic(...)`, `eval_sum_symbolic(...)`, and `eval_sum(...)` all returning `-1` on this exact path. I did not decide the best public-facing undefined value.
