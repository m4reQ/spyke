class GLMarshal:
	__IsCleaned = False
	__Objects = []

	def ReleaseAll():
		if GLMarshal.__IsCleaned:
			return
		
		for obj in GLMarshal.__Objects:
			obj.Delete(False)

		GLMarshal.__IsCleaned = True
	
	def AddObjectRef(obj):
		try:
			GLMarshal.__Objects.append(obj)
		except ValueError:
			pass
		
	def RemoveObjectRef(obj):
		try:
			GLMarshal.__Objects.remove(obj)
		except ValueError:
			pass