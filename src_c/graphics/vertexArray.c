#include "vertexArray.h"
#include "buffer.h"

static GLuint GLTypeToSize(GLenum type)
{
    switch (type)
    {
    case GL_DOUBLE:
        return sizeof(GLdouble);
    case GL_FLOAT:
        return sizeof(GLfloat);
    case GL_HALF_FLOAT:
        return sizeof(GLhalf);
    case GL_INT:
        return sizeof(GLint);
    case GL_UNSIGNED_INT:
        return sizeof(GLuint);
    case GL_SHORT:
        return sizeof(GLshort);
    case GL_UNSIGNED_SHORT:
        return sizeof(GLushort);
    case GL_BYTE:
        return sizeof(GLbyte);
    case GL_UNSIGNED_BYTE:
        return sizeof(GLubyte);
    default:
        return 0;
    }
}

static bool SetAttribFormat(GLuint array, PyVertexDescriptor *desc, GLuint *offset, GLuint rowOffset)
{
    switch (desc->type)
    {
    case GL_DOUBLE:
        glVertexArrayAttribLFormat(
            array,
            desc->attribIndex + rowOffset,
            desc->count,
            desc->type,
            *offset);
        break;
    case GL_FLOAT:
    case GL_HALF_FLOAT:
        glVertexArrayAttribFormat(
            array,
            desc->attribIndex + rowOffset,
            desc->count,
            desc->type,
            (GLboolean)desc->isNormalized,
            *offset);
        break;
    case GL_INT:
    case GL_UNSIGNED_INT:
    case GL_SHORT:
    case GL_UNSIGNED_SHORT:
    case GL_BYTE:
    case GL_UNSIGNED_BYTE:
        // allow to use normalized int attribs
        if (desc->isNormalized)
            glVertexArrayAttribFormat(
                array,
                desc->attribIndex + rowOffset,
                desc->count,
                desc->type,
                (GLboolean)desc->isNormalized,
                *offset);
        else
            glVertexArrayAttribIFormat(
                array,
                desc->attribIndex + rowOffset,
                desc->count,
                desc->type,
                *offset);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Invalid attribute type: %d.", desc->type);
        return false;
    }

    *offset += GLTypeToSize(desc->type) * desc->count;
    return true;
}

static bool AddVertexInput(GLuint array, GLuint index, PyVertexInput *input)
{
    GLuint attribOffset = 0;

    glVertexArrayBindingDivisor(array, index, input->divisor);

    if (input->bufferId != -1)
        glVertexArrayVertexBuffer(array, index, input->bufferId, input->offset, input->stride);

    const Py_ssize_t nDescriptors = PyList_GET_SIZE(input->descriptors);
    for (Py_ssize_t i = 0; i < nDescriptors; i++)
    {
        PyVertexDescriptor *descriptor = (PyVertexDescriptor *)PyList_GET_ITEM(input->descriptors, i);
        if (!PyObject_IsInstance((PyObject *)descriptor, (PyObject *)&PyVertexDescriptor_Type))
        {
            PyErr_SetString(PyExc_TypeError, "All vertex descriptors objects has to be of type spyke.graphics.gl.VertexDescriptor");
            return false;
        }

        for (GLuint row = 0; row < descriptor->rows; row++)
        {
            glEnableVertexArrayAttrib(array, descriptor->attribIndex + row);
            glVertexArrayAttribBinding(array, descriptor->attribIndex + row, index);

            if (!SetAttribFormat(array, descriptor, &attribOffset, row))
                return false;
        }
    }

    return true;
}

static int PyVertexArray_init(PyVertexArray *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"layout", "element_buffer", NULL};

    PyObject *vertexInputs = NULL;
    PyBuffer *elementBuffer = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|O!", kwNames, &PyList_Type, &vertexInputs, &PyBuffer_Type, &elementBuffer))
        return -1;

    glCreateVertexArrays(1, &self->id);

    if (elementBuffer)
        glVertexArrayElementBuffer(self->id, elementBuffer->id);

    const Py_ssize_t nInputs = PyList_GET_SIZE(vertexInputs);
    for (Py_ssize_t i = 0; i < nInputs; i++)
    {
        PyVertexInput *input = (PyVertexInput *)PyList_GET_ITEM(vertexInputs, i);
        // TODO Use PySequence API
        if (!PyList_Check(input->descriptors))
        {
            PyErr_SetString(PyExc_TypeError, "layout must be a list of spyke.graphics.gl.VertexInput objects.");
            return -1;
        }

        if (!AddVertexInput(self->id, (GLuint)i, input))
            return -1;
    }

    return 0;
}

static PyObject *PyVertexArray_delete(PyVertexArray *self, PyObject *args)
{
    (void)args;
    glDeleteVertexArrays(1, &self->id);
    Py_RETURN_NONE;
}

static PyObject *PyVertexArray_bind(PyVertexArray *self, PyObject *args)
{
    (void)args;
    glBindVertexArray(self->id);
    Py_RETURN_NONE;
}

static PyObject *PyVertexArray_set_debug_name(PyVertexArray *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *nameStr = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectLabel(GL_VERTEX_ARRAY, self->id, nameLength, nameStr);

    Py_RETURN_NONE;
}

static PyObject *PyVertexArray_bind_vertex_buffer(PyVertexArray *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"buffer", "index", "stride", "offset", "divisor", NULL};

    PyBuffer *buffer;
    GLuint index;
    GLsizei stride;
    GLintptr offset = 0;
    GLuint divisor = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!Ii|nI", kwNames, &PyBuffer_Type, &buffer, &index, &stride, &offset, &divisor))
        return NULL;

    glVertexArrayVertexBuffer(self->id, index, buffer->id, offset, stride);
    glVertexArrayBindingDivisor(self->id, index, divisor);

    Py_RETURN_NONE;
}

static PyObject *PyVertexArray_bind_index_buffer(PyVertexArray *self, PyBuffer *buffer)
{
    if (!PyObject_IsInstance((PyObject *)buffer, (PyObject *)&PyBuffer_Type))
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be of type spyke.graphics.gl.Buffer, got: %s.", Py_TYPE(buffer)->tp_name);
        return NULL;
    }

    glVertexArrayElementBuffer(self->id, buffer->id);

    Py_RETURN_NONE;
}

PyTypeObject PyVertexArray_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_new = PyType_GenericNew,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_name = "spyke.graphics.gl.VertexArray",
    .tp_basicsize = sizeof(PyVertexArray),
    .tp_init = (initproc)PyVertexArray_init,
    .tp_members = (PyMemberDef[]){
        {"id", Py_T_UINT, offsetof(PyVertexArray, id), Py_READONLY, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"delete", (PyCFunction)PyVertexArray_delete, METH_NOARGS, NULL},
        {"bind", (PyCFunction)PyVertexArray_bind, METH_NOARGS, NULL},
        {"bind_vertex_buffer", (PyCFunction)PyVertexArray_bind_vertex_buffer, METH_VARARGS | METH_KEYWORDS, NULL},
        {"bind_index_buffer", (PyCFunction)PyVertexArray_bind_index_buffer, METH_O, NULL},
        {"set_debug_name", (PyCFunction)PyVertexArray_set_debug_name, METH_O, NULL},
        {0},
    },
};
