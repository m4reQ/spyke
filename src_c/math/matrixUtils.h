#pragma once
#include "matrix.h"

int PyMatrix_init_buffer(float *matrixData, Py_buffer *buffer, Py_ssize_t matrixLength);
int PyMatrix_init_sequence(float *matrixData, PyObject *sequence, Py_ssize_t matrixLength);
int PyMatrix_init_topleft_matrix(float *matrixData, _PyMatrixAbstract *matrix, Py_ssize_t matrixLength);
int PyMatrix_init_one_arg(float *matrixData, PyObject *arg, PyObject *topleftMatrixType, Py_ssize_t matrixLength);
