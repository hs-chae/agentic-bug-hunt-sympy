import pytest

from sympy import Heaviside, exp, laplace_transform, simplify, symbols


@pytest.mark.parametrize("cutoff", [2, 1, 3, 4, 5, 6])
def test_laplace_transform_symbolic_heaviside_closing_step_after_substitution(cutoff):
    t = symbols("t", real=True)
    s = symbols("s", positive=True)
    a = symbols("a")

    symbolic_transform = laplace_transform(Heaviside(a - t), t, s, noconds=True)
    actual = symbolic_transform.subs(a, cutoff)
    expected = (1 - exp(-cutoff*s))/s

    assert simplify(actual - expected) == 0
