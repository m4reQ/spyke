import pytest

from spyke.math import Matrix2


def test_matrix2_identity():
    m = Matrix2.identity()
    assert m[0, 0] == 1 and m[1, 1] == 1
    assert m[0, 1] == 0 and m[1, 0] == 0

def test_matrix2_zero():
    m = Matrix2.zero()
    assert all(m[i, j] == 0 for i in range(2) for j in range(2))

def test_matrix2_transpose():
    m = Matrix2.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    m.transpose()
    assert m[0, 1] == 2 and m[1, 0] == 1

def test_matrix2_transposed():
    m = Matrix2.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    t = m.transposed()
    assert t[0, 1] == 2 and t[1, 0] == 1

def test_matrix2_inverse():
    m = Matrix2.identity()
    m.inverse()
    assert m[0, 0] == 1 and m[1, 1] == 1

def test_matrix2_inversed():
    m = Matrix2.identity()
    inv = m.inversed()
    assert inv[0, 0] == 1 and inv[1, 1] == 1

def test_matrix2_determinant():
    m = Matrix2.identity()
    assert m.determinant() == pytest.approx(1.0)
