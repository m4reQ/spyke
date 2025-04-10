#include "viewport.h"

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

    PyViewport3D *result = PyObject_New(PyViewport3D, &PyViewport3D_Type);
    result = (PyViewport3D *)PyObject_Init((PyObject *)result, &PyViewport3D_Type);

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

    PyViewport2D *result = PyObject_New(PyViewport2D, &PyViewport2D_Type);
    result = (PyViewport2D *)PyObject_Init(result, &PyViewport2D_Type);

    result->left = self->left;
    result->right = self->right;
    result->bottom = self->bottom;
    result->top = self->top;

    return result;
}

PyTypeObject PyViewport2D_Type = {
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

PyTypeObject PyViewport3D_Type = {
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
