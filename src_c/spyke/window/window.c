#include <Python.h>
#include <Windows.h>
#include <glad/wgl.h>
#include "windowSettings.h"
#include "windowEvents.h"
#include "../api.h"
#include "../enum.h"
#include "../events/events.h"

#define WIN32_CLASS_NAME L"SpykeWindowClass"
#define WIN32_WGL_CLASS_NAME "WGLDummyClass"
#define FLAG_IS_SET(flags, x) ((flags & x) == x)
#define FLAG_CLEAR(flags, x) flags &= ~(x)
#define FLAG_SET(flags, x) flags |= x
#define CREATE_EVENT_DATA(type) type *eventData = (type *)CreateEventData(&type##_Type)
#define INVOKE_EVENT(event) s_WindowProcFailed = !InvokeEvent(event, (PyObject *)eventData)

static bool s_IsInitialized;
static bool s_IsVisible;
static bool s_ShouldClose;
static bool s_CursorVisible;
static bool s_WindowProcFailed;
static bool s_IsInitializing;
static HCURSOR s_Cursor;
static HWND s_Handle;
static HDC s_DeviceContext;
static HGLRC s_GLContext;
static RECT s_WindowRect;

// events API
static EventsAPI *s_Events;

// window events
static PyEvent *s_ResizeEvent;
static PyEvent *s_WindowMoveEvent;
static PyEvent *s_CloseEvent;
static PyEvent *s_MouseMoveEvent;
static PyEvent *s_ShowEvent;
static PyEvent *s_ScrollEvent;
static PyEvent *s_KeyDownEvent;
static PyEvent *s_KeyUpEvent;
static PyEvent *s_ButtonDownEvent;
static PyEvent *s_ButtonUpEvent;
static PyEvent *s_CharEvent;

static PyEvent *NewEvent()
{
    return (PyEvent *)PyObject_CallNoArgs((PyObject *)s_Events->pyEventType);
}

static PyObject *CreateEventData(PyTypeObject *type)
{
    PyObject *result = PyObject_New(PyObject, type);
    return PyObject_Init(result, type);
}

static bool InvokeEvent(PyEvent *event, PyObject *eventData)
{
    bool success = true;

    // suppress events during window initialization
    // prevent further event invocations when an event raised exception (WindowProc is recursive bruh)
    if (!s_IsInitializing)
        success = s_Events->pyEventInvoke(event, eventData) != NULL;

    // if (s_WindowProcFailed)
    //     success = false;

    Py_DecRef(eventData);
    return success;
}

static void InvokeButtonDown(uint8_t button, WPARAM wParam, LPARAM lParam)
{
    CREATE_EVENT_DATA(PyButtonDownEventData);
    eventData->button = button;
    eventData->modifiers = wParam;
    eventData->x = LOWORD(lParam);
    eventData->y = HIWORD(lParam);

    INVOKE_EVENT(s_ButtonDownEvent);
}

static void InvokeButtonUp(uint8_t button, WPARAM wParam, LPARAM lParam)
{
    CREATE_EVENT_DATA(PyButtonUpEventData);
    eventData->button = button;
    eventData->modifiers = wParam;
    eventData->x = LOWORD(lParam);
    eventData->y = HIWORD(lParam);

    INVOKE_EVENT(s_ButtonUpEvent);
}

static uint32_t GetWidth()
{
    return s_WindowRect.right - s_WindowRect.left;
}

static uint32_t GetHeight()
{
    return s_WindowRect.bottom - s_WindowRect.top;
}

