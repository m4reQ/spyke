import ctypes as ct
import enum
import os
import threading
import typing as t

WAIT_ABANDONED = 0x80
WAIT_OBJECT_0 = 0x0
WAIT_TIMEOUT = 0x102
WAIT_FAILED = 0xFFFFFFFF
INFINITE = 0xFFFFFFFF

DEFAULT_WAIT_TIMEOUT_MS = 250

class NotifyFlags(enum.IntFlag):
    CHANGE_FILE_NAME = 0x1
    CHANGE_DIR_NAME = 0x2
    CHANGE_ATTRIBUTES = 0x4
    CHANGE_SIZE = 0x8
    CHANGE_LAST_WRITE = 0x10
    CHANGE_SECURITY = 0x100

class DirectoryWatcher:
    def __init__(self,
                 directory_change_callback: t.Callable[[str], t.Any],
                 notify_flags: NotifyFlags,
                 wait_timeout_ms: int = DEFAULT_WAIT_TIMEOUT_MS,
                 path: str | None = None) -> None:
        self._path = path or os.getcwd()
        self._notify_flags = notify_flags
        self._callback = directory_change_callback
        self._wait_timeout_ms = wait_timeout_ms
        self._filepath_changed_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._is_running = True

    def start(self) -> None:
        self.stop()

        self._is_running = True
        self._thread = self._create_thread()
        self._thread.start()

    def stop(self) -> None:
        if self._thread is not None:
            self._is_running = False

            self._thread.join()
            self._thread = None

    def set_path(self, path: str) -> None:
        self._path = path
        self._filepath_changed_event.set()

    def _main(self) -> None:
        notify_object = _find_first_change_notification(
            self._path,
            self._notify_flags)

        while self._is_running:
            if self._filepath_changed_event.is_set():
                _find_close_change_notification(notify_object)
                notify_object = _find_first_change_notification(self._path, self._notify_flags)

                continue

            wait_result = _wait_for_single_object(notify_object, self._wait_timeout_ms)
            if wait_result == WAIT_OBJECT_0:
                self._callback(self._path)
                _find_next_change_notification(notify_object)
            elif wait_result == WAIT_TIMEOUT:
                pass
            elif wait_result == WAIT_FAILED:
                raise RuntimeError('Failed to wait on directory notification handle.')

        _find_close_change_notification(notify_object)

    def _create_thread(self) -> threading.Thread:
        return threading.Thread(target=self._main)

def _find_first_change_notification(path: str, notify_filter: int, watch_subtree: bool = False) -> ct.c_void_p:
    return _find_first_change_notification_fn(path, watch_subtree, notify_filter)

def _find_next_change_notification(notify_object: ct.c_void_p) -> bool:
    return _find_next_change_notification_fn(notify_object)

def _find_close_change_notification(notify_object: ct.c_void_p) -> bool:
    return _find_close_change_notification_fn(notify_object)

def _wait_for_single_object(handle: ct.c_void_p, milliseconds: int = INFINITE) -> int:
    return _wait_for_single_object_fn(handle, milliseconds)

_kernel32 = ct.windll.kernel32

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstchangenotificationa
_find_first_change_notification_fn = _kernel32.FindFirstChangeNotificationW
_find_first_change_notification_fn.argtypes = (ct.c_wchar_p, ct.c_bool, ct.c_uint32)
_find_first_change_notification_fn.restype = ct.c_void_p

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findclosechangenotification
_find_close_change_notification_fn = _kernel32.FindCloseChangeNotification
_find_close_change_notification_fn.argtypes = (ct.c_void_p,)
_find_close_change_notification_fn.restype = ct.c_bool

# https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findnextchangenotification
_find_next_change_notification_fn = _kernel32.FindNextChangeNotification
_find_next_change_notification_fn.argtypes = (ct.c_void_p,)
_find_next_change_notification_fn.restype = ct.c_bool

# https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject
_wait_for_single_object_fn = _kernel32.WaitForSingleObject
_wait_for_single_object_fn.argtypes = (ct.c_void_p, ct.c_uint32)
_wait_for_single_object_fn.restype = ct.c_uint32
