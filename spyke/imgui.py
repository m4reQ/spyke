from .debug import Log, LogLevel
from .ecs import Scene
from .ecs.entityManager import EntityManager

import tkinter
from tkinter import ttk

class ImGui(object):
	BackgroundColor = "#090a29"
	RowHeight = 20

	def __init__(self, x, y, width, height):
		self.handle = tkinter.Tk()

		self.scene = None
		self.renderer = None

		self.sceneUpdate = False
		
		self.closed = False

		self.x = x
		self.y = y
		self.width = width
		self.height = height

		self.mousePos = (0, 0)

		self.Setup()
	
	def OnFrame(self):
		if self.closed:
			return

		if self.scene and self.sceneUpdate:
			height = 0
			for ent in self.scene._entities:
				entView = self.tree.insert("", ent, text = EntityManager.GetEntityName(ent))
				for comp in self.scene.components_for_entity(ent):
					self.tree.insert(entView, "end", text = type(comp).__name__.replace("Component", ''))
					height += ImGui.RowHeight
			
			height = max(height, self.height)

			self.tree.configure(height = height)
			self.tree.update()

			self.sceneUpdate = False
		
		if self.renderer:
			rendererText = f"Draw calls: {self.renderer.drawsCount}\nVertex count: {self.renderer.vertexCount}"
			self.rendererTextwidget.delete(1.0, "end")
			self.rendererTextwidget.insert("end", rendererText)
		
		try:
			self.handle.update()
		except tkinter.TclError:
			pass
	
	def SetScene(self, scene):
		self.scene = scene
		self.sceneUpdate = True
	
	def SetRenderer(self, renderer):
		self.renderer = renderer

	def Setup(self):
		self.handle.protocol("WM_DELETE_WINDOW", self.Close)
		self.handle.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
		self.handle.bind("<Button-1>", self.__GetMousePos)

		#setup title bar
		self.handle.title("Imgui")
		self.handle.overrideredirect(True)

		titleBar = tkinter.Frame(self.handle, bg = ImGui.BackgroundColor, relief = "raised", bd = 2, highlightbackground = "#dadbe0")
		title = tkinter.Label(titleBar, text = self.handle.title(), bg = ImGui.BackgroundColor, fg = "#edeef2")
		closeButton = tkinter.Button(titleBar, text = 'x', fg = "#edeef2", bg = ImGui.BackgroundColor, bd = 0, command = self.Close)

		titleBar.pack(side = "top", fill = 'x')
		title.pack(side = "left")
		closeButton.pack(side = "right")

		titleBar.bind("<B1-Motion>", self.MoveByMouse)
		title.bind("<B1-Motion>", self.MoveByMouse)

		self.handle.configure(bg = ImGui.BackgroundColor)

		#setup renderer view
		renderTitle = tkinter.Label(self.handle, text = "Renderer stats:", bg = ImGui.BackgroundColor, fg = "#edeef2", anchor = 'w')
		renderTitle.pack(expand = False, fill = 'x')
		self.rendererTextwidget = tkinter.Text(self.handle, bg = ImGui.BackgroundColor, fg = "#edeef2", height = 40)
		self.rendererTextwidget.pack(expand = False, fill = 'x')

		#setup entities treeview
		treeTitle = tkinter.Label(self.handle, text = "Entities:", bg = ImGui.BackgroundColor, fg = "#edeef2", anchor = 'w')
		treeTitle.pack(expand = False, fill = 'x')
		self.tree = ttk.Treeview(self.handle, show = "tree")
		self.tree.column("#0", width = self.width, minwidth = self.width, stretch = True)
		
		self.tree.pack(expand = False, fill = 'x')

		Log("Imgui window started.", LogLevel.Info)

	def Close(self):
		self.closed = True

		try:
			self.handle.destroy()
		except Exception:
			pass

		Log("Imgui window closed.", LogLevel.Info)
	
	def Move(self, x, y):
		self.x = x
		self.y = y

		self.handle.geometry(f"+{self.x}+{self.y}")
	
	def MoveByMouse(self, event):
		self.Move(event.x_root + self.mousePos[0], event.y_root + self.mousePos[1])
	
	def Resize(self, width, height):
		self.width = width
		self.height = height

		self.handle.geometry(f"{self.width}x{self.height}")
	
	def __GetMousePos(self, event):
		xWin = self.handle.winfo_x()
		yWin = self.handle.winfo_y()
		startX = event.x_root
		startY = event.y_root

		self.mousePos = (xWin - startX, yWin - startY)