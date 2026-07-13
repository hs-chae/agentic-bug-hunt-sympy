import pytest

from sympy import S, asec, diff, integrate, simplify, symbols


@pytest.mark.parametrize(
    "value",
    [
        S(-2),
        S(-3),
        -S(3) / 2,
        S(-4),
        -S(5) / 2,
        S(-10),
    ],
)
def test_integrate_asec_antiderivative_on_negative_real_branch(value):
    x = symbols("x", real=True)
    residual = diff(integrate(asec(x), x), x) - asec(x)
    assert simplify(residual.subs(x, value)) == 0
