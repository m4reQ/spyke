#include "texture.h"

static int PyTextureSpec_init(PyTextureSpec *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {
        "target",
        "width",
        "height",
        "internal_format",
        /* optional */
        "depth",
        "samples",
        "mipmaps",
        "min_filter",
        "mag_filter",
        "wrap_mode",
        NULL,
    };

    self->depth = 1;
    self->samples = 1;
    self->mipmaps = 1;
    self->minFilter = GL_LINEAR;
    self->magFilter = GL_LINEAR;
    self->wrapMode = GL_CLAMP_TO_EDGE;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "IiiI|iiiIII", kwNames,
            &self->target,
            &self->width, &self->height, &self->internalFormat,
            &self->depth, &self->samples, &self->mipmaps,
            &self->minFilter, &self->magFilter, &self->wrapMode))
        return -1;

    if (self->samples <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Samples count has to be higher than 0.");
        return -1;
    }

    if (self->mipmaps <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Mipmaps count has to be higher than 0.");
        return -1;
    }

    if (self->width <= 0 || self->height <= 0 || self->depth <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Texture size has to be higher than 0.");
        return -1;
    }

    return 0;
}

static PyObject *PyTextureSpec_size_getter(PyTextureSpec *self, void *closure)
{
    (void)closure;
    return PyTuple_Pack(3, PyLong_FromLong(self->width), PyLong_FromLong(self->height), PyLong_FromLong(self->depth));
}

static PyObject *PyTextureSpec_is_multisampled_getter(PyTextureSpec *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(self->samples > 1);
}

extern PyTypeObject PyTextureSpec_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_name = "spyke.graphics.gl.TextureSpec",
    .tp_basicsize = sizeof(PyTextureSpec),
    .tp_init = (initproc)PyTextureSpec_init,
    .tp_members = (PyMemberDef[]){
        {"target", Py_T_UINT, offsetof(PyTextureSpec, target), 0, NULL},
        {"width", Py_T_INT, offsetof(PyTextureSpec, width), 0, NULL},
        {"height", Py_T_INT, offsetof(PyTextureSpec, height), 0, NULL},
        {"depth", Py_T_INT, offsetof(PyTextureSpec, depth), 0, NULL},
        {"samples", Py_T_INT, offsetof(PyTextureSpec, samples), 0, NULL},
        {"mipmaps", Py_T_INT, offsetof(PyTextureSpec, mipmaps), 0, NULL},
        {"internal_format", Py_T_UINT, offsetof(PyTextureSpec, internalFormat), 0, NULL},
        {"min_filter", Py_T_UINT, offsetof(PyTextureSpec, minFilter), 0, NULL},
        {"mag_filter", Py_T_UINT, offsetof(PyTextureSpec, magFilter), 0, NULL},
        {"wrap_mode", Py_T_UINT, offsetof(PyTextureSpec, wrapMode), 0, NULL},
        {0},
    },
    .tp_getset = (PyGetSetDef[]){
        {"size", (getter)PyTextureSpec_size_getter, NULL, NULL, NULL},
        {"is_multisampled", (getter)PyTextureSpec_is_multisampled_getter, NULL, NULL, NULL},
        {0},
    },
};