static LRESULT CALLBACK WindowProc(HWND window, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_MOUSEMOVE:
    {
        CREATE_EVENT_DATA(PyMouseMoveEventData);
        eventData->modifiers = (uint16_t)wParam;
        eventData->x = LOWORD(lParam);
        eventData->y = HIWORD(lParam);

        INVOKE_EVENT(s_MouseMoveEvent);

        break;
    }
    case WM_CLOSE:
    {
        s_ShouldClose = true;

        CREATE_EVENT_DATA(PyCloseEventData);
        eventData->time = 0.0; // TODO Add close time to close event

        INVOKE_EVENT(s_CloseEvent);

        break;
    }
    case WM_MOVE:
    {
        const uint32_t width = GetWidth();
        const uint32_t height = GetHeight();

        const uint32_t x = LOWORD(lParam);
        const uint32_t y = HIWORD(lParam);

        s_WindowRect.left = x;
        s_WindowRect.right = s_WindowRect.left + width;

        s_WindowRect.top = y;
        s_WindowRect.bottom = s_WindowRect.top + height;

        CREATE_EVENT_DATA(PyMoveEventData);
        eventData->x = x;
        eventData->y = y;

        INVOKE_EVENT(s_WindowMoveEvent);

        break;
    }
    case WM_SHOWWINDOW:
    {
        s_IsVisible = (bool)wParam;

        CREATE_EVENT_DATA(PyShowEventData);
        eventData->isVisible = s_IsVisible;

        INVOKE_EVENT(s_ShowEvent);

        break;
    }
    case WM_MOUSEWHEEL:
    {
        CREATE_EVENT_DATA(PyScrollEventData);
        eventData->delta = HIWORD(wParam);
        eventData->modifiers = LOWORD(wParam);
        eventData->x = LOWORD(lParam);
        eventData->y = HIWORD(wParam);

        INVOKE_EVENT(s_ScrollEvent);

        break;
    }
    case WM_SIZE:
    {
        const uint32_t width = LOWORD(lParam);
        const uint32_t height = HIWORD(lParam);

        s_WindowRect.right = s_WindowRect.left + width;
        s_WindowRect.bottom = s_WindowRect.top + height;

        CREATE_EVENT_DATA(PyResizeEventData);
        eventData->width = (uint16_t)width;
        eventData->height = (uint16_t)height;

        INVOKE_EVENT(s_ResizeEvent);

        break;
    }
    case WM_KEYDOWN:
    {
        CREATE_EVENT_DATA(PyKeyDownEventData);
        eventData->key = wParam;
        eventData->repeatCount = LOWORD(lParam);
        eventData->scanCode = (lParam & 0x00FF0000) >> 16;
        eventData->wasPressed = (bool)(lParam & (1 << 30));

        INVOKE_EVENT(s_KeyDownEvent);

        break;
    }
    case WM_KEYUP:
    {
        CREATE_EVENT_DATA(PyKeyUpEventData);
        eventData->key = wParam;
        eventData->scanCode = (lParam & 0x00FF0000) >> 16;

        INVOKE_EVENT(s_KeyUpEvent);

        break;
    }
    case WM_LBUTTONDOWN:
    {
        InvokeButtonDown(3, wParam, lParam);
        break;
    }
    case WM_RBUTTONDOWN:
    {
        InvokeButtonDown(4, wParam, lParam);
        break;
    }
    case WM_MBUTTONDOWN:
    {
        InvokeButtonDown(5, wParam, lParam);
        break;
    }
    case WM_XBUTTONDOWN:
    {
        InvokeButtonDown(HIWORD(wParam), LOWORD(wParam), lParam);
        break;
    }

    case WM_LBUTTONUP:
    {
        InvokeButtonUp(3, wParam, lParam);
        break;
    }
    case WM_RBUTTONUP:
    {
        InvokeButtonUp(4, wParam, lParam);
        break;
    }
    case WM_MBUTTONUP:
    {
        InvokeButtonUp(5, wParam, lParam);
        break;
    }
    case WM_XBUTTONUP:
    {
        InvokeButtonUp(HIWORD(wParam), LOWORD(wParam), lParam);
        break;
    }
    case WM_CHAR:
    {
        CREATE_EVENT_DATA(PyCharEventData);
        eventData->character = wParam;
        eventData->repeatCount = LOWORD(lParam);
        eventData->scanCode = (lParam & 0x00FF0000) >> 16;
        eventData->wasPressed = (bool)(lParam & (1 << 30));

        INVOKE_EVENT(s_CharEvent);

        break;
    }
    case WM_SETCURSOR:
    {
        if (!s_CursorVisible)
        {
            if (LOWORD(lParam) == HTCAPTION)
                SetCursor(s_Cursor);
            else if (LOWORD(lParam) == HTCLIENT)
                SetCursor(NULL);

            return TRUE;
        }

        // Implicit fallthrough
    }
    default:
        // dont invoke default handler because that would lead to recursive call to us
        // possibly invoking python code through another event which would result in crash
        if (!s_WindowProcFailed)
            return DefWindowProcW(window, msg, wParam, lParam);
    }

    return FALSE;
}

