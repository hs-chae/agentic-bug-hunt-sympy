import pytest

from sympy import Abs, N, Rational, cos, exp, fourier_transform, pi, symbols

x, k = symbols("x k", real=True)
TRANSFORM = fourier_transform(cos(x) / (x**2 + 1), x, k)


@pytest.mark.parametrize(
    "value",
    [
        Rational(-1, 3),
        Rational(-1, 4),
        Rational(-1, 2),
        Rational(-2, 3),
        Rational(-1, 1),
        Rational(-3, 2),
    ],
)
def test_fourier_transform_shifted_cauchy_kernel_negative_frequencies(value):
    expected = pi * (exp(-Abs(2*pi*value - 1)) + exp(-Abs(2*pi*value + 1))) / 2
    assert abs(complex(N(TRANSFORM.subs(k, value) - expected, 80))) < 1e-40
