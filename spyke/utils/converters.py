import glm

def Mat4ToList(matrix: glm.mat4) -> list:
	matList = matrix.to_list()
	arr = []

	arr.extend(matList[0])
	arr.extend(matList[1])
	arr.extend(matList[2])
	arr.extend(matList[3])

	return arr

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