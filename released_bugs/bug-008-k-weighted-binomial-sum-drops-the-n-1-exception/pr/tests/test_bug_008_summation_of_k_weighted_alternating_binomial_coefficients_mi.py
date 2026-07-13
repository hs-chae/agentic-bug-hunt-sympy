import pytest
from sympy import binomial, summation, symbols

n = symbols("n", integer=True, nonnegative=True)
k = symbols("k", integer=True)
CASES = [1, 2, 3, 4, 5, 6]

@pytest.mark.parametrize("power", CASES)
def test_weighted_alternating_binomial_sum_preserves_n1_exception(power):
    closed = summation((-1)**k*k**power*binomial(n, k), (k, 0, n))
    direct = sum(((-1)**j)*(j**power)*binomial(1, j) for j in range(2))
    assert closed.subs(n, 1) == direct
