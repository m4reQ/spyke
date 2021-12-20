import time

class Delayer:
	__slots__ = (
		'__weakref__',
		'_first_wait',
		'_wait_time',
		'_to_wait',
		'_last_time'
	)
	
	def __init__(self, wait_time: float):
		self._first_wait = True
		self._wait_time = wait_time
		self._to_wait = wait_time
		self._last_time = 0.0

	def is_waiting(self) -> bool:
		if self._first_wait:
			self._last_time = time.perf_counter()
			self._first_wait = False

		if self._to_wait <= 0.0:
			self._to_wait = self._wait_time
			return False

		curTime = time.perf_counter()

		self._to_wait -=  curTime - self._last_time
		self._last_time = curTime

		return True