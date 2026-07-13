import pytest
from sympy import Matrix, symbols

a, b = symbols("a b")

@pytest.mark.parametrize("offdiag", [1, 2, 3, 4, 5, 6])
def test_is_diagonalizable_does_not_ignore_eigenvalue_collision(offdiag):
    M = Matrix([[a, offdiag], [0, b]])
    assert not (M.is_diagonalizable() is True and M.subs(b, a).is_diagonalizable() is False)
