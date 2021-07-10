from ...debugging import Debug, LogLevel

import atexit

_isCleaned = False
_objects = []

@atexit.register
def ReleaseAll():
	global _isCleaned

	if _isCleaned:
		return
	
	for obj in _objects:
		obj.Delete(False)

	Debug.Log(f"All {len(_objects)} OpenGL objects have been successfully deleted.", LogLevel.Info)

	_isCleaned = True
	_objects.clear()

def AddObjectRef(obj):
	if obj in _objects:
		return

	_objects.append(obj)
	
def RemoveObjectRef(obj):
	try:
		_objects.remove(obj)
	except ValueError:
		pass