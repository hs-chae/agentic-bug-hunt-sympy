# Candidate Bug 40: Even powers of complex sign collapse to one

## Status

Confirmed.

## SymPy version

SymPy version: `1.14.0`

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

## Minimal reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Abs, I, N, sign

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

z = 1 + I
actual = sign(z) ** 2
expected = z ** 2 / Abs(z) ** 2

print("actual:", actual)
print("expected:", expected)
print("numeric actual:", N(actual, 50))
print("numeric expected:", N(expected, 50))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3

z: 1 + I
actual: 1
expected: (1 + I)**2/2
numeric actual: 1.0000000000000000000000000000000000000000000000000
numeric expected: 1.0*I
```

## Expected output

`sign(1 + I)**2` should evaluate consistently with the complex-sign definition and produce `I`, or remain unevaluated rather than returning `1`.

## Why this is wrong

For nonzero complex `z`, the complex sign is the unit complex direction `z/Abs(z)`. Therefore:

```text
sign(1 + I)**2 = ((1 + I)/Abs(1 + I))**2
                = (1 + I)**2 / 2
                = I
```

Returning `1` silently applies the real-valued identity `sign(x)**2 = 1` outside its valid domain.

## Root cause

The source-level diagnosis located the cause in `sympy/functions/elementary/complexes.py:413-419`, in `sign._eval_power`. The method returns `S.One` whenever the sign argument is known nonzero and the exponent is an even integer. That shortcut lacks a real-valuedness guard, so it also fires for unevaluated non-real complex signs such as `sign(1 + I)`. See `root_cause.md` for the full call path and mechanism.

## Independent verification

`related_bugs.py` checks the representative case plus five additional non-real complex values. For each case it compares SymPy's result with the definition `z**2/Abs(z)**2` and with an independent Python `cmath` oracle `(complex(z)/abs(complex(z)))**2`.

On the current code, every case prints `actual=1` while the definition and `cmath` produce a non-real complex value, then the script prints `Incorrect` and exits with status 1.

## Additional instantiations

The five additional instantiations are included as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_040_even_powers_of_complex_sign_collapse_to_one.py`:

```text
1 + 2*I
2 + I
-1 + I
2 - I
3/5 + I/7
```

## Affected function or subsystem

Subsystem: elementary complex functions / simplification.

Affected function: `sympy.functions.elementary.complexes.sign._eval_power`, specifically `sympy/functions/elementary/complexes.py:413-419`.

## Severity

Medium.

This is a mathematically false simplification in a core elementary complex function, but it is limited to powers of unevaluated non-real complex `sign` expressions.

## Suggested regression test

```python
import pytest

from sympy import Abs, I, N, Rational, sign


CASES = [
    1 + I,
    1 + 2 * I,
    2 + I,
    -1 + I,
    2 - I,
    Rational(3, 5) + I / 7,
]


@pytest.mark.parametrize("z", CASES)
def test_even_power_of_complex_sign_uses_complex_direction(z):
    actual = sign(z) ** 2
    expected = z ** 2 / Abs(z) ** 2

    assert abs(complex(N(actual, 80)) - complex(N(expected, 80))) < 1e-45
```

## Confidence

98%. The wrong result follows directly from the complex-sign definition, numerical checks agree, and the diagnosis identifies the exact overbroad simplification rule.
