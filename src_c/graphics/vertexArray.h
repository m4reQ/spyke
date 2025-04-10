#pragma once
#include <glad/gl.h>
#include <stdbool.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint id;
} PyVertexArray;

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint attribIndex;
    GLenum type;
    GLint count;
    GLuint rows;
    bool isNormalized;
} PyVertexDescriptor;

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint bufferId;
    GLsizei stride;
    PyObject *descriptors; // list of PyVertexDescriptor
    GLintptr offset;
    GLuint divisor;
} PyVertexInput;

extern PyTypeObject PyVertexArray_Type;
extern PyTypeObject PyVertexInput_Type;
extern PyTypeObject PyVertexDescriptor_Type;
