# from .debug import Log, LogLevel, GetVideoMemoryCurrent, GLInfo, GetMemoryUsed
# from .utils	import Static, KwargParse
# from . import IS_NVIDIA
# from .ecs import Scene
# from .ecs.entityManager import EntityManager

import tkinter
from tkinter import ttk
############################################ PRACUJ KURWAAAAAAAA ###############################################

class ToggledFrame(tkinter.Frame):
	def __init__(self, master, *args, **options):
		super().__init__(master, *args, **KwargParse(options, ["bg"], "l"))
		
		self.show = tkinter.IntVar(value = 0)
		
		self.__titleFrame = tkinter.Frame(self)

		self.__title = tkinter.Label(self.__titleFrame, anchor = "w", **KwargParse(options, ["text", "font", "fg", "bg"], "l"))
		ttk.Style(master).configure("Toolbutton", **KwargParse(options, ["bg"], "l"))
		self.__button = ttk.Checkbutton(self.__titleFrame, text = "+", command = self.__Toggle, variable = self.show, style = "Toolbutton")
		self.__button.pack(side = "right")
		self.__title.pack(side = "left", fill = "x", expand = True)

		self.__titleFrame.pack(fill = "x")
		
		self.Frame = tkinter.Frame(self, bd = 1, **KwargParse(options, ["bg"], "l"))
	
	def __Toggle(self):
		if bool(self.show.get()):
			self.Frame.pack(fill = "x")
			self.__button.configure(text = "-")
		else:
			self.Frame.forget()
			self.__button.configure(text = "+")

class __ImGui(Static):
	__Initialized = False

	Scene = None
	Renderer = None

	Title = "Imgui"

	BackgroundColor = "#090a29"
	TextColor = "#edeef2"
	LabelFont = ("Helvetica", 12, "bold")
	RowHeight = 20

	SelectedEntity = None
	BaseTreeHeight = 0
	TreeHeightChange = 0

	#main window
	__Handle = tkinter.Tk()

	def IsInitialized():
		return ImGui.__Initialized

	def Close():
		ImGui.Closed = True

		try:
			ImGui.__Handle.destroy()
		except Exception:
			pass

		Log("Imgui window closed.", LogLevel.Info)

	#widgets
	__TitleBar = tkinter.Frame(__Handle, bg = BackgroundColor, relief = "raised", bd = 2, highlightbackground = "#dadbe0")
	__Title = tkinter.Label(__TitleBar, text = Title, bg = BackgroundColor, fg = TextColor)
	__CloseButton = tkinter.Button(__TitleBar, text = 'x', fg = TextColor, bg = BackgroundColor, bd = 0, command = Close)
	__RendererFrame = ToggledFrame(__Handle, text = "Renderer stats", font = LabelFont, bg = BackgroundColor, fg = TextColor)
	__RenderStats = tkinter.Text(__RendererFrame.Frame, bg = BackgroundColor, fg = TextColor, bd = 0)
	__EntitiesLabel = tkinter.Label(__Handle, bg = BackgroundColor, fg = TextColor, text = "Entities:", bd = 0, anchor = "w", font = LabelFont)
	__EntitiesTree = ttk.Treeview(__Handle, show = "tree")

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

		ImGui.TreeHeightChange = 0
		
		if ImGui.Renderer:
			ImGui.__RenderStats.delete(1.0, "end")

			text = f"Draws count: {ImGui.Renderer.drawsCount}\nVertices count: {ImGui.Renderer.vertexCount}\nMemory used: {GetMemoryUsed() / 1000}kB\n"

			mem = GLInfo.MemoryAvailable - GetVideoMemoryCurrent()
			if IS_NVIDIA:
				text += f"Video memory used: {mem / 1000000.0}GB\n"
			else:
				text += f"Video memory used: unavailable\n"

			ImGui.__RenderStats.insert("end", text)

		if ImGui.SceneUpdate:
			for child in ImGui.__EntitiesTree.get_children():
				ImGui.__EntitiesTree.delete(child)
			
			for ent in ImGui.Scene._entities:
				entView = ImGui.__EntitiesTree.insert("", ent, text = EntityManager.GetEntityName(ent), values = (ent,))
				for comp in ImGui.Scene.components_for_entity(ent):
					ImGui.__EntitiesTree.insert(entView, "end", text = type(comp).__name__.replace("Component", ''))
				ImGui.BaseTreeHeight += 1

			ImGui.__EntitiesTree.configure(height = ImGui.BaseTreeHeight + ImGui.TreeHeightChange)
			ImGui.__EntitiesTree.update()

			ImGui.SceneUpdate = False
						
		try:
			ImGui.__Handle.update()
		except tkinter.TclError:
			pass
	
	def __OpenTreeItem(event):
		item = ImGui.__EntitiesTree.focus()
		ent = ImGui.__EntitiesTree.item(item)["values"][0]
		entHeight = len(ImGui.Scene.components_for_entity(ent))
		ImGui.__EntitiesTree.configure(height = ImGui.BaseTreeHeight + entHeight)
		ImGui.__EntitiesTree.update()
	
	def __SelectTreeItem(event):
		ImGui.SelectedEntity = ImGui.__EntitiesTree.item(ImGui.__EntitiesTree.focus())
	
	def __CloseTreeItem(event):
		ImGui.__EntitiesTree.configure(height = ImGui.BaseTreeHeight)
		ImGui.__EntitiesTree.update()

	def Setup():
		ImGui.__Handle.update()
		ImGui.__Handle.protocol("WM_DELETE_WINDOW", ImGui.Close)
		ImGui.__Handle.bind("<Button-1>", ImGui.__GetMousePos)
		ImGui.__Handle.title("Imgui")
		ImGui.__Handle.overrideredirect(True)
		ImGui.__Handle.geometry(f"{ImGui.Size[0]}x{ImGui.Size[1]}+{ImGui.Pos[0]}+{ImGui.Pos[1]}")
		ImGui.__Handle.configure(bg = ImGui.BackgroundColor)

		ImGui.__TitleBar.configure(width = ImGui.Size[0])
		ImGui.__TitleBar.bind("<B1-Motion>", ImGui.MoveByMouse)
		ImGui.__Title.bind("<B1-Motion>", ImGui.MoveByMouse)
		ImGui.__Title.pack(side = "left")
		ImGui.__CloseButton.pack(side = "right")
		ImGui.__TitleBar.pack(side = "top", fill = "x")

		ImGui.__RenderStats.configure(height = 3)
		ImGui.__RenderStats.pack(fill = "x")

		ImGui.__RendererFrame.pack(fill = "x")

		ImGui.__EntitiesLabel.pack(fill = "x")

		ImGui.__EntitiesTree.bind("<ButtonRelease-1>", ImGui.__SelectTreeItem)
		ImGui.__EntitiesTree.bind("<<TreeviewOpen>>", ImGui.__OpenTreeItem)
		ImGui.__EntitiesTree.bind("<<TreeviewClose>>", ImGui.__CloseTreeItem)
		ImGui.__EntitiesTree.pack(fill = "x", expand = False)

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