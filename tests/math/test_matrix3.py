import struct

import pytest

from spyke.math import Matrix2, Matrix3, Vector3


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

def test_matrix3_constructor_buffer():
    data = struct.pack('9f', *(float(i) for i in range(9)))
    m = Matrix3(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(9))

def test_matrix3_constructor_list():
    data = [float(i) for i in range(9)]
    m = Matrix3(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(9))

def test_matrix3_constructor_tuple():
    data = tuple(float(i) for i in range(9))
    m = Matrix3(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(9))

def test_matrix3_constructor_topleft():
    topleft = Matrix2.identity()
    m = Matrix3(topleft)

    assert m[0, 0] == 1.0 and m[1, 1] == 1.0

def test_matrix3_constructor_vectors():
    m = Matrix3(
        Vector3(1.0, 0.0, 0.0),
        Vector3(0.0, 2.0, 0.0),
        Vector3(0.0, 0.0, 3.0))

    assert m[0, 0] == 1.0 and m[1, 1] == 2.0 and m[2, 2] == 3.0