static const char *GetWin32ErrorString(void)
{
    static char s_MessageBuffer[64 * 1024];

    const DWORD messageLength = FormatMessageA(
        FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        GetLastError(),
        LANG_NEUTRAL,
        s_MessageBuffer,
        sizeof(s_MessageBuffer),
        NULL);
    if (messageLength == 0)
        return "[failed to format win32 error message]";

    s_MessageBuffer[messageLength] = '\0';
    return s_MessageBuffer;
}

static HCURSOR LoadWindowCursor(void)
{
    return LoadCursorA(NULL, IDC_ARROW);
}

static bool RegisterWindowClass(bool cursorVisible)
{
    const WNDCLASSEXW wndClass = {
        .cbSize = sizeof(WNDCLASSEXW),
        .hInstance = GetModuleHandleA(NULL),
        .lpszClassName = WIN32_CLASS_NAME,
        .style = CS_OWNDC,
        .lpfnWndProc = WindowProc,
        .hCursor = cursorVisible ? NULL : s_Cursor,
    };
    return (bool)RegisterClassExW(&wndClass);
}

static DWORD GetStyleFlags(WindowFlags flags)
{
    DWORD result = 0;
    if (FLAG_IS_SET(flags, WND_FLAGS_FULLSCREEN) || FLAG_IS_SET(flags, WND_FLAGS_BORDERLESS))
        result = WS_POPUP;
    else
        result = WS_OVERLAPPEDWINDOW;

    if (!FLAG_IS_SET(flags, WND_FLAGS_RESIZABLE))
        FLAG_CLEAR(result, WS_SIZEBOX);

    FLAG_SET(result, WS_VISIBLE);

    return result;
}

static DWORD GetStyleExFlags(WindowFlags flags)
{
    DWORD result = 0;
    if (FLAG_IS_SET(flags, WND_FLAGS_ALLOW_FILE_DROP))
        FLAG_SET(result, WS_EX_ACCEPTFILES);

    if (FLAG_IS_SET(flags, WND_FLAGS_TRANSPARENT_FRAMEBUFFER))
        FLAG_SET(result, WS_EX_TRANSPARENT);

    return result;
}

static void GetFullscreenSize(uint32_t *width, uint32_t *height)
{
    *width = (uint32_t)GetSystemMetrics(SM_CXSCREEN);
    *height = (uint32_t)GetSystemMetrics(SM_CYSCREEN);
}

static HWND CreateWindowHandle(const PyWindowSettings *settings)
{
    const DWORD style = GetStyleFlags(settings->flags);
    const DWORD styleEx = GetStyleExFlags(settings->flags);

    uint32_t width = settings->width;
    uint32_t height = settings->height;
    if (FLAG_IS_SET(settings->flags, WND_FLAGS_FULLSCREEN))
        GetFullscreenSize(&width, &height);

    return CreateWindowExW(
        styleEx,
        WIN32_CLASS_NAME,
        PyUnicode_AsWideCharString(settings->pyTitle, NULL),
        style,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        width,
        height,
        NULL,
        NULL,
        GetModuleHandleA(NULL),
        NULL);
}

static bool LoadWGL(void)
{
    const WNDCLASSA dummyWndClass = {
        .lpszClassName = WIN32_WGL_CLASS_NAME,
        .style = CS_OWNDC,
        .lpfnWndProc = DefWindowProcA,
    };
    if (!RegisterClassA(&dummyWndClass))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to register dummy WGL window class: %s.", GetWin32ErrorString());
        return false;
    }

    HWND dummyWindow = CreateWindowA(
        WIN32_WGL_CLASS_NAME,
        "",
        WS_OVERLAPPED,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        NULL,
        NULL,
        NULL,
        NULL);
    if (!dummyWindow)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to create dummy WGL window: %s.", GetWin32ErrorString());
        return false;
    }

    HDC dummyDeviceContext = GetDC(dummyWindow);
    if (!dummyDeviceContext)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to retrieve dummy WGL device context: %s.", GetWin32ErrorString());
        return false;
    }

    PIXELFORMATDESCRIPTOR pfd = {
        .nSize = sizeof(PIXELFORMATDESCRIPTOR),
        .nVersion = 1,
        .dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        .iPixelType = PFD_TYPE_RGBA,
        .cColorBits = 24,
    };

    const int format = ChoosePixelFormat(dummyDeviceContext, &pfd);
    if (!format)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find suitable pixel format for dummy WGL device context: %s.", GetWin32ErrorString());
        return false;
    }

    if (!DescribePixelFormat(dummyDeviceContext, format, sizeof(PIXELFORMATDESCRIPTOR), &pfd))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to describe dummy WGL pixel format: %s.", GetWin32ErrorString());
        return false;
    }

    if (!SetPixelFormat(dummyDeviceContext, format, &pfd))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to set pixel format for dummy WGL device context: %s", GetWin32ErrorString());
        return false;
    }

    HGLRC dummyGLContext = wglCreateContext(dummyDeviceContext);
    if (!dummyGLContext)
    {
        PyErr_Format(PyExc_RuntimeWarning, "Failed to create dummy WGL GL context: %s.", GetWin32ErrorString());
        return false;
    }

    if (!wglMakeCurrent(dummyDeviceContext, dummyGLContext))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to set dummy WGL GL context current: %s.", GetWin32ErrorString());
        return false;
    }

    if (!gladLoaderLoadWGL(dummyDeviceContext))
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to load WGL.");
        return false;
    }

    wglMakeCurrent(NULL, NULL);
    wglDeleteContext(dummyGLContext);
    ReleaseDC(dummyWindow, dummyDeviceContext);
    DestroyWindow(dummyWindow);
    UnregisterClassA(WIN32_WGL_CLASS_NAME, NULL);

    return true;
}

