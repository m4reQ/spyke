#include "matrixUtils.h"

int PyMatrix_init_buffer(float *matrixData, Py_buffer *buffer, Py_ssize_t matrixLength)
{
    const int result = PyBuffer_ToContiguous(matrixData, buffer, matrixLength * matrixLength * sizeof(float), 'C');
    PyBuffer_Release(buffer);

    return result;
}

int PyMatrix_init_sequence(float *matrixData, PyObject *sequence, Py_ssize_t matrixLength)
{
    Py_ssize_t nValues = PySequence_Fast_GET_SIZE(sequence);
    if (nValues != matrixLength * matrixLength)
    {
        PyErr_Format(PyExc_ValueError, "Expected values count to be %zu, got %zu.", matrixLength * matrixLength, nValues);
        Py_DecRef(sequence);
        return -1;
    }

    for (Py_ssize_t i = 0; i < nValues; i++)
    {
        const float value = (float)PyFloat_AsDouble(PySequence_Fast_GET_ITEM(sequence, i));
        if (PyErr_Occurred())
        {
            Py_DecRef(sequence);
            return -1;
        }

        matrixData[i] = value;
    }

    Py_DecRef(sequence);
    return 0;
}

int PyMatrix_init_topleft_matrix(float *matrixData, _PyMatrixAbstract *matrix, Py_ssize_t matrixLength)
{
    memset(matrixData, 0, matrixLength * matrixLength * sizeof(float));

    for (Py_ssize_t i = 0; i < matrixLength - 1; i++)
    {
        const Py_ssize_t selfRowSize = matrixLength;
        const Py_ssize_t otherRowSize = (matrixLength - 1);
        memcpy(&matrixData[selfRowSize * i], &matrix->data[otherRowSize * i], otherRowSize * sizeof(float));
    }

    return 0;
}

int PyMatrix_init_one_arg(float *matrixData, PyObject *arg, PyObject *topleftMatrixType, Py_ssize_t matrixLength)
{
    if (matrixLength != 2 && PyObject_IsInstance(arg, topleftMatrixType))
        return PyMatrix_init_topleft_matrix(matrixData, (_PyMatrixAbstract *)arg, matrixLength);

    Py_buffer buffer = {0};
    if (PyObject_GetBuffer(arg, &buffer, PyBUF_READ) != -1)
        return PyMatrix_init_buffer(matrixData, &buffer, matrixLength);

    PyErr_Clear();

    PyObject *argAsSequence = PySequence_Fast(arg, "");
    if (argAsSequence != NULL)
        return PyMatrix_init_sequence(matrixData, argAsSequence, matrixLength);

    PyErr_Format(PyExc_TypeError, "Expected matrix argument to be either t.Sequence[float], Matrix%zu or support buffer protocol, got: %s", matrixLength - 1, Py_TYPE(arg)->tp_name);
    return -1;
}
