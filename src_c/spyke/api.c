#include "api.h"

bool PyAPI_Add(PyObject *module, void *api)
{
    PyObject *apiCapsule = PyCapsule_New(api, "_C_API", NULL);
    if (!apiCapsule)
        return false;

    if (PyModule_AddObject(module, "_C_API", apiCapsule))
        return false;

    return true;
}

void *PyAPI_Import(const char *moduleName)
{
    PyObject *module = PyImport_ImportModule(moduleName);
    if (!module)
        return NULL;

    PyObject *capsule = PyObject_GetAttrString(module, "_C_API");
    if (!capsule)
        return NULL;

    if (!PyCapsule_CheckExact(capsule))
    {
        PyErr_SetString(PyExc_TypeError, "API object is not a capsule.");
        return NULL;
    }

    return PyCapsule_GetPointer(capsule, "_C_API");
}
