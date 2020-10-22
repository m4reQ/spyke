from .functional import Static
from ..debug import Log, LogLevel

import ctypes
from OpenGL import GL
import gc

FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
INT_SIZE = ctypes.sizeof(ctypes.c_int)

GL_FLOAT_SIZE = 4
GL_INT_SIZE = 4

def GetGLTypeSize(_type: int) -> int:
	if _type == GL.GL_FLOAT:
		return 4
	elif _type == GL.GL_UNSIGNED_BYTE or _type == GL.GL_BYTE:
		return 1
	elif _type == GL.GL_UNSIGNED_SHORT or _type == GL.GL_SHORT:
		return 2
	elif _type == GL.GL_UNSIGNED_INT or _type == GL.GL_INT:
		return 4
	elif _type == GL.GL_DOUBLE:
		return 8
	elif _type == GL.GL_HALF_FLOAT:
		return 2
	elif _type == GL.GL_FIXED:
		return 4
	else:
		raise RuntimeError(f"Invalid enum: {_type}")

def GetPointer(value: int) -> ctypes.c_void_p:
	return ctypes.c_void_p(value)

def CollectGarbage() -> None:
	objCount = gc.get_count()[0]
	gc.collect()
	Log(f"Garbage collection freed {objCount - gc.get_count()[0]} objects.", LogLevel.Info)

class ObjectManager(Static):
	Objects = []

	def AddObject(obj):
		ObjectManager.Objects.append(obj)

	def DeleteObject(obj):
		if obj not in ObjectManager.Objects:
			Log(f"Cannot delete object of type {type(obj).__name__}, object not present.", LogLevel.Error)
			return
		
		try:
			obj.Delete()
		except Exception as e:
			raise RuntimeError(f"Cannot delete object of type '{type(obj).__name__}', {e}")

		ObjectManager.Objects.remove(obj)

		Log(f"Object of type {type(obj).__name__} deleted.", LogLevel.Info)

	def DeleteAll():
		for obj in ObjectManager.Objects:
			try:
				obj.Delete()
			except Exception as e:
				raise RuntimeError(f"Cannot delete object of type '{type(obj).__name__}', {e}")

			Log(f"Object of type {type(obj).__name__} deleted.", LogLevel.Info)
		
		ObjectManager.Objects.clear()
		
		Log("All objects deleted succesfully.", LogLevel.Info)