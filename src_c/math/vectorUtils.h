#pragma once
#include "vector.h"

int PyVector_init_buffer(float *vectorData, Py_buffer *buffer, Py_ssize_t vectorLength);
int PyVector_init_sequence(float *vectorData, PyObject *sequence, Py_ssize_t vectorLength);
int PyVector_init_float(float *vectorData, PyObject *floatObject, Py_ssize_t vectorLength);
int PyVector_init_one_arg(float *data, PyObject *arg, Py_ssize_t vectorLength);
