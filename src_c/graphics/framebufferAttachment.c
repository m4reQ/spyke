#include "framebuffer.h"

bool _PyFramebufferAttachment_IsDepthAttachment(PyFramebufferAttachment *attachment)
{
    return attachment->attachment == GL_DEPTH_ATTACHMENT ||
           attachment->attachment == GL_STENCIL_ATTACHMENT ||
           attachment->attachment == GL_DEPTH_STENCIL_ATTACHMENT;
}

GLenum _PyFramebufferAttachment_ObjectToAttachmentPoint(PyObject *value)
{
    if (PyLong_CheckExact(value))
        return GL_COLOR_ATTACHMENT0 + PyLong_AsUnsignedLong(value);
    else if (PyLong_Check(value))
        return PyLong_AsUnsignedLong(value);

    PyErr_Format(PyExc_TypeError, "Expected attachment point to be of type int, got: %s.", Py_TYPE(value)->tp_name);
    return (GLenum)-1;
}

static int PyFramebufferAttachment_init(PyFramebufferAttachment *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"width", "height", "format", "attachment", "samples", "min_filter", "mag_filter", "use_renderbuffer", "is_writable", NULL};

    PyObject *attachment;
    self->samples = 1;
    self->minFilter = GL_NEAREST;
    self->magFilter = GL_NEAREST;
    self->isRenderbuffer = false;
    self->isWritable = true;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iiIO|iIIpp", kwNames, &self->width, &self->height, &self->format, &attachment, &self->samples, &self->minFilter, &self->magFilter, &self->isRenderbuffer, &self->isWritable))
        return -1;

    self->attachment = _PyFramebufferAttachment_ObjectToAttachmentPoint(attachment);
    if (self->attachment == -1)
        return -1;

    return 0;
}

static PyObject *PyFramebufferAttachment_size_getter(PyFramebufferAttachment *self, void *closure)
{
    (void)closure;
    return PyTuple_Pack(2, PyLong_FromLong(self->width), PyLong_FromLong(self->height));
}

static int PyFramebufferAttachment_size_setter(PyFramebufferAttachment *self, PyObject *value, void *closure)
{
    (void)closure;
    return PyArg_ParseTuple(value, "ii", &self->width, &self->height) ? 0 : -1;
}

static PyObject *PyFramebufferAttachment_is_resizable_getter(PyFramebufferAttachment *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(self->width == 0 && self->height == 0);
}

static PyObject *PyFramebufferAttachment_is_depth_attachment_getter(PyFramebufferAttachment *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(_PyFramebufferAttachment_IsDepthAttachment(self));
}

static PyObject *PyFramebufferAttachment_is_color_attachment_getter(PyFramebufferAttachment *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(!_PyFramebufferAttachment_IsDepthAttachment(self));
}

static PyObject *PyFramebufferAttachment_is_multisampled_getter(PyFramebufferAttachment *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(self->samples > 1);
}

PyTypeObject PyFramebufferAttachment_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.FramebufferAttachment",
    .tp_basicsize = sizeof(PyFramebufferAttachment),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyFramebufferAttachment_init,
    .tp_members = (PyMemberDef[]){
        {"width", Py_T_INT, offsetof(PyFramebufferAttachment, width), 0, NULL},
        {"height", Py_T_INT, offsetof(PyFramebufferAttachment, height), 0, NULL},
        {"samples", Py_T_INT, offsetof(PyFramebufferAttachment, samples), 0, NULL},
        {"format", Py_T_UINT, offsetof(PyFramebufferAttachment, format), 0, NULL},
        {"min_filter", Py_T_UINT, offsetof(PyFramebufferAttachment, minFilter), 0, NULL},
        {"mag_filter", Py_T_UINT, offsetof(PyFramebufferAttachment, magFilter), 0, NULL},
        {"attachment", Py_T_UINT, offsetof(PyFramebufferAttachment, attachment), 0, NULL},
        {"use_renderbuffer", Py_T_BOOL, offsetof(PyFramebufferAttachment, isRenderbuffer), 0, NULL},
        {"is_writable", Py_T_BOOL, offsetof(PyFramebufferAttachment, isWritable), 0, NULL},
        {0},
    },
    .tp_getset = (PyGetSetDef[]){
        {"size", (getter)PyFramebufferAttachment_size_getter, (setter)PyFramebufferAttachment_size_setter, NULL, NULL},
        {"is_resizable", (getter)PyFramebufferAttachment_is_resizable_getter, NULL, NULL, NULL},
        {"is_depth_attachment", (getter)PyFramebufferAttachment_is_depth_attachment_getter, NULL, NULL, NULL},
        {"is_color_attachment", (getter)PyFramebufferAttachment_is_color_attachment_getter, NULL, NULL, NULL},
        {"is_multisampled", (getter)PyFramebufferAttachment_is_multisampled_getter, NULL, NULL, NULL},
        {0},
    },
};
