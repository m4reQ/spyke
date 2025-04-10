#include "buffer.h"

static Py_ssize_t AlignTo(Py_ssize_t x, Py_ssize_t alignment)
{
    return (x + alignment - 1) & (-alignment);
}

static bool CanStoreData(Py_ssize_t dataSize, Py_ssize_t currentOffset, Py_ssize_t size)
{
    return currentOffset + dataSize <= size;
}

static int PyBuffer_init(PyBuffer *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"size", "flags", "data", NULL};

    Py_buffer data = {0};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II|y*", kwNames, &self->size, &self->flags, &data))
        return -1;

    void *dataPtr = NULL;
    bool freeDataPtr = false;
    if (data.obj != NULL)
    {
        if (data.len > self->size)
        {
            PyErr_SetString(PyExc_ValueError, "Provided data size is bigger than requested buffer size.");
            return -1;
        }

        dataPtr = PyMem_Malloc(data.len);
        if (PyBuffer_ToContiguous(dataPtr, &data, data.len, 'C') == -1)
        {
            PyBuffer_Release(&data);
            PyMem_Free(dataPtr);
            return -1;
        }

        freeDataPtr = true;

        PyBuffer_Release(&data);
    }

    glCreateBuffers(1, &self->id);
    glNamedBufferStorage(self->id, self->size, dataPtr, self->flags);

    if ((self->flags & GL_MAP_COHERENT_BIT) != GL_MAP_COHERENT_BIT)
        self->flags |= GL_MAP_FLUSH_EXPLICIT_BIT;

    if ((self->flags & GL_DYNAMIC_STORAGE_BIT) == GL_DYNAMIC_STORAGE_BIT)
    {
        self->dataPtr = PyMem_Malloc(self->size);
    }
    else if ((self->flags & GL_MAP_PERSISTENT_BIT) == GL_MAP_PERSISTENT_BIT)
    {
        self->dataPtr = glMapNamedBufferRange(self->id, 0, self->size, self->flags);
    }
    else
    {
        self->dataPtr = NULL;
    }

    if (freeDataPtr)
        PyMem_Free(dataPtr);

    return 0;
}

static void PyBuffer_dealloc(PyBuffer *self)
{
    if ((self->flags & GL_DYNAMIC_STORAGE_BIT) == GL_DYNAMIC_STORAGE_BIT)
        PyMem_Free(self->dataPtr);

    Py_TYPE(self)->tp_free(self);
}

static PyObject *PyBuffer_repr(PyBuffer *self)
{
    return PyUnicode_FromFormat(
        "<object %s (size: %d, current offset: %d, memory: %s) at 0x%zX>",
        Py_TYPE(self)->tp_name,
        self->size,
        self->currentOffset,
        ((self->flags & GL_DYNAMIC_STORAGE_BIT) == GL_DYNAMIC_STORAGE_BIT) ? "CLIENT" : "OPENGL",
        (uintptr_t)self);
}

static PyObject *PyBuffer_delete(PyBuffer *self, PyObject *args)
{
    (void)args;
    glDeleteBuffers(1, &self->id);
    Py_RETURN_NONE;
}

static PyObject *PyBuffer_bind(PyBuffer *self, PyObject *target)
{
    CHECK_ARG_INT(target, NULL);
    glBindBuffer(PyLong_AsUnsignedLong(target), self->id);
    Py_RETURN_NONE;
}

static PyObject *PyBuffer_bind_base(PyBuffer *self, PyObject *const *args, Py_ssize_t nArgs)
{
    GLenum target;
    GLuint index;
    if (!_PyArg_ParseStack(args, nArgs, "II", &target, &index))
        return NULL;

    glBindBufferBase(target, index, self->id);
    Py_RETURN_NONE;
}