static HGLRC CreateOpenGLContext(bool transparentFramebuffer)
{
    const int pixelFormatAttribs[] =
        {
            WGL_DRAW_TO_WINDOW_ARB,
            TRUE,
            WGL_SUPPORT_OPENGL_ARB,
            TRUE,
            WGL_DOUBLE_BUFFER_ARB,
            TRUE,
            WGL_PIXEL_TYPE_ARB,
            WGL_TYPE_RGBA_ARB,
            WGL_COLOR_BITS_ARB,
            24,
            WGL_ALPHA_BITS_ARB,
            (transparentFramebuffer ? 8 : 0),
            WGL_DEPTH_BITS_ARB,
            24,
            WGL_STENCIL_BITS_ARB,
            8,
            0,
        };

    int format;
    UINT formatsCount;
    if (!wglChoosePixelFormatARB(s_DeviceContext, pixelFormatAttribs, NULL, 1, &format, &formatsCount))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to retireve WGL pixel formats: %s.", GetWin32ErrorString());
        return NULL;
    }

    if (formatsCount == 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to find suitable pixel format.");
        return NULL;
    }

    PIXELFORMATDESCRIPTOR pfd = {.nSize = sizeof(PIXELFORMATDESCRIPTOR)};
    if (!DescribePixelFormat(s_DeviceContext, format, sizeof(PIXELFORMATDESCRIPTOR), &pfd))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to describe pixel format: %s.", GetWin32ErrorString());
        return NULL;
    }

    if (!SetPixelFormat(s_DeviceContext, format, &pfd))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to set window pixel format: %s.", GetWin32ErrorString());
        return NULL;
    }

    // ugly hack because python api doesnt expose this anywhere except Py_DebugFlag which is deprecated
    const bool optimizationEnabled = _PyInterpreterState_GetConfig(PyInterpreterState_Get())->parser_debug;

    const int glAttribs[] = {
        WGL_CONTEXT_MAJOR_VERSION_ARB,
        4,
        WGL_CONTEXT_MINOR_VERSION_ARB,
        5,
        WGL_CONTEXT_PROFILE_MASK_ARB,
        WGL_CONTEXT_CORE_PROFILE_BIT_ARB,
        WGL_CONTEXT_FLAGS_ARB,
        WGL_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB | (optimizationEnabled ? WGL_CONTEXT_DEBUG_BIT_ARB : 0),
        0,
    };

    HGLRC glContext = wglCreateContextAttribsARB(s_DeviceContext, NULL, glAttribs);
    if (!glContext)
        PyErr_SetString(PyExc_RuntimeError, "Failed to create OpenGL context.");

    return glContext;
}

