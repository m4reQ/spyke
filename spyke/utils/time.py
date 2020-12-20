import time

class Delayer(object):
	def __init__(self, waitTime: float):
		self.__firstWait = True
		self.__waitTime = waitTime
		self.__toWait = waitTime
		self.__lastTime = 0.0

	def IsWaiting(self) -> bool:
		if self.__firstWait:
			self.__lastTime = time.perf_counter()
			self.__firstWait = False

		if self.__toWait <= 0.0:
			self.__toWait = self.__waitTime
			return False

		curTime = time.perf_counter()

		self.__toWait -=  curTime - self.__lastTime
		self.__lastTime = curTime
		return True

class Timer:
	__Start = 0.0
	
	@staticmethod
	def Start() -> None:
		Timer.__Start = time.perf_counter()
	
	@staticmethod
	def Stop() -> float:
		return time.perf_counter() - Timer.__Start
	
	@staticmethod
	def GetCurrent() -> float:
		return time.perf_counter()