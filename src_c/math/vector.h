#pragma once
#include <cglm/cglm.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    float data[];
} _PyVectorAbstract;

typedef struct
{
    PY_OBJECT_HEAD;
    vec2 data;
} PyVector2;

typedef struct
{
    PY_OBJECT_HEAD;
    vec3 data;
} PyVector3;

typedef struct
{
    PY_OBJECT_HEAD;
    vec4 data;
} PyVector4;

typedef struct
{
    PY_OBJECT_HEAD;
    _PyVectorAbstract *object;
    Py_ssize_t current;
    Py_ssize_t end;
} PyVectorIter;

extern PyTypeObject PyVectorIter_Type;
extern PyTypeObject PyVector2_Type;
extern PyTypeObject PyVector3_Type;
extern PyTypeObject PyVector4_Type;
