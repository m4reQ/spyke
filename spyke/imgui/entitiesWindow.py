from .guiWindow import GuiWindow
from ..debug import Log, LogLevel

import tkinter

class EntitiesWindow(GuiWindow):
	def __init__(self, width, height, baseX = 0, baseY = 0):
		self.width = width
		self.height = height

		self.winX = baseX
		self.winY = baseY

		super().__init__()
	
	def Update(self):
		pass
	
	def Setup(self):
		self.Handle.title("Entities")
		self.Handle.overrideredirect(True)
		self.Handle.geometry(f"{self.width}x{self.height}+{self.winX}+{self.winY}")

		titleBar = tkinter.Frame(self.Handle, bg = "#090a29", relief = "raised", bd = 2, highlightbackground = "#dadbe0")
		title = tkinter.Label(titleBar, text = self.Title ,bg = "#090a29", fg = "#edeef2")
		closeButton = tkinter.Button(titleBar, text = 'x', fg = "#edeef2", bg = "#090a29", bd = 0, command = self.OnClose)

		titleBar.pack(side = "top", fill = "x")
		title.pack(side = "left")
		closeButton.pack(side = "right")

		titleBar.bind("<B1-Motion>", self.Move)
		title.bind("<B1-Motion>", self.Move)

		self.Handle.configure(bg = "#090a29")
	
	def Close(self):
		if self.isRunning:
			Log("Imgui entities viewer closed succesfully", LogLevel.Info)