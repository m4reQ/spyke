#include "framebuffer.h"

static void DeleteFramebuffer(PyFramebuffer *framebuffer)
{
    for (size_t i = 0; i < framebuffer->nAttachments; i++)
    {
        Attachment *attachment = &framebuffer->attachments[i];
        if (attachment->settings->isRenderbuffer)
            glDeleteRenderbuffers(1, &attachment->id);
        else
            glDeleteTextures(1, &attachment->id);
    }

    glDeleteFramebuffers(1, &framebuffer->id);
}

static void InitializeFramebuffer(PyFramebuffer *framebuffer)
{
    glCreateFramebuffers(1, &framebuffer->id);

    GLenum *drawBuffers = PyMem_Malloc(sizeof(GLenum) * framebuffer->nAttachments);
    GLsizei nDrawBuffers = 0;

    for (size_t i = 0; i < framebuffer->nAttachments; i++)
    {
        Attachment *attachment = &framebuffer->attachments[i];
        PyFramebufferAttachment *settings = attachment->settings;

        const bool isMultisampled = settings->samples > 1;
        GLsizei width = framebuffer->width;
        GLsizei height = framebuffer->height;
        if (settings->width != 0 && settings->height != 0)
        {
            width = settings->width;
            height = settings->height;
        }

        if (settings->isRenderbuffer)
        {
            glCreateRenderbuffers(1, &attachment->id);

            if (isMultisampled)
                glNamedRenderbufferStorageMultisample(attachment->id, settings->samples, settings->format, width, height);
            else
                glNamedRenderbufferStorage(attachment->id, settings->format, width, height);

            glNamedFramebufferRenderbuffer(framebuffer->id, settings->attachment, GL_RENDERBUFFER, attachment->id);
        }
        else
        {
            const GLenum textureTarget = isMultisampled ? GL_TEXTURE_2D_MULTISAMPLE : GL_TEXTURE_2D;
            glCreateTextures(textureTarget, 1, &attachment->id);

            if (isMultisampled)
                glTextureStorage2DMultisample(attachment->id, settings->samples, settings->format, width, height, GL_TRUE);
            else
                glTextureStorage2D(attachment->id, 1, settings->format, width, height);

            glTextureParameteri(attachment->id, GL_TEXTURE_MIN_FILTER, settings->minFilter);
            glTextureParameteri(attachment->id, GL_TEXTURE_MAG_FILTER, settings->magFilter);
            glTextureParameteri(attachment->id, GL_TEXTURE_MAX_LEVEL, 1);
            glTextureParameteri(attachment->id, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
            glTextureParameteri(attachment->id, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
            glTextureParameteri(attachment->id, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

            glNamedFramebufferTexture(framebuffer->id, settings->attachment, attachment->id, 0);
        }

        if (settings->isWritable && !_PyFramebufferAttachment_IsDepthAttachment(settings))
        {
            drawBuffers[nDrawBuffers] = settings->attachment;
            nDrawBuffers++;
        }
    }

    if (nDrawBuffers == 0)
        glNamedFramebufferDrawBuffer(framebuffer->id, GL_NONE);
    else
        glNamedFramebufferDrawBuffers(framebuffer->id, nDrawBuffers, drawBuffers);

    PyMem_Free(drawBuffers);
}

static const char *FramebufferStatusToString(GLenum status)
{
    switch (status)
    {
    case GL_FRAMEBUFFER_UNDEFINED:
        return "GL_FRAMEBUFFER_UNDEFINED";
    case GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        return "GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT";
    case GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        return "GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT";
    case GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
        return "GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER";
    case GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
        return "GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER";
    case GL_FRAMEBUFFER_UNSUPPORTED:
        return "GL_FRAMEBUFFER_UNSUPPORTED";
    case GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
        return "GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE";
    case GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
        return "GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS";
    default:
        return "UNKNOWN";
    }
}

static bool ValidateFramebuffer(PyFramebuffer *framebuffer)
{
    GLenum status = glCheckNamedFramebufferStatus(framebuffer->id, GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to create framebuffer (id: %d): %s.", framebuffer->id, FramebufferStatusToString(status));
        return false;
    }

    return true;
}

static Attachment *FindAttachment(PyFramebuffer *framebuffer, GLenum attachmentPoint)
{
    for (size_t i = 0; i < framebuffer->nAttachments; i++)
    {
        Attachment *attachment = &framebuffer->attachments[i];
        if (attachment->settings->attachment == attachmentPoint)
            return attachment;
    }

    PyErr_Format(PyExc_RuntimeError, "No attachment bound to attachment point %d.", attachmentPoint);
    return NULL;
}

static Py_ssize_t GetGLTypeSize(GLenum type)
{
    switch (type)
    {
    case GL_BYTE:
        return sizeof(GLbyte);
    case GL_UNSIGNED_BYTE:
        return sizeof(GLubyte);
    case GL_SHORT:
        return sizeof(GLshort);
    case GL_UNSIGNED_SHORT:
        return sizeof(GLushort);
    case GL_INT:
        return sizeof(GLint);
    case GL_UNSIGNED_INT:
        return sizeof(GLuint);
    case GL_FIXED:
        return sizeof(GLfixed);
    case GL_HALF_FLOAT:
        return sizeof(GLhalf);
    case GL_FLOAT:
        return sizeof(GLfloat);
    case GL_DOUBLE:
        return sizeof(GLdouble);
    default:
        return 0;
    }
}

static int PyFramebuffer_init(PyFramebuffer *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;

    PyObject *attachments;
    if (!PyArg_ParseTuple(args, "O!ii", &PyList_Type, &attachments, &self->width, &self->height))
        return -1;

    self->nAttachments = (size_t)PyList_GET_SIZE(attachments);
    self->attachments = PyMem_Calloc(self->nAttachments, sizeof(Attachment));

    for (size_t i = 0; i < self->nAttachments; i++)
    {
        PyObject *attachment = PyList_GET_ITEM(attachments, i);
        if (!PyObject_IsInstance(attachment, (PyObject *)&PyFramebufferAttachment_Type))
        {
            PyErr_Format(PyExc_TypeError, "Expected attachments[%d] to be of type %s, got: %s.", i, PyFramebufferAttachment_Type.tp_name, Py_TYPE(attachment)->tp_name);
            return -1;
        }

        self->attachments[i].settings = (PyFramebufferAttachment *)Py_NewRef(attachment);
    }

    InitializeFramebuffer(self);
    if (!ValidateFramebuffer(self))
        return -1;

    return 0;
}

static void PyFramebuffer_dealloc(PyFramebuffer *self)
{
    if (self->attachments != NULL)
    {
        for (size_t i = 0; i < self->nAttachments; i++)
        {
            Py_XDECREF(self->attachments[i].settings);
        }

        PyMem_Free(self->attachments);
    }

    Py_TYPE(self)->tp_free(self);
}

static PyObject *PyFramebuffer_size_getter(PyFramebuffer *self, void *closure)
{
    (void)closure;
    return PyTuple_Pack(2, PyLong_FromLong(self->width), PyLong_FromLong(self->height));
}

static PyObject *PyFramebuffer_set_debug_name(PyFramebuffer *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *nameStr = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectLabel(GL_FRAMEBUFFER, self->id, nameLength, nameStr);

    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_delete(PyFramebuffer *self, PyObject *args)
{
    (void)args;
    DeleteFramebuffer(self);
    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_bind(PyFramebuffer *self, PyObject *args)
{
    (void)args;
    glBindFramebuffer(GL_FRAMEBUFFER, self->id);
    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_unbind(PyFramebuffer *self, PyObject *args)
{
    (void)self;
    (void)args;
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_resize(PyFramebuffer *self, PyObject *const *args, Py_ssize_t nArgs)
{
    GLsizei width, height;
    if (!_PyArg_ParseStack(args, nArgs, "ii", &width, &height))
        return NULL;

    if (width == 0 || height == 0 || (width == self->width && height == self->height))
        Py_RETURN_NONE;

    self->width = width;
    self->height = height;

    DeleteFramebuffer(self);
    InitializeFramebuffer(self);

    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_get_attachment(PyFramebuffer *self, PyObject *pyAttachmentPoint)
{
    const GLenum attachmentPoint = _PyFramebufferAttachment_ObjectToAttachmentPoint(pyAttachmentPoint);
    if (attachmentPoint == -1)
        return NULL;

    const Attachment *attachment = FindAttachment(self, attachmentPoint);
    if (attachment == NULL)
        return NULL;

    return Py_NewRef(attachment->settings);
}

static PyObject *PyFramebuffer_get_attachment_id(PyFramebuffer *self, PyObject *pyAttachmentPoint)
{
    const GLenum attachmentPoint = _PyFramebufferAttachment_ObjectToAttachmentPoint(pyAttachmentPoint);
    if (attachmentPoint == -1)
        return NULL;

    const Attachment *attachment = FindAttachment(self, attachmentPoint);
    if (attachment == NULL)
        return NULL;

    return PyLong_FromUnsignedLong(attachment->id);
}

static PyObject *PyFramebuffer_clear_color_attachment(PyFramebuffer *self, PyObject *const *args, Py_ssize_t nArgs)
{
    PyObject *result = NULL;

    Py_buffer clearValueBuffer = {0};
    GLint drawBuffer;
    GLenum clearValueType;
    if (!_PyArg_ParseStack(args, nArgs, "y*iI", &clearValueBuffer, &drawBuffer, &clearValueType))
        goto end;

    if (!PyBuffer_IsContiguous(&clearValueBuffer, 'C'))
    {
        PyErr_SetString(PyExc_ValueError, "Clear value buffer must be C-contiguous.");
        goto end;
    }

    if (clearValueBuffer.shape[0] != 4)
    {
        PyErr_Format(PyExc_ValueError, "Clear value buffer must be 4-items long, got only %d items.", clearValueBuffer.shape[0]);
        goto end;
    }

    if (clearValueBuffer.itemsize != GetGLTypeSize(clearValueType))
    {
        PyErr_Format(PyExc_ValueError, "Clear value buffer's item size do not match requested OpenGL type size. Stopping to prevent access violation.");
        goto end;
    }

    switch (clearValueType)
    {
    case GL_FLOAT:
    case GL_FIXED:
    case GL_DOUBLE:
        glClearNamedFramebufferfv(self->id, GL_COLOR, drawBuffer, clearValueBuffer.buf);
        break;
    case GL_BYTE:
    case GL_SHORT:
    case GL_INT:
        glClearNamedFramebufferiv(self->id, GL_COLOR, drawBuffer, clearValueBuffer.buf);
        break;
    case GL_UNSIGNED_BYTE:
    case GL_UNSIGNED_SHORT:
    case GL_UNSIGNED_INT:
        glClearNamedFramebufferuiv(self->id, GL_COLOR, drawBuffer, clearValueBuffer.buf);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Unsupported OpenGL type for buffer clear value: %d.", clearValueType);
        goto end;
    }

    result = Py_NewRef(Py_None);

end:
    if (clearValueBuffer.buf != NULL)
        PyBuffer_Release(&clearValueBuffer);

    return result;
}

static PyObject *PyFramebuffer_clear_depth_attachment(PyFramebuffer *self, PyObject *depthValue)
{
    CHECK_ARG_FLOAT(depthValue, NULL);

    const GLfloat depth = (float)PyFloat_AS_DOUBLE(depthValue);
    glClearNamedFramebufferfv(self->id, GL_DEPTH, 0, &depth);

    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_clear_stencil_attachment(PyFramebuffer *self, PyObject *stencilValue)
{
    CHECK_ARG_INT(stencilValue, NULL);

    const GLint stencil = PyLong_AsLong(stencilValue);
    glClearNamedFramebufferiv(self->id, GL_STENCIL, 0, &stencil);

    Py_RETURN_NONE;
}

static PyObject *PyFramebuffer_clear_depth_stencil_attachment(PyFramebuffer *self, PyObject *const *args, Py_ssize_t nArgs)
{
    GLfloat depth;
    GLint stencil;
    if (!_PyArg_ParseStack(args, nArgs, "fi", &depth, &stencil))
        return NULL;

    glClearNamedFramebufferfi(self->id, GL_DEPTH_STENCIL, 0, depth, stencil);

    Py_RETURN_NONE;
}

PyTypeObject PyFramebuffer_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.Framebuffer",
    .tp_basicsize = sizeof(PyFramebuffer),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyFramebuffer_init,
    .tp_dealloc = (destructor)PyFramebuffer_dealloc,
    .tp_members = (PyMemberDef[]){
        {"id", Py_T_UINT, offsetof(PyFramebuffer, id), Py_READONLY, NULL},
        {"width", Py_T_INT, offsetof(PyFramebuffer, width), Py_READONLY, NULL},
        {"height", Py_T_INT, offsetof(PyFramebuffer, height), Py_READONLY, NULL},
        {"attachments_count", Py_T_PYSSIZET, offsetof(PyFramebuffer, nAttachments), Py_READONLY, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"delete", (PyCFunction)PyFramebuffer_delete, METH_NOARGS, NULL},
        {"bind", (PyCFunction)PyFramebuffer_bind, METH_NOARGS, NULL},
        {"unbind", (PyCFunction)PyFramebuffer_unbind, METH_NOARGS, NULL},
        {"resize", (PyCFunction)PyFramebuffer_resize, METH_FASTCALL, NULL},
        {"get_attachment", (PyCFunction)PyFramebuffer_get_attachment, METH_O, NULL},
        {"get_attachment_id", (PyCFunction)PyFramebuffer_get_attachment_id, METH_O, NULL},
        {"clear_color_attachment", (PyCFunction)PyFramebuffer_clear_color_attachment, METH_FASTCALL, NULL},
        {"clear_depth_attachment", (PyCFunction)PyFramebuffer_clear_depth_attachment, METH_O, NULL},
        {"clear_stencil_attachment", (PyCFunction)PyFramebuffer_clear_stencil_attachment, METH_O, NULL},
        {"clear_depth_stencil_attachment", (PyCFunction)PyFramebuffer_clear_depth_stencil_attachment, METH_FASTCALL, NULL},
        {"set_debug_name", (PyCFunction)PyFramebuffer_set_debug_name, METH_O, NULL},
        // TODO Implement framebuffer attachment reading
        {0},
    },
    .tp_getset = (PyGetSetDef[]){
        {"size", (getter)PyFramebuffer_size_getter, NULL, NULL, NULL},
        {0},
    },
};
