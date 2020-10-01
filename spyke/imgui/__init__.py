from .imguiWindow import ImguiWindow
from ..debug import Log, LogLevel
from ..ecs import Scene
from ..ecs.entityManager import EntityManager

import tkinter
from tkinter import ttk

class ImGui(object):
	BackgroundColor = "#090a29"
	RowHeight = 20

	def __init__(self, x, y, width, height):
		self.window = ImguiWindow(self, x, y, width, height)
		self.window.OnFrame = self.OnFrame
		self.window.Setup = self.Setup

		self.scene = None
		self.renderer = None

		self.sceneUpdate = False

		self.window.Run()
	
	def OnFrame(self):
		if self.scene and self.sceneUpdate:
			height = 0
			for ent in self.scene._entities:
				entView = self.window.tree.insert("", ent, text = EntityManager.GetEntityName(ent))
				for comp in self.scene.components_for_entity(ent):
					self.window.tree.insert(entView, "end", text = type(comp).__name__.replace("Component", ''))
					height += ImGui.RowHeight
			
			height = max(height, self.window.Size[0])

			self.window.tree.configure(height = height)
			self.window.tree.update()

			self.sceneUpdate = False
		
		if self.renderer:
			rendererText = f"Draw calls: {self.renderer.drawsCount}\nVertex count: {self.renderer.vertexCount}"
			self.window.rendererTextwidget.delete(1.0, "end")
			self.window.rendererTextwidget.insert("end", rendererText)
	
	def SetScene(self, scene):
		self.scene = scene
		self.sceneUpdate = True
	
	def SetRenderer(self, renderer):
		self.renderer = renderer

	def Setup(self):
		#setup title bar
		self.window.Handle.title("Imgui")
		self.window.Handle.overrideredirect(True)

		titleBar = tkinter.Frame(self.window.Handle, bg = ImGui.BackgroundColor, relief = "raised", bd = 2, highlightbackground = "#dadbe0")
		title = tkinter.Label(titleBar, text = self.window.Title, bg = ImGui.BackgroundColor, fg = "#edeef2")
		closeButton = tkinter.Button(titleBar, text = 'x', fg = "#edeef2", bg = ImGui.BackgroundColor, bd = 0, command = self.window.Close)

		titleBar.pack(side = "top", fill = 'x')
		title.pack(side = "left")
		closeButton.pack(side = "right")

		titleBar.bind("<B1-Motion>", self.MoveByMouse)
		title.bind("<B1-Motion>", self.MoveByMouse)

		self.window.Handle.configure(bg = ImGui.BackgroundColor)

		#setup renderer view
		renderTitle = tkinter.Label(self.window.Handle, text = "Renderer stats:", bg = ImGui.BackgroundColor, fg = "#edeef2", anchor = 'w')
		renderTitle.pack(expand = False, fill = 'x')
		self.window.rendererTextwidget = tkinter.Text(self.window.Handle, bg = ImGui.BackgroundColor, fg = "#edeef2", height = 40)
		self.window.rendererTextwidget.pack(expand = False, fill = 'x')

		#setup entities treeview
		treeTitle = tkinter.Label(self.window.Handle, text = "Entities:", bg = ImGui.BackgroundColor, fg = "#edeef2", anchor = 'w')
		treeTitle.pack(expand = False, fill = 'x')
		self.window.tree = ttk.Treeview(self.window.Handle, show = "tree")
		self.window.tree.column("#0", width = self.window.Size[0], minwidth = self.window.Size[0], stretch = True)
		
		self.window.tree.pack(expand = False, fill = 'x')

	def Close(self):
		self.window.Close()
	
	def MoveByMouse(self, event):
		self.window.Move(event.x_root + self.window.mousePos[0], event.y_root + self.window.mousePos[1])