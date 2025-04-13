#define MAT_LEN 4
#define TOPLEFT_MATRIX_PY_TYPE &PyMatrix3_Type
#include "matrixTemplate.h"

static int MATRIX_INIT_MULTI_ARGS_FUNC(float *matrixData, PyObject *args)
{
    PyVector4 *r0, *r1, *r2, *r3;
    if (!PyArg_ParseTuple(
            args,
            "O!O!O!O!",
            &PyVector4_Type, &r0,
            &PyVector4_Type, &r1,
            &PyVector4_Type, &r2,
            &PyVector4_Type, &r3))
        return -1;

    glm_vec4_copy(r0->data, matrixData + (MAT_LEN * 0));
    glm_vec4_copy(r1->data, matrixData + (MAT_LEN * 1));
    glm_vec4_copy(r2->data, matrixData + (MAT_LEN * 2));
    glm_vec4_copy(r3->data, matrixData + (MAT_LEN * 3));

    return 0;
}
