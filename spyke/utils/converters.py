from ..exceptions import GraphicsException

import glm
import numpy as np
from PIL import Image
from typing import Union, TypeVar, NoReturn

T = TypeVar('T')

def EnsureObjectOfType(_type: T, obj: object) -> Union[T, NoReturn]:
	if isinstance(obj, _type):
		return obj
	else:
		raise TypeError(f"Object '{obj}' is of invalid type '{type(obj)}' (expected {_type}).")

def StrToBool(string: str) -> bool:
	_s = string.lower()
	
	if _s == "true":
		return True
	elif _s == "false":
		return False
	else:
		raise ValueError(f"Invalid string for conversion '{string}'.")

def IsArrayLike(obj: object) -> bool:
	return "__getitem__" in dir(obj)

def Mat4ToTuple(mat: glm.mat4) -> tuple:
	return tuple(mat[0]) + tuple(mat[1]) + tuple(mat[2]) + tuple(mat[3])

def PilImageToNp(im: Image.Image):
    im.load()

    encoder = Image._getencoder(im.mode, 'raw', im.mode)
    encoder.setimage(im.im)

    shape, typestr = Image._conv_type_shape(im)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise GraphicsException(f"Encoder error: {s}")
		
    return data

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