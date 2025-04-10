#pragma once
#include <glad/gl.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    GLsync sync;
} PySync;

extern PyTypeObject PySync_Type;