static PyObject *PyWindow_Initialize(PyObject *UNUSED(self), PyWindowSettings *settings)
{
    CHECK_ARG_TYPE(settings, &PyWindowSettings_Type, NULL);

    s_IsInitializing = true;

    if (!LoadWGL())
        return NULL; // error already set by the function

    s_CursorVisible = !FLAG_IS_SET(settings->flags, WND_FLAGS_CURSOR_HIDDEN);
    s_Cursor = LoadWindowCursor();
    if (!s_Cursor)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to load windows cursor: %s.", GetWin32ErrorString());
        return NULL;
    }

    if (!RegisterWindowClass(s_CursorVisible))
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to register window class: %s", GetWin32ErrorString());
        return NULL;
    }

    s_Handle = CreateWindowHandle(settings);
    if (!s_Handle)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to create window handle: %s.", GetWin32ErrorString());
        return NULL;
    }

    s_DeviceContext = GetDC(s_Handle);
    if (!s_DeviceContext)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to acquire window device context: %s.", GetWin32ErrorString());
        return NULL;
    }

    s_GLContext = CreateOpenGLContext(FLAG_IS_SET(settings->flags, WND_FLAGS_TRANSPARENT_FRAMEBUFFER));
    if (!s_GLContext)
        return NULL; // error already set

    if (!wglMakeCurrent(s_DeviceContext, s_GLContext))
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to make OpenGL context current.");
        return NULL;
    }

    wglSwapIntervalEXT(FLAG_IS_SET(settings->flags, WND_FLAGS_ENABLE_VSYNC) ? 1 : 0);

    s_IsInitializing = false;

    Py_RETURN_NONE;
}

static PyObject *PyWindowShutdown(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    if (s_GLContext)
    {
        wglMakeCurrent(NULL, NULL);
        wglDeleteContext(s_GLContext);

        s_GLContext = NULL;
    }

    if (s_DeviceContext)
    {
        ReleaseDC(s_Handle, s_DeviceContext);
        s_DeviceContext = NULL;
    }

    if (s_Handle)
    {
        DestroyWindow(s_Handle);
        s_Handle = NULL;
    }

    UnregisterClassW(WIN32_CLASS_NAME, GetModuleHandleA(NULL));

    Py_RETURN_NONE;
}

static PyObject *PyWindowGetWidth(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(GetWidth());
}

static PyObject *PyWindowGetHeight(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(GetHeight());
}

static PyObject *PyWindowGetSize(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyTuple_Pack(2, PyWindowGetWidth(NULL, NULL), PyWindowGetHeight(NULL, NULL));
}

static PyObject *PyWindowGetX(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(s_WindowRect.left);
}

static PyObject *PyWindowGetY(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyLong_FromUnsignedLong(s_WindowRect.top);
}

static PyObject *PyWindowGetPosition(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyTuple_Pack(2, PyWindowGetX(NULL, NULL), PyWindowGetY(NULL, NULL));
}

static PyObject *PyWindowIsVisible(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyBool_FromLong(s_IsVisible);
}

static PyObject *PyWindowShouldClose(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    return PyBool_FromLong(s_ShouldClose);
}

static PyObject *PyWindowSetTitle(PyObject *UNUSED(self), PyObject *title)
{
    CHECK_ARG_STRING(title, NULL);

    SetWindowTextA(s_Handle, PyUnicode_AsUTF8(title));

    Py_RETURN_NONE;
}

static PyObject *PyWindowResize(PyObject *UNUSED(self), PyObject **args, Py_ssize_t argsCount)
{
    uint32_t width, height;
    if (!_PyArg_ParseStack(args, argsCount, "II", &width, &height))
        return NULL;

    SetWindowPos(s_Handle, NULL, width, height, 0, 0, SWP_NOMOVE);

    Py_RETURN_NONE;
}

static PyObject *PyWindowMove(PyObject *UNUSED(self), PyObject **args, Py_ssize_t argsCount)
{
    uint32_t x, y;
    if (!_PyArg_ParseStack(args, argsCount, "II", &x, &y))
        return NULL;

    SetWindowPos(s_Handle, NULL, 0, 0, x, y, SWP_NOSIZE);

    Py_RETURN_NONE;
}

static PyObject *PyWindow_SwapBuffers(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    SwapBuffers(s_DeviceContext);
    Py_RETURN_NONE;
}