static PyObject *PyBuffer_write(PyBuffer *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"data", "offset", "alignment", NULL};

    PyObject *data;
    void *dataPtr;
    Py_ssize_t dataSize;
    Py_ssize_t offset = self->currentOffset;
    Py_ssize_t alignment = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|nn", kwNames, &data, &offset))
        return NULL;

    // data pointer can only be NULL if buffer was not mapped
    if (self->dataPtr == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Buffers that use mapping have to be mapped before storing data.");
        return NULL;
    }

    offset = AlignTo(offset, alignment);

    if (PyObject_CheckBuffer(data))
    {
        Py_buffer dataBuffer = {0};
        if (PyObject_GetBuffer(data, &dataBuffer, 0) == -1)
            return NULL;

        if (!CanStoreData(dataBuffer.len, offset, self->size))
        {
            PyBuffer_Release(&dataBuffer);
            PyErr_SetString(PyExc_RuntimeError, "Data transfer would cause buffer overflow.");
            return NULL;
        }

        if (PyBuffer_ToContiguous((char *)self->dataPtr + offset, &dataBuffer, dataBuffer.len, 'C') == -1)
        {
            PyBuffer_Release(&dataBuffer);
            return NULL;
        }

        self->currentOffset = offset + dataBuffer.len;

        PyBuffer_Release(&dataBuffer);
        Py_RETURN_NONE;
    }
    else if (PyLong_Check(data))
    {
        uint32_t _data = PyLong_AsUnsignedLong(data);
        dataPtr = &_data;
        dataSize = sizeof(uint32_t);
    }
    else if (PyFloat_Check(data))
    {
        float _data = (float)PyFloat_AsDouble(data);
        dataPtr = &_data;
        dataSize = sizeof(float);
    }
    else
    {
        PyErr_Format(PyExc_TypeError, "Expected data argument to be either int, float or object that supports buffer protocol, got: %s.", Py_TYPE(data)->tp_name);
        return NULL;
    }

    if (!CanStoreData(dataSize, offset, self->size))
    {
        PyErr_SetString(PyExc_RuntimeError, "Data transfer would cause buffer overflow.");
        return NULL;
    }

    memcpy((char *)self->dataPtr + offset, dataPtr, dataSize);
    self->currentOffset = offset + dataSize;

    Py_RETURN_NONE;
}

static PyObject *PyBuffer_write_address(PyBuffer *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"data", "size", "offset", "alignment", NULL};

    if (self->dataPtr == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Buffers that use mapping have to be mapped before storing data.");
        return NULL;
    }

    void *address;
    Py_ssize_t size;
    Py_ssize_t offset = self->currentOffset;
    Py_ssize_t alignment = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "nn|nn", kwNames, &address, &size, &offset))
        return NULL;

    offset = AlignTo(offset, alignment);

    if (!CanStoreData(size, offset, self->size))
    {
        PyErr_SetString(PyExc_RuntimeError, "Data transfer would cause buffer overflow.");
        return NULL;
    }

    memcpy((char *)self->dataPtr + offset, address, size);
    self->currentOffset = offset + size;

    Py_RETURN_NONE;
}

static PyObject *PyBuffer_transfer(PyBuffer *self, PyObject *args)
{
    (void)args;

    // don't do anything if buffer no data was stored
    if (self->currentOffset == 0)
        Py_RETURN_NONE;

    if ((self->flags & GL_DYNAMIC_STORAGE_BIT) == GL_DYNAMIC_STORAGE_BIT)
    {
        glNamedBufferSubData(self->id, 0, self->currentOffset, self->dataPtr);
    }
    else
    {
        if ((self->flags & GL_MAP_COHERENT_BIT) != GL_MAP_COHERENT_BIT)
        {
            glFlushMappedNamedBufferRange(self->id, 0, self->currentOffset);
        }

        if ((self->flags & GL_MAP_PERSISTENT_BIT) != GL_MAP_PERSISTENT_BIT)
        {
            glUnmapNamedBuffer(self->id);
            self->dataPtr = NULL;
        }
    }

    PyObject *result = PyLong_FromSize_t(self->currentOffset);
    self->currentOffset = 0;

    return result;
}

static PyObject *PyBuffer_reset_data_offset(PyBuffer *self, PyObject *args)
{
    (void)args;
    self->currentOffset = 0;
    Py_RETURN_NONE;
}

static PyObject *PyBuffer_map(PyBuffer *self, PyObject *args)
{
    (void)args;

    // data ptr can only be null when using non-persistent mapped buffer when it's unmapped
    if (self->dataPtr == NULL)
    {
        self->dataPtr = glMapNamedBufferRange(self->id, 0, self->size, self->flags);
        if (self->dataPtr == NULL)
        {
            PyErr_Format(PyExc_RuntimeError, "Failed to map the buffer. Error code: %d.", glGetError());
            return NULL;
        }
    }

    Py_RETURN_NONE;
}

