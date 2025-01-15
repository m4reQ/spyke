#pragma once
#include <Python.h>
#include <stdbool.h>

bool PyAPI_Add(PyObject *module, void *api);
void *PyAPI_Import(const char *moduleName);
