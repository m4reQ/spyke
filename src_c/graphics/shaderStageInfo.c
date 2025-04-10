#include "shader.h"

static PyShaderStageInfo *PyShaderStageInfo_from_file(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"type", "filepath", "use_binary", "specialize_info", NULL};

    GLenum shaderType;
    PyObject *filepathObject;
    bool useBinary = false;
    PyShaderSpecializeInfo *specializeInfo = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IU|pO!", kwNames, &shaderType, &filepathObject, &useBinary, &PyShaderSpecializeInfo_Type, &specializeInfo))
        return NULL;

    PyShaderStageInfo *result = PyObject_New(PyShaderStageInfo, cls);
    result->shaderType = shaderType;
    result->filepathOrSource = Py_NewRef(filepathObject);
    result->useBinary = useBinary;
    result->useFile = true;
    result->specializeInfo = (PyShaderSpecializeInfo *)Py_XNewRef(specializeInfo);

    return result;
}

static PyShaderStageInfo *PyShaderStageInfo_from_source(PyTypeObject *cls, PyObject *args)
{
    GLenum shaderType;
    PyObject *sourceObject;
    if (!PyArg_ParseTuple(args, "IU", &shaderType, &sourceObject))
        return NULL;

    PyShaderStageInfo *result = PyObject_New(PyShaderStageInfo, cls);
    if (result == NULL)
        return NULL;

    result = (PyShaderStageInfo *)PyObject_Init((PyObject *)result, cls);
    if (result == NULL)
        return NULL;

    result->shaderType = shaderType;
    result->filepathOrSource = Py_NewRef(sourceObject);
    result->useBinary = false;
    result->useFile = false;
    result->specializeInfo = NULL;

    return result;
}

static PyShaderStageInfo *PyShaderStageInfo_from_binary(PyTypeObject *cls, PyObject *args)
{
    GLenum shaderType;
    PyObject *source;
    PyShaderSpecializeInfo *specializeInfo;
    if (!PyArg_ParseTuple(args, "IOO!", &shaderType, &source, &PyShaderSpecializeInfo_Type, &specializeInfo))
        return NULL;

    if (!PyObject_CheckBuffer(source))
    {
        PyErr_SetString(PyExc_TypeError, "specialize_info must support buffer protocol.");
        return NULL;
    }

    PyShaderStageInfo *result = PyObject_New(PyShaderStageInfo, cls);
    if (result == NULL)
        return NULL;

    result = (PyShaderStageInfo *)PyObject_Init((PyObject *)result, cls);
    if (result == NULL)
        return NULL;

    result->shaderType = shaderType;
    result->specializeInfo = (PyShaderSpecializeInfo *)Py_NewRef(specializeInfo);
    result->filepathOrSource = Py_NewRef(source);
    result->useBinary = true;
    result->useFile = false;

    return result;
}

static void PyShaderStageInfo_dealloc(PyShaderStageInfo *self)
{
    Py_XDECREF(self->specializeInfo);
    Py_XDECREF(self->filepathOrSource);
    Py_TYPE(self)->tp_free(self);
}

PyTypeObject PyShaderStageInfo_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.ShaderStageInfo",
    .tp_basicsize = sizeof(PyShaderStageInfo),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor)PyShaderStageInfo_dealloc,
    .tp_members = (PyMemberDef[]){
        {"type", Py_T_UINT, offsetof(PyShaderStageInfo, shaderType), 0, NULL},
        {"filepath_or_source", Py_T_OBJECT_EX, offsetof(PyShaderStageInfo, filepathOrSource), 0, NULL},
        {"use_binary", Py_T_BOOL, offsetof(PyShaderStageInfo, useBinary), 0, NULL},
        {"specialize_info", _Py_T_OBJECT, offsetof(PyShaderStageInfo, specializeInfo), 0, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"from_file", (PyCFunction)PyShaderStageInfo_from_file, METH_VARARGS | METH_KEYWORDS | METH_CLASS, NULL},
        {"from_source", (PyCFunction)PyShaderStageInfo_from_source, METH_VARARGS | METH_CLASS, NULL},
        {"from_binary", (PyCFunction)PyShaderStageInfo_from_binary, METH_VARARGS | METH_CLASS, NULL},
        {0},
    },
};
