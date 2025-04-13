#define MAT_LEN 2
#include "matrixTemplate.h"

static int MATRIX_INIT_MULTI_ARGS_FUNC(float *matrixData, PyObject *args)
{
    PyVector2 *r0, *r1;
    if (!PyArg_ParseTuple(
            args,
            "O!O!",
            &PyVector2_Type, &r0,
            &PyVector2_Type, &r1))
        return -1;

    glm_vec2_copy(r0->data, matrixData + (MAT_LEN) * 0);
    glm_vec2_copy(r1->data, matrixData + (MAT_LEN) * 1);

    return 0;
}
