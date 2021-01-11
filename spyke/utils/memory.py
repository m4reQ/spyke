from .functional import Static
from ..debug import Log, LogLevel

import ctypes
from OpenGL import GL
import gc
import threading
import pickle

FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
INT_SIZE = ctypes.sizeof(ctypes.c_int)

GL_FLOAT_SIZE = 4
GL_INT_SIZE = 4

__GL_TYPE_SIZES = {
	GL.GL_DOUBLE: 8,
	GL.GL_FIXED: 4,
	GL.GL_FLOAT: 4,
	GL.GL_UNSIGNED_INT: 4,
	GL.GL_INT: 4,
	GL.GL_UNSIGNED_SHORT: 2,
	GL.GL_SHORT: 2,
	GL.GL_HALF_FLOAT: 2,
	GL.GL_UNSIGNED_BYTE: 1,
	GL.GL_BYTE: 1}

def __ThreadedGC():
	__GC_FLAG.wait()

	objCount = gc.get_count()[0]
	gc.collect()
	Log(f"Garbage collection freed {objCount - gc.get_count()[0]} objects.", LogLevel.Info)
	__GC_FLAG.clear()

__GC_FLAG = threading.Event()
__GC_THREAD = threading.Thread(target = __ThreadedGC, name = "spyke.gc")
__GC_THREAD.start()

def RequestGC():
	__GC_FLAG.set()

def GetGLTypeSize(_type: int) -> int:
	try:
		return __GL_TYPE_SIZES[_type]
	except KeyError:
		raise RuntimeError(f"Invalid enum: {_type}")

def GetPointer(value: int) -> ctypes.c_void_p:
	return ctypes.c_void_p(value)

class Serializable(object):
	ClassName = "Serializable"

	@classmethod
	def Deserialize(cls, data: str) -> object:
		pass

	@classmethod
	def DeserializeBin(cls, data: bytes) -> object:
		return pickle.loads(data)
	
	def Serialize(self) -> str:
		pass

	def SerializeBin(self) -> bytes:
		return pickle.dumps(self)

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