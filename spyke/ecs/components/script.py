from ...debug import Log, LogLevel

import os

class ScriptComponent(object):
	@staticmethod
	def __defaultcaller(func, _object):
		def inner(*args, **kwargs):
			return func(_object, *args, **kwargs)

		return inner

	def __init__(self, file):
		self.Filepath = os.path.abspath(file)
		self.entity = 0
		self.world = None

		ext = __import__(file[:-3], globals(), locals())
		
		func = None
		for attr in dir(ext):
			if attr == "OnInit":
				func = getattr(ext, attr)
				break

		if not func or not callable(func):
			Log("OnInit function not found. Object members may not be properly initialized.", LogLevel.Warning)
		else:
			if callable(func):
				func(self)

		onProcessFound = False
		self.Process = lambda *args, **kwargs: None
		for attr in dir(ext):
			if attr == "OnInit":
				continue

			_func = getattr(ext, attr)
			if callable(_func):
				if attr[:2] == "__":
					attr = "_" + type(self).__name__ + attr
				setattr(self, attr, ScriptComponent.__defaultcaller(_func, self))
			
			if attr == "OnProcess":
				onProcessFound = True
		
		if onProcessFound:
			self.Process = self.OnProcess
		else:
			Log("OnProcess function not found. Process function won't be called.", LogLevel.Warning)
	
	def GetComponent(self, componentType):
		return self.world.ComponentForEntity(self.entity, componentType)