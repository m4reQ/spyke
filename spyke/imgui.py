from .debug import Log, LogLevel
from .utils	import Static
from .ecs import Scene
from .ecs.entityManager import EntityManager

import tkinter
from tkinter import ttk

class ImGui(Static):
	__Initialized = False

	Scene = None
	Renderer = None

	Title = "Imgui"

	BackgroundColor = "#090a29"
	TextColor = "#edeef2"

	#main window
	__Handle = tkinter.Tk()

	def Close():
		ImGui.Closed = True

		try:
			ImGui.__Handle.destroy()
		except Exception:
			pass

		Log("Imgui window closed.", LogLevel.Info)

	#containers
	__RendererDiv = tkinter.PanedWindow(__Handle)
	__SceneDiv = tkinter.PanedWindow(__Handle)
	__LogDiv = tkinter.PanedWindow(__Handle)

	#widgets
	__TitleBar = tkinter.Frame(__Handle, bg = BackgroundColor, relief = "raised", bd = 2, highlightbackground = "#dadbe0")
	__Title = tkinter.Label(__TitleBar, text = Title, bg = BackgroundColor, fg = TextColor)
	__CloseButton = tkinter.Button(__TitleBar, text = 'x', fg = TextColor, bg = BackgroundColor, bd = 0, command = Close)
	
	__SceneLabel = tkinter.Label(__SceneDiv)
	__SceneTree = ttk.Treeview(__SceneDiv)

	#positioning
	__RendererDiv.grid(row = 1, column = 0)
	__SceneDiv.grid(row = 1, column = 1)
	__LogDiv.grid(row = 1, column = 2)

	__TitleBar.grid(row = 0, column = 0)
	__Title.pack(side = "left")
	__CloseButton.pack(side = "right")

	SceneUpdate = False
	Closed = False

	Pos = (0, 0)
	Size = (0, 0)
	MousePos = (0, 0)

	def Initialize(x: int, y: int, width: int, height: int):
		if ImGui.__Initialized:
			Log("Imgui already initialized.", LogLevel.Warning)
			return

		ImGui.Pos = (x, y)
		ImGui.Size = (width, height)

		if not ImGui.Scene:
			Log("Imgui scene not set.", LogLevel.Warning)
		
		if not ImGui.Renderer:
			Log("Imgui renderer not set.", LogLevel.Warning)
		
		ImGui.Setup()
		
		ImGui.__Initialized = True

		Log("Imgui window started.", LogLevel.Info)
	
	def OnFrame():
		if ImGui.Closed:
			return

		# if ImGui.Scene and ImGui.SceneUpdate:
		# 	height = 0
		# 	for ent in self.scene._entities:
		# 		entView = self.tree.insert("", ent, text = EntityManager.GetEntityName(ent))
		# 		for comp in self.scene.components_for_entity(ent):
		# 			self.tree.insert(entView, "end", text = type(comp).__name__.replace("Component", ''))
		# 			height += ImGui.RowHeight
			
		# 	height = max(height, self.height)

		# 	self.tree.configure(height = height)
		# 	self.tree.update()

		# 	self.sceneUpdate = False
			
		try:
			ImGui.__Handle.update()
		except tkinter.TclError:
			pass

	def Setup():
		ImGui.__Handle.protocol("WM_DELETE_WINDOW", ImGui.Close)
		ImGui.__Handle.geometry(f"{ImGui.Size[0]}x{ImGui.Size[1]}+{ImGui.Pos[0]}+{ImGui.Pos[1]}")
		ImGui.__Handle.bind("<Button-1>", ImGui.__GetMousePos)
		ImGui.__Handle.title("Imgui")
		ImGui.__Handle.overrideredirect(True)
		ImGui.__Handle.configure(bg = ImGui.BackgroundColor)

		ImGui.__TitleBar.bind("<B1-Motion>", ImGui.MoveByMouse)
		ImGui.__Title.bind("<B1-Motion>", ImGui.MoveByMouse)
		ImGui.__TitleBar.configure(width = ImGui.Size[0])

	def SetScene(scene):
		ImGui.Scene = scene
		ImGui.SceneUpdate = True
	
	def SetRenderer(renderer):
		ImGui.Renderer = renderer
	
	def Move(x, y):
		ImGui.Pos = (x, y)

		ImGui.__Handle.geometry(f"+{ImGui.Pos[0]}+{ImGui.Pos[1]}")

	def MoveByMouse(event):
		ImGui.Move(event.x_root + ImGui.MousePos[0], event.y_root + ImGui.MousePos[1])
	
	def Resize(width, height):
		ImGui.Size = (width, height)

		ImGui.__Handle.geometry(f"{ImGui.Size[0]}x{ImGui.Size[1]}")
	
	def __GetMousePos(event):
		xWin = ImGui.__Handle.winfo_x()
		yWin = ImGui.__Handle.winfo_y()
		startX = event.x_root
		startY = event.y_root

		ImGui.MousePos = (xWin - startX, yWin - startY)

class __ImGui:
	def __init__(self, x, y, width, height):
		self.handle = tkinter.Tk()

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

	def Setup(self):
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