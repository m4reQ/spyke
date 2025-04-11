#include "vectorUtils.h"

int PyVector_init_buffer(float *vectorData, Py_buffer *buffer, Py_ssize_t vectorLength)
{
    return PyBuffer_ToContiguous(vectorData, buffer, vectorLength * sizeof(float), 'C');
}

int PyVector_init_sequence(float *vectorData, PyObject *sequence, Py_ssize_t vectorLength)
{
    const Py_ssize_t nItems = PySequence_Fast_GET_SIZE(sequence);
    if (nItems != vectorLength)
    {
        PyErr_Format(PyExc_ValueError, "Invalid values sequence length. Expected %d items, got: %d", vectorLength, nItems);
        return -1;
    }

    for (Py_ssize_t i = 0; i < nItems; i++)
    {
        PyObject *floatItem = PyNumber_Float(PySequence_Fast_GET_ITEM(sequence, i));
        if (floatItem == NULL)
        {
            PyErr_Format(PyExc_ValueError, "Invalid value at index %d: value must be convertible to float.", i);
            return -1;
        }

        vectorData[i] = (float)PyFloat_AS_DOUBLE(floatItem);
        Py_DecRef(floatItem);
    }

    return 0;
}

int PyVector_init_float(float *vectorData, PyObject *floatObject, Py_ssize_t vectorLength)
{
    const float value = (float)PyFloat_AS_DOUBLE(floatObject);
    for (Py_ssize_t i = 0; i < vectorLength; i++)
        vectorData[i] = value;

    return 0;
}

int PyVector_init_one_arg(float *data, PyObject *arg, Py_ssize_t vectorLength)
{
    Py_buffer buffer = {0};
    if (PyObject_GetBuffer(arg, &buffer, PyBUF_READ) != -1)
    {
        int result = PyVector_init_buffer(data, &buffer, vectorLength);
        PyBuffer_Release(&buffer);

        return result;
    }

    PyErr_Clear();

    PyObject *argFloat = PyNumber_Float(arg);
    if (argFloat != NULL)
    {
        int result = PyVector_init_float(data, argFloat, vectorLength);
        Py_DecRef(argFloat);

        return result;
    }

    PyErr_Clear();

    PyObject *argSequence = PySequence_Fast(arg, "");
    if (argSequence != NULL)
    {
        int result = PyVector_init_sequence(data, argSequence, vectorLength);
        Py_DecRef(argSequence);

        return result;
    }

    PyErr_Format(PyExc_TypeError, "Expected argument to be either float, t.Sequence[float] or support buffer protocol, got: %s.", Py_TYPE(arg)->tp_name);
    return -1;
}
