import pytest

from spyke.math import Matrix3


def test_matrix3_identity():
    m = Matrix3.identity()
    assert all(m[i, i] == 1 for i in range(3))
    assert all(m[i, j] == 0 for i in range(3) for j in range(3) if i != j)

def test_matrix3_zero():
    m = Matrix3.zero()
    assert all(m[i, j] == 0 for i in range(3) for j in range(3))

def test_matrix3_transpose():
    m = Matrix3.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    m.transpose()
    assert m[0, 1] == 2 and m[1, 0] == 1

def test_matrix3_transposed():
    m = Matrix3.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    t = m.transposed()
    assert t[0, 1] == 2 and t[1, 0] == 1

def test_matrix3_inverse():
    m = Matrix3.identity()
    m.inverse()
    assert all(m[i, i] == 1 for i in range(3))

def test_matrix3_inversed():
    m = Matrix3.identity()
    inv = m.inversed()
    assert all(inv[i, i] == 1 for i in range(3))

def test_matrix3_determinant():
    m = Matrix3.identity()
    assert m.determinant() == pytest.approx(1.0)
