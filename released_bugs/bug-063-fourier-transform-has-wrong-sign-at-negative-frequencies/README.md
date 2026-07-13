# Candidate Bug 63: fourier_transform(cos(x)/(x**2 + 1)) has the wrong sign at negative frequencies

## Status

Confirmed.

## SymPy version

SymPy version: 1.14.0. `SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`. SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`. Python executable: `python3`. Commit hash: None.

## Minimal reproducer

See `reproduce_bug.py`.

```python
x, k = symbols("x k", real=True)
F = fourier_transform(cos(x)/(x**2 + 1), x, k)
value = Rational(-1, 3)
expected = pi*(exp(-Abs(2*pi*value - 1)) + exp(-Abs(2*pi*value + 1)))/2
print(N(F.subs(k, value), 50))
print(N(expected, 50))
print(N(F.subs(k, value) - expected, 50))
```

## Actual output

```text
SymPy at k=-1/3: -0.59697240701635906558464748995740185380690547910845 + 2.2927016814328156775234560803181663759131427061003e-64*I
shift-theorem expected: 0.59697240701635906558464748995740185380690547910845
difference: -1.1939448140327181311692949799148037076138109582169 + 2.2927016814328156775234560803181663759131427061003e-64*I
```

## Expected output

At `k = -1/3`, the transform should be positive:

```text
pi/2*(exp(-Abs(2*pi*(-1/3) - 1)) + exp(-Abs(2*pi*(-1/3) + 1)))
= 0.59697240701635906558464748995740185380690547910845
```

## Why this is wrong

With SymPy's convention, the Fourier transform is `Integral(f(x)*exp(-2*pi*I*x*k), (x, -oo, oo))`. The standard transform `F[1/(x**2 + 1)](k) = pi*exp(-2*pi*Abs(k))`, combined with `cos(x) = (exp(I*x) + exp(-I*x))/2`, gives `pi/2*(exp(-Abs(2*pi*k - 1)) + exp(-Abs(2*pi*k + 1)))`. The integrand is also real and even, so its transform must be real and even. SymPy's negative value at `k = -1/3` violates both the shift-theorem result and evenness.

## Root cause

The diagnosis in `root_cause.md` narrows the issue to the Meijer definite integration path in `sympy/integrals/meijerint.py:1834` and `sympy/integrals/meijerint.py:2048`. The half-line Meijer formulas introduce branch-sensitive factors involving `polar_lift(k)**2`, `Abs(k)`, and a denominator `k`; after transform simplification the public result retains an overall `Abs(k)/k` sign factor. That makes the result odd in `k` although the transform should be even.

This is an instance of a known meijerg Fourier-transform `abs/k` sign family. Open issue [sympy/sympy#25137](https://github.com/sympy/sympy/issues/25137) ("Integrate returns wrong answer for fourier transform of sinc") documents the same artifact under `real=True`, with a maintainer comment identifying the root cause as a branch-dependent `sqrt(1/y**2)` collapsing to `sign(y) = abs(y)/y`. The specific integrand `cos(x)/(x**2 + 1)` here is plausibly a new instance of that family.

## Independent verification

`related_bugs.py` computes the SymPy transform and compares it against the shift-theorem formula using `mpmath` arithmetic. It also prints the evenness difference against the positive frequency counterpart.

## Additional instantiations

The same negative-frequency sign error is tested for `-1/4`, `-1/2`, `-2/3`, `-1`, and `-3/2`.

## Affected function or subsystem

Integral transforms / Fourier transform through Meijer definite integration: `sympy/integrals/meijerint.py:1834` and `sympy/integrals/meijerint.py:2048`, with final exposure through `fourier_transform`.

## Severity

High. SymPy returns the negative of a Fourier transform value for a simple real even integrand.

## Suggested regression test

See `pr/tests/test_bug_063_fourier_transform_cos_x_x_2_1_has_the_wrong_sign_at_negative.py`.

## Confidence

94%. The shift-theorem derivation is direct and the diagnosis traces the bad sign factor, though the exact Meijer substep is narrowed rather than isolated to one local rewrite.
