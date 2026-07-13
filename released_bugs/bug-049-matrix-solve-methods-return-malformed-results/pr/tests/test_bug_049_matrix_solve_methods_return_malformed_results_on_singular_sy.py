import pytest

from sympy import Matrix
from sympy.matrices.exceptions import NonInvertibleMatrixError


CASES = [
    (2, 1),
    (3, 1),
    (2, 5),
    (-1, 4),
    (4, -2),
    (5, 3),
]


@pytest.mark.parametrize("a,c", CASES)
@pytest.mark.parametrize("method", ["QR", "LDL", "CRAMER"])
def test_matrix_solve_method_rejects_nonunique_singular_system(a, c, method):
    A = Matrix([[1, 1], [a, a]])
    b = Matrix([c, a*c])

    assert A.rank() == A.row_join(b).rank() == 1
    with pytest.raises(NonInvertibleMatrixError):
        A.solve(b, method=method)
