import pytest

from sympy import Interval, Rational, S, sqrt, tan, symbols
from sympy.calculus.util import function_range


@pytest.mark.parametrize(
    "bound",
    [S.One, Rational(1, 2), Rational(1, 3), Rational(2, 3), Rational(3, 4), Rational(1, 4)],
)
def test_function_range_sqrt_tan_squared_includes_cusp_value(bound):
    x = symbols("x")
    assert function_range(sqrt(tan(x)**2), x, Interval(-bound, bound)) == Interval(0, tan(bound))
