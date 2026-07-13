# Fix Q.extended_real for reciprocals with possibly zero denominator

## Summary

`ask(Q.extended_real(1/(xr - 1)))` returns `True` for real `xr`, even though the allowed substitution `xr=1` gives `zoo`.

## Reproducer

Run `reproduce_bug.py`; current output proves the predicate and then shows the counterexample substitution.

## Expected behavior

The predicate should not return `True` unless the denominator is known nonzero.

## Evidence

`related_bugs.py` covers six shifted reciprocal cases.

## Suggested regression test

Use `pr/tests/test_bug_041_ask_incorrectly_proves_1_xr_1_is_extended_real_for_an_arbitr.py`.
