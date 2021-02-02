import threading
import time

class ProfileSession:
	def __init__(self):
		self.begin = 0
		self.time = 0
		self.tid = 0
		self._start = 0
		self.name = ""
		self.threadName = ""

class Profiler:
	__FileHeader = '{"otherData":{},"traceEvents":['
	__FileFooter = ']}'
	__SessionFormatString = '{{"cat":"function","dur":{0},"name":"{1}","ph":"X","pid":0,"tid":"{2}","ts":{3}}}'
	
	__File = None

	__FirstSession = True

	@staticmethod
	def BeginProfile(filepath: str):
		Profiler.__FirstSession = True

		Profiler.__File = open(filepath, "w+")
		Profiler.__File.write(Profiler.__FileHeader)
		Profiler.__File.flush()

	@staticmethod
	def EndProfile():
		Profiler.__File.write(Profiler.__FileFooter)
		Profiler.__File.close()
	
	@staticmethod
	def AddSession(session):
		comma = ""
		if not Profiler.__FirstSession:
			comma = ","
				
		Profiler.__File.write(comma + Profiler.__SessionFormatString.format(session.time, session.name, f"{session.threadName} ({session.tid})", session.begin))
		Profiler.__File.flush()

		Profiler.__FirstSession = False
	
	@staticmethod
	def StartSession(name: str) -> ProfileSession:
		session = ProfileSession()
		session.name = name
		session.tid = threading.get_ident()
		session.threadName = threading.current_thread().name
			
		session.begin = time.time_ns() // (10 ** 9)

		return session
	
	@staticmethod
	def EndSession(session: ProfileSession):
		session.time = (time.time_ns() - session.begin) / (10 ** 9)

		Profiler.AddSession(session)
	
def Timed(name):
	def innerDecor(func):
		def innerFunc(*args, **kwargs):
			session = ProfileSession()
			session.name = name
			session.tid = threading.get_ident()
			session.threadName = threading.current_thread().name
			
			session.begin = time.time_ns() / (10 ** 9)

			r = func(*args, **kwargs)

			session.time = (time.time_ns() / (10 ** 9)) - session.begin

			Profiler.AddSession(session)

			return r
		return innerFunc
	return innerDecor