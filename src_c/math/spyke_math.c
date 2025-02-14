#include "spyke_math.h"

static PyTypeObject PyViewport2DType;
static PyTypeObject PyViewport3DType;

static int PyViewport2D_Init(PyViewport2D *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;

    if (!PyArg_ParseTuple(args, "ffff", &self->left, &self->right, &self->bottom, &self->top))
        return -1;

    return 0;
}

static PyViewport3D *PyViewport2D_ToViewport3D(PyViewport2D *self, PyObject *args)
{
    (void)args;

    PyViewport3D *result = PyObject_New(PyViewport3D, &PyViewport3DType);
    result = (PyViewport3D *)PyObject_Init(result, &PyViewport3DType);

    result->left = self->left;
    result->right = self->right;
    result->bottom = self->bottom;
    result->top = self->top;
    result->near = 0.0f;
    result->far = 0.0f;

    return result;
}

static int PyViewport3D_Init(PyViewport3D *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;

    if (!PyArg_ParseTuple(args, "ffffff", &self->left, &self->right, &self->bottom, &self->top, &self->near, &self->far))
        return -1;

    return 0;
}

static PyViewport2D *PyViewport3D_ToViewport2D(PyViewport3D *self, PyObject *args)
{
    (void)args;

    PyViewport2D *result = PyObject_New(PyViewport2D, &PyViewport2DType);
    result = (PyViewport2D *)PyObject_Init(result, &PyViewport2DType);

    result->left = self->left;
    result->right = self->right;
    result->bottom = self->bottom;
    result->top = self->top;

    return result;
}

static PyTypeObject PyViewport2DType = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.math.Viewport2D",
    .tp_basicsize = sizeof(PyViewport2D),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyViewport2D_Init,
    .tp_members = (PyMemberDef[]){
        {"left", Py_T_FLOAT, offsetof(PyViewport2D, left), 0, NULL},
        {"right", Py_T_FLOAT, offsetof(PyViewport2D, right), 0, NULL},
        {"bottom", Py_T_FLOAT, offsetof(PyViewport2D, bottom), 0, NULL},
        {"top", Py_T_FLOAT, offsetof(PyViewport2D, top), 0, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"to_viewport_3d", (PyCFunction)PyViewport2D_ToViewport3D, METH_NOARGS, NULL},
        {0},
    },
};

static PyTypeObject PyViewport3DType = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.math.Viewport3D",
    .tp_basicsize = sizeof(PyViewport3D),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyViewport3D_Init,
    .tp_members = (PyMemberDef[]){
        {"left", Py_T_FLOAT, offsetof(PyViewport3D, left), 0, NULL},
        {"right", Py_T_FLOAT, offsetof(PyViewport3D, right), 0, NULL},
        {"bottom", Py_T_FLOAT, offsetof(PyViewport3D, bottom), 0, NULL},
        {"top", Py_T_FLOAT, offsetof(PyViewport3D, top), 0, NULL},
        {"near", Py_T_FLOAT, offsetof(PyViewport3D, near), 0, NULL},
        {"far", Py_T_FLOAT, offsetof(PyViewport3D, far), 0, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"to_viewport_2d", (PyCFunction)PyViewport3D_ToViewport2D, METH_NOARGS, NULL},
        {0},
    },
};

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.math",
};

static MathAPI s_API = {
    .pyViewport2DType = &PyViewport2DType,
    .pyViewport3DType = &PyViewport3DType,
};

PyMODINIT_FUNC PyInit_math()
{
    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module ||
        !PyAPI_Add(module, &s_API) ||
        PyModule_AddType(module, &PyViewport2DType) ||
        PyModule_AddType(module, &PyViewport3DType))
        return NULL;

    return module;
}