static PyObject *PyBuffer_read(PyBuffer *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"out", "size", "offset", NULL};

    Py_buffer out = {0};
    Py_ssize_t size = 0;
    Py_ssize_t offset = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "w*|nn", kwNames, &out, &size, &offset))
        return NULL;

    if (size == 0)
        size = out.len * out.itemsize;

    if (size > out.len * out.itemsize)
    {
        PyErr_SetString(PyExc_RuntimeError, "Provided buffer is smaller than requested read size.");
        return NULL;
    }

    if (size + offset > self->size)
    {
        PyErr_SetString(PyExc_RuntimeError, "Trying to perform requested read would result in buffer underflow.");
        return NULL;
    }

    if (PyBuffer_IsContiguous(&out, 'C'))
    {
        PyErr_SetString(PyExc_ValueError, "Provided output buffer must be C-contiguous.");
        return NULL;
    }

    if ((self->flags & GL_DYNAMIC_STORAGE_BIT) == GL_DYNAMIC_STORAGE_BIT)
    {
        glGetNamedBufferSubData(self->id, offset, size, out.buf);
    }
    else
    {
        if ((self->flags & GL_MAP_READ_BIT) != GL_MAP_READ_BIT)
        {
            PyErr_SetString(PyExc_RuntimeError, "Bufer is not readable.");
            return NULL;
        }

        if (self->dataPtr == NULL)
        {
            PyErr_SetString(PyExc_RuntimeError, "Buffers that use non-persistent mapping must be mapped before reading.");
            return NULL;
        }

        if (PyBuffer_FromContiguous(&out, (char *)self->dataPtr + offset, size, 'C') == -1)
            return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyBuffer_unbind(PyObject *self, PyObject *target)
{
    (void)self;

    GLenum _target = PyLong_AsUnsignedLong(target);
    if (PyErr_Occurred())
        return NULL;

    glBindBuffer(_target, 0);

    Py_RETURN_NONE;
}

static PyObject *PyBuffer_can_store_data(PyBuffer *self, PyObject *dataSize)
{
    Py_ssize_t _dataSize = PyLong_AsSsize_t(dataSize);
    if (PyErr_Occurred())
        return NULL;

    return PyBool_FromLong(CanStoreData(_dataSize, self->currentOffset, self->size));
}

static PyObject *PyBuffer_set_debug_name(PyBuffer *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *name = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectLabel(GL_BUFFER, self->id, nameLength, name);

    Py_RETURN_NONE;
}

PyTypeObject PyBuffer_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.Buffer",
    .tp_basicsize = sizeof(PyBuffer),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyBuffer_init,
    .tp_dealloc = (destructor)PyBuffer_dealloc,
    .tp_repr = (reprfunc)PyBuffer_repr,
    .tp_methods = (PyMethodDef[]){
        {"unbind", (PyCFunction)PyBuffer_unbind, METH_STATIC | METH_O, NULL},
        {"delete", (PyCFunction)PyBuffer_delete, METH_NOARGS, NULL},
        {"bind", (PyCFunction)PyBuffer_bind, METH_O, NULL},
        {"bind_base", (PyCFunction)PyBuffer_bind_base, METH_FASTCALL, NULL},
        {"write", (PyCFunction)PyBuffer_write, METH_VARARGS | METH_KEYWORDS, NULL},
        {"write_address", (PyCFunction)PyBuffer_write_address, METH_VARARGS | METH_KEYWORDS, NULL},
        {"transfer", (PyCFunction)PyBuffer_transfer, METH_NOARGS, NULL},
        {"reset_data_offset", (PyCFunction)PyBuffer_reset_data_offset, METH_NOARGS, NULL},
        {"map", (PyCFunction)PyBuffer_map, METH_NOARGS, NULL},
        {"read", (PyCFunction)PyBuffer_read, METH_VARARGS | METH_KEYWORDS, NULL},
        {"can_store_data", (PyCFunction)PyBuffer_can_store_data, METH_O, NULL},
        {"set_debug_name", (PyCFunction)PyBuffer_set_debug_name, METH_O, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"id", Py_T_UINT, offsetof(PyBuffer, id), Py_READONLY, NULL},
        {"size", Py_T_PYSSIZET, offsetof(PyBuffer, size), Py_READONLY, NULL},
        {"current_offset", Py_T_PYSSIZET, offsetof(PyBuffer, currentOffset), 0, NULL},
        {0},
    },
};
