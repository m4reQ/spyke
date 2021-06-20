from ...debugging import Debug, LogLevel

import atexit

class GLMarshal:
	__IsCleaned = False
	__Objects = []

	@atexit.register
	def ReleaseAll():
		if GLMarshal.__IsCleaned:
			return
		
		for obj in GLMarshal.__Objects:
			obj.Delete(False)

		GLMarshal.__IsCleaned = True
		GLMarshal.__Objects.clear()

		Debug.Log("All OpenGL objects have been successfully deleted.", LogLevel.Info)

	def AddObjectRef(obj):
		if obj in GLMarshal.__Objects:
			return

		GLMarshal.__Objects.append(obj)
		
	def RemoveObjectRef(obj):
		try:
			GLMarshal.__Objects.remove(obj)
		except ValueError:
			pass