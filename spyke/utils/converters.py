import glm

def StrToBool(string: str) -> bool:
	_s = string.lower()
	
	if _s == "true":
		return True
	elif _s == "false":
		return False
	else:
		raise ValueError(f"Invalid string for conversion '{string}'.")

def IsArrayLike(obj: object) -> True:
	return "__getitem__" in dir(obj)

def Mat4ToTuple(mat: glm.mat4) -> tuple:
	return tuple(mat[0]) + tuple(mat[1]) + tuple(mat[2]) + tuple(mat[3])

def KwargParse(kwargs: dict, keywords: list, usage: str, copy = True) -> dict:
	if not usage.lower() in ["n", "r", "l"]:
		raise RuntimeError(f"Invalid usage mode: {usage}")
	
	if copy:
		_kwargs = kwargs.copy()
	else:
		_kwargs = kwargs

	if usage == "r":
		for name in keywords:
			try:
				del _kwargs[name]
			except KeyError:
				pass
		return _kwargs
	elif usage == "l":
		_dict = _kwargs.copy()
		for key in _kwargs.keys():
			if key not in keywords:
				del _dict[key]
		_kwargs = _dict
		return _kwargs
	else:
		return _kwargs