static PyObject *PyWindow_ProcessEvents(PyObject *UNUSED(self), PyObject *UNUSED(args))
{
    MSG msg;
    while (PeekMessageA(&msg, s_Handle, 0, 0, PM_REMOVE))
    {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);

        if (s_WindowProcFailed)
            return NULL;
    }

    Py_RETURN_NONE;
}

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.graphics.window",
    .m_size = -1,
    .m_methods = (PyMethodDef[]){
        {"initialize", (PyCFunction)PyWindow_Initialize, METH_O, NULL},
        {"shutdown", PyWindowShutdown, METH_NOARGS, NULL},
        {"get_width", PyWindowGetWidth, METH_NOARGS, NULL},
        {"get_height", PyWindowGetHeight, METH_NOARGS, NULL},
        {"get_size", PyWindowGetSize, METH_NOARGS, NULL},
        {"get_x", PyWindowGetX, METH_NOARGS, NULL},
        {"get_y", PyWindowGetY, METH_NOARGS, NULL},
        {"get_position", PyWindowGetPosition, METH_NOARGS, NULL},
        {"is_visible", PyWindowIsVisible, METH_NOARGS, NULL},
        {"should_close", PyWindowShouldClose, METH_NOARGS, NULL},
        {"set_title", PyWindowSetTitle, METH_O, NULL},
        {"resize", (PyCFunction)PyWindowResize, METH_FASTCALL, NULL},
        {"move", (PyCFunction)PyWindowMove, METH_FASTCALL, NULL},
        {"swap_buffers", PyWindow_SwapBuffers, METH_NOARGS, NULL},
        {"process_events", PyWindow_ProcessEvents, METH_NOARGS, NULL},
        {0},
    },
};

PyMODINIT_FUNC PyInit_window()
{
    s_Events = PyAPI_Import("spyke.events");
    if (!s_Events)
        return NULL;

    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module)
        return NULL;

    if (PyModule_AddType(module, &PyWindowSettings_Type))
        return NULL;

    const EnumValue windowFlagsValues[] = {
        {"DEFAULT", WND_FLAGS_DEFAULT},
        {"RESIZABLE", WND_FLAGS_RESIZABLE},
        {"FULLSCREEN", WND_FLAGS_FULLSCREEN},
        {"BORDERLESS", WND_FLAGS_BORDERLESS},
        {"TRANSPARENT_FRAMEBUFFER", WND_FLAGS_TRANSPARENT_FRAMEBUFFER},
        {"CURSOR_HIDDEN", WND_FLAGS_CURSOR_HIDDEN},
        {"ENABLE_VSYNC", WND_FLAGS_ENABLE_VSYNC},
        {"ALLOW_FILE_DROP", WND_FLAGS_ALLOW_FILE_DROP},
        {0},
    };
    if (!PyEnum_Add(module, "WindowFlags", windowFlagsValues, false))
        return NULL;

    s_ResizeEvent = NewEvent();
    if (PyModule_AddObject(module, "resize_event", (PyObject *)s_ResizeEvent))
        return NULL;

    s_WindowMoveEvent = NewEvent();
    if (PyModule_AddObject(module, "move_event", (PyObject *)s_WindowMoveEvent))
        return NULL;

    s_CloseEvent = NewEvent();
    if (PyModule_AddObject(module, "close_event", (PyObject *)s_CloseEvent))
        return NULL;

    s_MouseMoveEvent = NewEvent();
    if (PyModule_AddObject(module, "mouse_move_event", (PyObject *)s_MouseMoveEvent))
        return NULL;

    s_ShowEvent = NewEvent();
    if (PyModule_AddObject(module, "show_event", (PyObject *)s_ShowEvent))
        return NULL;

    s_ScrollEvent = NewEvent();
    if (PyModule_AddObject(module, "scroll_event", (PyObject *)s_ScrollEvent))
        return NULL;

    s_KeyDownEvent = NewEvent();
    if (PyModule_AddObject(module, "key_down_event", (PyObject *)s_KeyDownEvent))
        return NULL;

    s_KeyUpEvent = NewEvent();
    if (PyModule_AddObject(module, "key_up_event", (PyObject *)s_KeyUpEvent))
        return NULL;

    s_ButtonDownEvent = NewEvent();
    if (PyModule_AddObject(module, "button_down_event", (PyObject *)s_ButtonDownEvent))
        return NULL;

    s_ButtonUpEvent = NewEvent();
    if (PyModule_AddObject(module, "button_up_event", (PyObject *)s_ButtonUpEvent))
        return NULL;

    s_CharEvent = NewEvent();
    if (PyModule_AddObject(module, "char_event", (PyObject *)s_CharEvent))
        return NULL;

    if (PyModule_AddType(module, &PyResizeEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyButtonUpEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyButtonDownEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyCharEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyKeyUpEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyKeyDownEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyScrollEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyShowEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyMouseMoveEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyCloseEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyMoveEventData_Type))
        return NULL;

    if (PyModule_AddType(module, &PyResizeEventData_Type))
        return NULL;

    return module;
}
