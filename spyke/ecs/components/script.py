from ...debugging import Debug, LogLevel

import os
import importlib.util

def _DEFAULT_CALLER(func, obj):
	def inner(*args, **kwargs):
		return func(obj, *args, **kwargs)
	
	return inner

def _DEFAULT_PROCESS_FUNC(*args, **kwargs):
	return

class ScriptComponent(object):
	def _LoadScriptModule(self, filepath):
		spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(filepath))[0], filepath)
		ext = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(ext)

		return ext

	def __init__(self, file):
		self.filepath = os.path.abspath(file)
		self.entity = 0

		onProcessFound = False
		onInitFound = False

		ext = self._LoadScriptModule(self.filepath)

		for attr in dir(ext):
			if attr == "OnInit":
				getattr(ext, attr)(self)
				onInitFound = True

			if attr.startswith("__"):
				continue

			_attr = getattr(ext, attr)
			if callable(_attr):
				setattr(self, attr, _DEFAULT_CALLER(_attr, self))
				if attr == "OnProcess":
					onProcessFound = True
			else:
				setattr(self, attr, _attr)
		
		if not onInitFound:
			pass

		if not onProcessFound:
			Debug.Log("OnProcess function not found. Process function won't be called.", LogLevel.Warning)
			self.OnProcess = ScriptComponent._defaultcaller(_DEFAULT_PROCESS_FUNC, self)
		
		if not onInitFound:
			Debug.Log("OnInit function not found. Object members may not be properly initialized.", LogLevel.Warning)
