#pragma once
#include <Python.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct
{
    const char *name;
    uint32_t value;
} EnumValue;

bool PyEnum_Add(PyObject *module, const char *enumName, const EnumValue values[], bool isFlag);
bool PyEnum_Check(PyObject *object);
