import time

class Delayer(object):
	__slots__ = ("_firstWait", "_waitTime", "_toWait", "_lastTime")

	def __init__(self, waitTime: float):
		self._firstWait = True
		self._waitTime = waitTime
		self._toWait = waitTime
		self._lastTime = 0.0

	def IsWaiting(self) -> bool:
		if self._firstWait:
			self._lastTime = time.perf_counter()
			self._firstWait = False

		if self._toWait <= 0.0:
			self._toWait = self._waitTime
			return False

		curTime = time.perf_counter()

		self._toWait -=  curTime - self._lastTime
		self._lastTime = curTime

		return True