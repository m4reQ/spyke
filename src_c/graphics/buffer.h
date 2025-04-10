#pragma once
#include <stdbool.h>
#include <glad/gl.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint id;
    void *dataPtr;
    GLsizeiptr size;
    GLsizeiptr currentOffset;
    GLenum flags;
} PyBuffer;

extern PyTypeObject PyBuffer_Type;
