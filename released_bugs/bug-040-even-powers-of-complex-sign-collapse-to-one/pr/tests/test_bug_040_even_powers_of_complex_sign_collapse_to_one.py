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

