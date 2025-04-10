#include "viewport.h"
#include "vector.h"
#include "matrix.h"

static PyObject *PyMath_deg_to_rad(PyObject *self, PyObject *value)
{
    PyObject *valueFloat = PyNumber_Float(value);
    if (valueFloat == NULL)
        return NULL;

    return PyFloat_FromDouble(glm_rad((float)PyFloat_AS_DOUBLE(valueFloat)));
}

static PyObject *PyMath_rad_to_deg(PyObject *self, PyObject *value)
{
    PyObject *valueFloat = PyNumber_Float(value);
    if (valueFloat == NULL)
        return NULL;

    return PyFloat_FromDouble(glm_deg((float)PyFloat_AS_DOUBLE(valueFloat)));
}

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.math",
    .m_size = -1,
    .m_methods = (PyMethodDef[]){
        {"deg_to_rad", (PyCFunction)PyMath_deg_to_rad, METH_O, NULL},
        {"rad_to_deg", (PyCFunction)PyMath_rad_to_deg, METH_O, NULL},
        {0},
    },
};

PyMODINIT_FUNC PyInit_math()
{
    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module)
        return NULL;

    ADD_TYPE_OR_FAIL(module, PyViewport2D_Type);
    ADD_TYPE_OR_FAIL(module, PyViewport3D_Type);

    ADD_TYPE_OR_FAIL(module, PyVectorIter_Type);
    ADD_TYPE_OR_FAIL(module, PyVector2_Type);
    ADD_TYPE_OR_FAIL(module, PyVector3_Type);
    ADD_TYPE_OR_FAIL(module, PyVector4_Type);

    // ADD_TYPE_OR_FAIL(module, PyMatrixIter_Type);
    ADD_TYPE_OR_FAIL(module, PyMatrix2_Type);
    ADD_TYPE_OR_FAIL(module, PyMatrix3_Type);
    ADD_TYPE_OR_FAIL(module, PyMatrix4_Type);

    return module;
}
