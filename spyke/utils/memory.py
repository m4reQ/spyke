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
	__VertexArrays = []
	__Buffers = []
	__Textures = []
	__Shaders = []
	__Framebuffers = []

	def AddObject(obj):
		name = type(obj).__name__

		if name == "VertexArray":
			ObjectManager.__VertexArrays.append(obj.ID)
		elif name == "Framebuffer":
			ObjectManager.__Framebuffers.append(obj.ID)
		elif "buffer" in name.lower() and name != "Framebuffer":
			ObjectManager.__Buffers.append(obj.ID)
		elif name == "Shader":
			ObjectManager.__Shaders.append(obj.ID)
		elif "texture" in name.lower():
			ObjectManager.__Textures.append(obj.ID)
		else:
			Log(f"Invalid object of type '{name}'.", LogLevel.Warning)
	
	def DeleteAll():
		for _ in ObjectManager.__Buffers:
			GL.glDeleteBuffers(len(ObjectManager.__Buffers), ObjectManager.__Buffers)
			
		Log(f"{len(ObjectManager.__Buffers)} buffers deleted succesfully.", LogLevel.Info)

		for _ in ObjectManager.__Framebuffers:
			GL.glDeleteFramebuffers(len(ObjectManager.__Framebuffers), ObjectManager.__Framebuffers)
			
		Log(f"{len(ObjectManager.__Framebuffers)} frame buffers deleted succesfully.", LogLevel.Info)
		
		for _ in ObjectManager.__Shaders:
			GL.glDeleteBuffers(len(ObjectManager.__Shaders), ObjectManager.__Shaders)
		
		Log(f"{len(ObjectManager.__Shaders)} shader programs deleted succesfully.", LogLevel.Info)

		for _ in ObjectManager.__Textures:
			GL.glDeleteTextures(len(ObjectManager.__Textures), ObjectManager.__Textures)
		
		Log(f"{len(ObjectManager.__Textures)} textures deleted succesfully.", LogLevel.Info)
		
		for _ in ObjectManager.__VertexArrays:
			GL.glDeleteVertexArrays(len(ObjectManager.__VertexArrays), ObjectManager.__VertexArrays)
		
		Log(f"{len(ObjectManager.__VertexArrays)} vertex arrays deleted succesfully.", LogLevel.Info)

		ObjectManager.__Buffers.clear()
		ObjectManager.__Framebuffers.clear()
		ObjectManager.__Shaders.clear()
		ObjectManager.__Textures.clear()
		ObjectManager.__VertexArrays.clear()

		gc.collect()