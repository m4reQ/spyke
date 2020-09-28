from .guiWindow import GuiWindow
from ..debug import Log, LogLevel
from ..ecs import Scene
from ..ecs.components import *

import tkinter
from tkinter import ttk
import uuid

class EntitiesWindow(GuiWindow):
	BackgroundColor = "#090a29"
	RowHeight = 20

	def __init__(self, width, height, baseX = 0, baseY = 0):
		self.width = width
		self.height = height

		self.winX = baseX
		self.winY = baseY

		self.scene = None

		super().__init__()

	def Update(self):
		self.tree.column("#0", width = self.width, minwidth = self.width, stretch = True)
	
	def Reorganize(self):
		height = 0
		for ent in self.scene._entities:
			entView = self.tree.insert("", ent, text = str(ent))
			for comp in self.scene.components_for_entity(ent):
				self.tree.insert(entView, "end", text = type(comp).__name__.replace("Component", ''))
				height += EntitiesWindow.RowHeight
		
		height = max(height, self.height)

		self.tree.configure(height = height)

		self.tree.update()
		self.tree.pack(expand = True, fill = "both")
	
	def Setup(self):
		self.style = ttk.Style(self.Handle)
		self.style.configure("Treeview", background = EntitiesWindow.BackgroundColor, foreground="white", fieldbackground = EntitiesWindow.BackgroundColor, rowheight = EntitiesWindow.RowHeight)

		self.style.map("Treeview", background = [("selected", "#161966")], foreground = [("selected", "white")])

		self.Handle.title("Entities")
		self.Handle.overrideredirect(True)
		self.Handle.geometry(f"{self.width}x{self.height}+{self.winX}+{self.winY}")

		titleBar = tkinter.Frame(self.Handle, bg = EntitiesWindow.BackgroundColor, relief = "raised", bd = 2, highlightbackground = "#dadbe0")
		title = tkinter.Label(titleBar, text = self.Title ,bg = EntitiesWindow.BackgroundColor, fg = "#edeef2")
		closeButton = tkinter.Button(titleBar, text = 'x', fg = "#edeef2", bg = EntitiesWindow.BackgroundColor, bd = 0, command = self.OnClose)

		titleBar.pack(side = "top", fill = "x")
		title.pack(side = "left")
		closeButton.pack(side = "right")

		titleBar.bind("<B1-Motion>", self.Move)
		title.bind("<B1-Motion>", self.Move)

		self.Handle.configure(bg = EntitiesWindow.BackgroundColor)

		self.tree = ttk.Treeview(self.Handle, show = "tree", style = "Treeview")
		self.tree.column("#0", width = self.width, minwidth = self.width, stretch = True)
		
		self.tree.pack(expand = True, fill = "both")
	
	def Close(self):
		if self.isRunning:
			Log("Imgui entities viewer closed succesfully", LogLevel.Info)
		
	def SetScene(self, scene: Scene):
		self.scene = scene