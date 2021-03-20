def noexcept(func):
	def __wrapper(*args, **kwargs):
		r = None
		try:
			r = func(*args, **kwargs)
		except Exception:
			pass
		return r
	return __wrapper

class StaticProperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class Static:
	def __decorator(_cls):
		def inner(cls):
			for attr in cls.__dict__:
				_attr = getattr(cls, attr)
				if callable(_attr):
					setattr(cls, attr, staticmethod(_attr))
			return cls
		return inner

	def __init_subclass__(cls, *args, **kwargs):
		return Static.__decorator(_cls = cls)
	
	def __new__(self, *args, **kwargs):
		raise RuntimeError("Cannot instantiate static class.")

class Enum:
	def __new__(self):
		raise RuntimeError("Cannot instantiate an enum.")