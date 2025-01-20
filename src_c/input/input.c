#pragma once
#include "input.h"
#include <stdbool.h>
#include <Python.h>
#include <Windows.h>
#include "../utils.h"
#include "../api.h"
#include "../enum.h"

#define TEXT_BUFFER_SIZE 512

static bool s_TextInputActive;
static size_t s_TextBufferOffset;
static wchar_t s_TextBuffer[TEXT_BUFFER_SIZE];
static uint8_t s_ActiveModifiers;
static uint16_t s_MouseX;
static uint16_t s_MouseY;
static bool s_KeysDown[UINT8_MAX];
static bool s_ButtonsDown[UINT8_MAX];

static bool IsButtonDown(PyObject *button, bool *result)
{
    CHECK_ARG_INT(button, false);

    const uint32_t _button = PyLong_AsUnsignedLong(button);
    if (_button > UINT8_MAX)
    {
        PyErr_SetString(PyExc_ValueError, "Provided button exceeds maximum button value.");
        return false;
    }

    *result = s_ButtonsDown[_button];
    return true;
}

static bool IsKeyDown(PyObject *key, bool *result)
{
    CHECK_ARG_INT(key, false);
    uint32_t _key = PyLong_AsUnsignedLong(key);

    if (_key > UINT8_MAX)
    {
        PyErr_SetString(PyExc_ValueError, "Provided key exceeds max allowed key value.");
        return false;
    }

    *result = s_KeysDown[(uint8_t)_key];
    return true;
}

static void PyInput_API_AppendTextChar(wchar_t character)
{
    if (s_TextInputActive)
    {
        if (character == L'\b')
            s_TextBufferOffset;
        else if (iswprint(character))
            s_TextBuffer[s_TextBufferOffset++] = character;
    }
}

static void PyInput_API_UpdateKeyState(uint8_t key, bool isDown)
{
    s_KeysDown[key] = isDown;
}

static void PyInput_API_UpdateButtonState(uint8_t button, bool isDown)
{
    s_ButtonsDown[button] = isDown;
}

static void PyInput_API_UpdateModifiers(uint8_t modifiers)
{
    s_ActiveModifiers = modifiers;
}

static void PyInput_API_UpdateMousePos(uint16_t x, uint16_t y)
{
    s_MouseX = x;
    s_MouseY = y;
}

static PyObject *PyInput_IsKeyDown(PyObject *UNUSED(self), PyObject *key)
{
    bool result;
    if (IsKeyDown(key, &result))
        return PyBool_FromLong(result);

    return NULL;
}

static PyObject *PyInput_IsKeyUp(PyObject *UNUSED(self), PyObject *key)
{
    bool result;
    if (IsKeyDown(key, &result))
        return PyBool_FromLong(!result);

    return NULL;
}

static PyObject *PyInput_IsButtonUp(PyObject *UNUSED(self), PyObject *button)
{
    bool result;
    if (IsButtonDown(button, &result))
        return PyBool_FromLong(!result);

    return NULL;
}

static PyObject *PyInput_IsButtonDown(PyObject *UNUSED(self), PyObject *button)
{
    bool result;
    if (IsButtonDown(button, &result))
        return PyBool_FromLong(result);

    return NULL;
}

static PyObject *PyInput_GetMouseX(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(s_MouseX);
}

static PyObject *PyInput_GetMouseY(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(s_MouseY);
}

static PyObject *PyInput_GetMousePosition(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyTuple_Pack(2, PyInput_GetMouseX(NULL, NULL), PyInput_GetMouseY(NULL, NULL));
}

static PyObject *PyInput_GetModifiers(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromLong(s_ActiveModifiers);
}

static PyObject *PyInput_IsModifierActive(PyObject *UNUSED(self), PyObject *modifier)
{
    CHECK_ARG_INT(modifier, NULL);

    const uint8_t _modifier = (uint8_t)PyLong_AsUnsignedLong(modifier);
    return PyBool_FromLong((s_ActiveModifiers & _modifier) == _modifier);
}

static PyObject *PyInput_BeginTextInput(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    if (s_TextInputActive)
        Py_RETURN_NONE;

    s_TextBufferOffset = 0;
    s_TextInputActive = true;

    Py_RETURN_NONE;
}

static PyObject *PyInput_GetTextInput(PyObject *UNUSED(self), PyObject *args)
{
    return PyUnicode_FromWideChar(s_TextBuffer, s_TextBufferOffset);
}

static PyObject *PyInput_EndTextInput(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    if (s_TextInputActive)
    {
        s_TextBuffer[s_TextBufferOffset] = '\0';
        s_TextInputActive = false;
    }

    return PyInput_GetTextInput(NULL, NULL);
}

static PyObject *PyInput_ClearTextInput(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    s_TextBufferOffset = 0;
    Py_RETURN_NONE;
}

