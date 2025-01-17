#pragma once
#include <Python.h>

// override default defines because they mess up formatting
#define PY_OBJECT_HEAD PyObject ob_base
#define PY_VAR_OBJECT_HEAD_INIT(type, size) .ob_base = {PyObject_HEAD_INIT(type)(size)}

#define CHECK_ARG_TYPE(arg, type, returnVal)                                                                                       \
    do                                                                                                                             \
    {                                                                                                                              \
        if (!PyObject_IsInstance((PyObject *)arg, (PyObject *)type))                                                               \
        {                                                                                                                          \
            PyErr_Format(PyExc_TypeError, "Expected argument to be of type %s, got: %s.", (type)->tp_name, Py_TYPE(arg)->tp_name); \
            return returnVal;                                                                                                      \
        }                                                                                                                          \
    } while (0)
#define CHECK_ARG_STRING(arg, returnVal)                                                                           \
    do                                                                                                             \
    {                                                                                                              \
        if (!PyUnicode_Check(arg))                                                                                 \
        {                                                                                                          \
            PyErr_Format(PyExc_TypeError, "Expected argument to be of type str, got: %s.", Py_TYPE(arg)->tp_name); \
            return returnVal;                                                                                      \
        }                                                                                                          \
    } while (0)
#define CHECK_ARG_CALLABLE(arg, returnVal)                                                                      \
    do                                                                                                          \
    {                                                                                                           \
        if (!PyCallable_Check(arg))                                                                             \
        {                                                                                                       \
            PyErr_Format(PyExc_TypeError, "Expected argument to be callable, got: %s.", Py_TYPE(arg)->tp_name); \
            return returnVal;                                                                                   \
        }                                                                                                       \
    } while (0)
#define CHECK_ARG_INT(arg, returnVal)                                                                              \
    do                                                                                                             \
    {                                                                                                              \
        if (!PyLong_Check(arg))                                                                                    \
        {                                                                                                          \
            PyErr_Format(PyExc_TypeError, "Expected argument to be of type int, got: %s.", Py_TYPE(arg)->tp_name); \
            return returnVal;                                                                                      \
        }                                                                                                          \
    } while (0)

#ifdef __GNUC__
#define UNUSED(x) __attribute__((unused)) x
#else
#define UNUSED(x) x
#endif
