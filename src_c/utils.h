#pragma once
#include <Python.h>

// override default defines because they mess up formatting
#define PY_OBJECT_HEAD PyObject ob_base
#define PY_VAR_OBJECT_HEAD_INIT(type, size) .ob_base = {PyObject_HEAD_INIT(type)(size)}

#define ADD_TYPE_OR_FAIL(module, type)   \
    if (PyModule_AddType(module, &type)) \
    return NULL
#define ADD_ENUM_OR_FAIL(module, name, values, isFlag) \
    if (!PyEnum_Add(module, name, values, isFlag))     \
    return NULL

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

#define CHECK_ARG_FLOAT(arg, returnVal)                                                                              \
    do                                                                                                               \
    {                                                                                                                \
        if (!PyFloat_Check(arg))                                                                                     \
        {                                                                                                            \
            PyErr_Format(PyExc_TypeError, "Expected argument to be of type float, got: %s.", Py_TYPE(arg)->tp_name); \
            return returnVal;                                                                                        \
        }                                                                                                            \
    } while (0)

#define FLAG_IS_SET(flags, x) (((flags) & (x)) == (x))

#define MACRO_CONCAT_NX(A, B) A##B
#define MACRO_CONCAT(A, B) MACRO_CONCAT_NX(A, B)
#define MACRO_STRINGIFY_NX(A) #A
#define MACRO_STRINGIFY(A) MACRO_STRINGIFY_NX(A)

#ifdef __GNUC__
#define UNUSED(x) __attribute__((unused)) x
#else
#define UNUSED(x) x
#endif