static PyObject *PyInput_IsTextInputActive(PyObject *UNUSED(self), PyObject *args)
{
    return PyBool_FromLong(s_TextInputActive);
}

static EnumValue s_ButtonEnumValues[] = {
    {"X1", BUTTON_X1},
    {"X2", BUTTON_X2},
    {"LEFT", BUTTON_LEFT},
    {"RIGHT", BUTTON_RIGHT},
    {"MIDDLE", BUTTON_MIDDLE},
    {0},
};

static EnumValue s_KeyEnumValues[] = {
    {"NUM_0", '0'},
    {"NUM_1", '1'},
    {"NUM_2", '2'},
    {"NUM_3", '3'},
    {"NUM_4", '4'},
    {"NUM_5", '5'},
    {"NUM_6", '6'},
    {"NUM_7", '7'},
    {"NUM_8", '8'},
    {"NUM_9", '9'},
    {"A", 'A'},
    {"B", 'B'},
    {"C", 'C'},
    {"D", 'D'},
    {"E", 'E'},
    {"F", 'F'},
    {"G", 'G'},
    {"H", 'H'},
    {"I", 'I'},
    {"J", 'J'},
    {"K", 'K'},
    {"L", 'L'},
    {"M", 'M'},
    {"N", 'N'},
    {"O", 'O'},
    {"P", 'P'},
    {"Q", 'Q'},
    {"R", 'R'},
    {"S", 'S'},
    {"T", 'T'},
    {"U", 'U'},
    {"V", 'V'},
    {"W", 'W'},
    {"X", 'X'},
    {"Y", 'Y'},
    {"Z", 'Z'},
    {"CANCEL", VK_CANCEL},
    {"BACK", VK_BACK},
    {"TAB", VK_TAB},
    {"CLEAR", VK_CLEAR},
    {"RETURN", VK_RETURN},
    {"SHIFT", VK_SHIFT},
    {"CONTROL", VK_CONTROL},
    {"MENU", VK_MENU},
    {"PAUSE", VK_PAUSE},
    {"CAPITAL", VK_CAPITAL},
    {"KANA", VK_KANA},
    {"HANGUL", VK_HANGUL},
    {"IME_ON", VK_IME_ON},
    {"JUNJA", VK_JUNJA},
    {"FINAL", VK_FINAL},
    {"HANJA", VK_HANJA},
    {"KANJI", VK_KANJI},
    {"IME_OFF", VK_IME_OFF},
    {"ESCAPE", VK_ESCAPE},
    {"CONVERT", VK_CONVERT},
    {"NONCONVERT", VK_NONCONVERT},
    {"ACCEPT", VK_ACCEPT},
    {"MODECHANGE", VK_MODECHANGE},
    {"SPACE", VK_SPACE},
    {"PRIOR", VK_PRIOR},
    {"NEXT", VK_NEXT},
    {"END", VK_END},
    {"HOME", VK_HOME},
    {"LEFT", VK_LEFT},
    {"UP", VK_UP},
    {"RIGHT", VK_RIGHT},
    {"DOWN", VK_DOWN},
    {"SELECT", VK_SELECT},
    {"PRINT", VK_PRINT},
    {"EXECUTE", VK_EXECUTE},
    {"SNAPSHOT", VK_SNAPSHOT},
    {"INSERT", VK_INSERT},
    {"DELETE", VK_DELETE},
    {"HELP", VK_HELP},
    {"LWIN", VK_LWIN},
    {"RWIN", VK_RWIN},
    {"APPS", VK_APPS},
    {"SLEEP", VK_SLEEP},
    {"NUMPAD0", VK_NUMPAD0},
    {"NUMPAD1", VK_NUMPAD1},
    {"NUMPAD2", VK_NUMPAD2},
    {"NUMPAD3", VK_NUMPAD3},
    {"NUMPAD4", VK_NUMPAD4},
    {"NUMPAD5", VK_NUMPAD5},
    {"NUMPAD6", VK_NUMPAD6},
    {"NUMPAD7", VK_NUMPAD7},
    {"NUMPAD8", VK_NUMPAD8},
    {"NUMPAD9", VK_NUMPAD9},
    {"MULTIPLY", VK_MULTIPLY},
    {"ADD", VK_ADD},
    {"SEPARATOR", VK_SEPARATOR},
    {"SUBTRACT", VK_SUBTRACT},
    {"DECIMAL", VK_DECIMAL},
    {"DIVIDE", VK_DIVIDE},
    {"F1", VK_F1},
    {"F2", VK_F2},
    {"F3", VK_F3},
    {"F4", VK_F4},
    {"F5", VK_F5},
    {"F6", VK_F6},
    {"F7", VK_F7},
    {"F8", VK_F8},
    {"F9", VK_F9},
    {"F10", VK_F10},
    {"F11", VK_F11},
    {"F12", VK_F12},
    {"F13", VK_F13},
    {"F14", VK_F14},
    {"F15", VK_F15},
    {"F16", VK_F16},
    {"F17", VK_F17},
    {"F18", VK_F18},
    {"F19", VK_F19},
    {"F20", VK_F20},
    {"F21", VK_F21},
    {"F22", VK_F22},
    {"F23", VK_F23},
    {"F24", VK_F24},
    {"NUMLOCK", VK_NUMLOCK},
    {"SCROLL", VK_SCROLL},
    {"LSHIFT", VK_LSHIFT},
    {"RSHIFT", VK_RSHIFT},
    {"LCONTROL", VK_LCONTROL},
    {"RCONTROL", VK_RCONTROL},
    {"LMENU", VK_LMENU},
    {"RMENU", VK_RMENU},
    {"BROWSER_BACK", VK_BROWSER_BACK},
    {"BROWSER_FORWARD", VK_BROWSER_FORWARD},
    {"BROWSER_REFRESH", VK_BROWSER_REFRESH},
    {"BROWSER_STOP", VK_BROWSER_STOP},
    {"BROWSER_SEARCH", VK_BROWSER_SEARCH},
    {"BROWSER_FAVORITES", VK_BROWSER_FAVORITES},
    {"BROWSER_HOME", VK_BROWSER_HOME},
    {"VOLUME_MUTE", VK_VOLUME_MUTE},
    {"VOLUME_DOWN", VK_VOLUME_DOWN},
    {"VOLUME_UP", VK_VOLUME_UP},
    {"MEDIA_NEXT_TRACK", VK_MEDIA_NEXT_TRACK},
    {"MEDIA_PREV_TRACK", VK_MEDIA_PREV_TRACK},
    {"MEDIA_STOP", VK_MEDIA_STOP},
    {"MEDIA_PLAY_PAUSE", VK_MEDIA_PLAY_PAUSE},
    {"LAUNCH_MAIL", VK_LAUNCH_MAIL},
    {"LAUNCH_MEDIA_SELECT", VK_LAUNCH_MEDIA_SELECT},
    {"LAUNCH_APP1", VK_LAUNCH_APP1},
    {"LAUNCH_APP2", VK_LAUNCH_APP2},
    {0},
};

