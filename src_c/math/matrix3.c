#define MAT_LEN 3
#define TOPLEFT_MATRIX_PY_TYPE &PyMatrix2_Type
#include "matrixTemplate.h"

static int MATRIX_INIT_MULTI_ARGS_FUNC(float *matrixData, PyObject *args)
{
    PyVector3 *r0, *r1, *r2;
    if (!PyArg_ParseTuple(
            args,
            "O!O!O!",
            &PyVector3_Type, &r0,
            &PyVector3_Type, &r1,
            &PyVector3_Type, &r2))
        return -1;

    glm_vec3_copy(r0->data, matrixData + (MAT_LEN) * 0);
    glm_vec3_copy(r1->data, matrixData + (MAT_LEN) * 1);
    glm_vec3_copy(r2->data, matrixData + (MAT_LEN) * 2);

    return 0;
}
