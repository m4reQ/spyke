#include "enum.h"

static PyObject *enumClass = NULL;
static PyObject *flagClass = NULL;

bool PyEnum_Check(PyObject *object)
{
    return PyObject_IsInstance(object, enumClass);
}

bool PyEnum_Add(PyObject *module, const char *enumName, const EnumValue values[], bool isFlag)
{
    if (!enumClass || !flagClass)
    {
        PyObject *enumModule = PyImport_ImportModule("enum");
        if (!enumModule)
            return false;

        enumClass = PyObject_GetAttrString(enumModule, "IntEnum");
        flagClass = PyObject_GetAttrString(enumModule, "IntFlag");
    }

    PyObject *valuesDict = PyDict_New();
    EnumValue *enumValue = values;

    while (true)
    {
        if (enumValue->name == 0 && enumValue->value == 0)
            break;

        PyDict_SetItemString(valuesDict, enumValue->name, PyLong_FromUnsignedLong(enumValue->value));

        enumValue++;
    }

    PyObject *result = PyObject_CallFunction(isFlag ? flagClass : enumClass, "sN", enumName, valuesDict);
    if (!result)
        return false;

    if (PyModule_AddObject(module, enumName, result))
        return false;

    return true;
}