static EnumValue s_ModifierEnumValues[] = {
    {"CONTROL", MK_CONTROL},
    {"SHIFT", MK_SHIFT},
    {0},
};

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.input",
    .m_size = -1,
    .m_methods = (PyMethodDef[]){
        {"is_key_down", PyInput_IsKeyDown, METH_O, NULL},
        {"is_key_up", PyInput_IsKeyUp, METH_O, NULL},
        {"is_button_up", PyInput_IsButtonUp, METH_O, NULL},
        {"is_button_down", PyInput_IsButtonDown, METH_O, NULL},
        {"get_mouse_x", PyInput_GetMouseX, METH_NOARGS, NULL},
        {"get_mouse_y", PyInput_GetMouseY, METH_NOARGS, NULL},
        {"get_mouse_position", PyInput_GetMousePosition, METH_NOARGS, NULL},
        {"get_modifiers", PyInput_GetModifiers, METH_NOARGS, NULL},
        {"is_modifier_active", PyInput_IsModifierActive, METH_O, NULL},
        {"begin_text_input", PyInput_BeginTextInput, METH_NOARGS, NULL},
        {"end_text_input", PyInput_EndTextInput, METH_NOARGS, NULL},
        {"get_text_input", PyInput_GetTextInput, METH_NOARGS, NULL},
        {"clear_text_input", PyInput_ClearTextInput, METH_NOARGS, NULL},
        {"is_text_input_active", PyInput_IsTextInputActive, METH_NOARGS, NULL},
        {0},
    },
};

static PyInput_API s_API = {
    .AppendTextChar = PyInput_API_AppendTextChar,
    .UpdateModifiers = PyInput_API_UpdateModifiers,
    .UpdateMousePos = PyInput_API_UpdateMousePos,
    .UpdateKeyState = PyInput_API_UpdateKeyState,
    .UpdateButtonState = PyInput_API_UpdateButtonState,
};

PyMODINIT_FUNC PyInit_input()
{
    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module)
        return NULL;

    if (!PyAPI_Add(module, &s_API))
        return NULL;

    if (!PyEnum_Add(module, "Key", s_KeyEnumValues, false))
        return NULL;

    if (!PyEnum_Add(module, "Button", s_ButtonEnumValues, false))
        return NULL;

    if (!PyEnum_Add(module, "Modifier", s_ModifierEnumValues, true))
        return NULL;

    return module;
}
