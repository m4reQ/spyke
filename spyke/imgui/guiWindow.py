from ..utils import noexcept

import tkinter

class GuiWindow(object):
	def __init__(self):
		self.isRunning = True
		self.mousePos = (0, 0)

		self.__handle = tkinter.Tk()

		self.__handle.protocol("WM_DELETE_WINDOW", self.OnClose)
		self.__handle.bind('<Button-1>', self.__GetMousePos)

		self.Setup()
	
	def Setup(self):
		pass
	
	def Update(self):
		pass

	def Close(self):
		pass

	@noexcept
	def OnUpdate(self):
		if not self.isRunning:
			return
			
		self.Update()

		try:
			self.__handle.update()
		except tkinter.TclError:
			pass
	
	@noexcept
	def OnClose(self):
		self.Close()

		try:
			self.__handle.destroy()
		except Exception:
			pass
		
		self.isRunning = False
	
	def __GetMousePos(self, event):
		xWin = self.__handle.winfo_x()
		yWin = self.__handle.winfo_y()
		startX = event.x_root
		startY = event.y_root

		self.mousePos = (xWin - startX, yWin - startY)
	
	def Move(self, event):
		self.__handle.geometry(f"{self.__handle.winfo_width()}x{self.__handle.winfo_height()}+{event.x_root + self.mousePos[0]}+{event.y_root + self.mousePos[1]}")
	
	@property
	def Handle(self):
		return self.__handle
	
	@property
	def Title(self):
		return self.__handle.title()
	
	@property
	def Size(self):
		return (self.__handle.winfo_width(), self.__handle.winfo_height())
	
	@property
	def Position(self):
		return (self.__handle.winfo_rootx(), self.__handle.winfo_rooty())
