from .enums import GLType, VertexAttribType
from .debug import Log, LogLevel

import ctypes
from OpenGL import GL
import gc

FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
INT_SIZE = ctypes.sizeof(ctypes.c_int)

GL_FLOAT_SIZE = 4
GL_INT_SIZE = 4

def GetGLTypeSize(type: GLType or VertexAttribType):
	if type == GL.GL_FLOAT:
		return 4
	elif type == GL.GL_UNSIGNED_BYTE or type == GL.GL_BYTE:
		return 1
	elif type == GL.GL_UNSIGNED_SHORT or type == GL.GL_SHORT:
		return 2
	elif type == GL.GL_UNSIGNED_INT or type == GL.GL_INT:
		return 4
	elif type == GL.GL_DOUBLE:
		return 8
	elif type == GL.GL_HALF_FLOAT:
		return 2
	elif type == GL.GL_FIXED:
		return 4
	else:
		raise RuntimeError(f"Invalid enum: {type}")

def GetPointer(value):
	return ctypes.c_void_p(value)

def GetQuadIndexData(count):
	data = []

	offset = 0
	i = 0
	while i < count:
		data.extend([
			0 + offset,
			1 + offset,
			2 + offset,
			2 + offset,
			3 + offset,
			0 + offset])
		
		offset += 4
		i += 6
	
	return data

def CollectGarbage():
	objCount = gc.get_count()[0]

	gc.collect()

	Log(f"Garbage collection freed {objCount - gc.get_count()[0]} objects.", LogLevel.Info)

class ObjectManager:
	Objects = []

	@staticmethod
	def AddObject(obj):
		ObjectManager.Objects.append(obj)

	@staticmethod
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

	@staticmethod
	def DeleteAll():
		for obj in ObjectManager.Objects:
			try:
				obj.Delete()
			except Exception as e:
				raise RuntimeError(f"Cannot delete object of type '{type(obj).__name__}', {e}")

			Log(f"Object of type {type(obj).__name__} deleted.", LogLevel.Info)
		
		ObjectManager.Objects.clear()
		
		Log("All objects deleted succesfully.", LogLevel.Info)
