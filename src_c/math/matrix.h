#pragma once
#include <cglm/cglm.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    CGLM_ALIGN_MAT float data[];
} _PyMatrixAbstract;

typedef struct
{
    PY_OBJECT_HEAD;
    mat2 data;
} PyMatrix2;

typedef struct
{
    PY_OBJECT_HEAD;
    mat3 data;
} PyMatrix3;

typedef struct
{
    PY_OBJECT_HEAD;
    mat4 data;
} PyMatrix4;

typedef struct
{
    PY_OBJECT_HEAD;
    _PyMatrixAbstract *object;
    Py_ssize_t current;
    Py_ssize_t end;
} PyMatrixIter;

extern PyTypeObject PyMatrixIter_Type;
extern PyTypeObject PyMatrix2_Type;
extern PyTypeObject PyMatrix3_Type;
extern PyTypeObject PyMatrix4_Type;
