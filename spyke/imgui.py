#region Import
from . import IS_NVIDIA
from .debug import GetMemoryUsed, GetVideoMemoryCurrent, GLInfo
from .ecs.entityManager import EntityManager
from .ecs.components import *
from .graphics import Renderer

import tkinter
from tkinter import ttk
#endregion

#This is just a large weight which forces other widgets with
#weight 1 to be practically not resizable. Add this to widgets
#that should be able to resize as grid_configure "weight" parameter.
DONT_RESIZE_OTHERS = 450

class TextEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.var = tkinter.StringVar()
		self.entry = tkinter.Entry(master, textvariable = self.var)

		self.var.trace_add("write", self.EditText)
		self.comp = None

	def EditText(self, *args):
		self.comp.Text = self.var.get()
	
	def SetComp(self, comp):
		self.comp = comp
		self.var.set(comp.Text)

	def Use(self):
		self.entry.pack(fill = "x", expand = True)

	def Forget(self):
		self.entry.forget()

class ColorEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.redSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues)
		self.blueSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues)
		self.greenSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues)
		self.alphaSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues)

		self.comp = None
	
	def ChangeValues(self, _):
		if not self.comp:
			return

		self.comp.R = self.redSlider.get()
		self.comp.G = self.greenSlider.get()
		self.comp.B = self.blueSlider.get()
		self.comp.A = self.alphaSlider.get()

	def Use(self):
		self.redSlider.pack(fill = "x", expand = True)
		self.blueSlider.pack(fill = "x", expand = True)
		self.greenSlider.pack(fill = "x", expand = True)
		self.alphaSlider.pack(fill = "x", expand = True)
	
	def Forget(self):
		self.redSlider.forget()
		self.blueSlider.forget()
		self.greenSlider.forget()
		self.alphaSlider.forget()
	
	def SetComp(self, comp):
		self.comp = comp

		self.redSlider.set(comp.R)
		self.greenSlider.set(comp.G)
		self.blueSlider.set(comp.B)
		self.alphaSlider.set(comp.A)

class ImGui:
	__Initialized = False
	__SceneUpdate = False

	__ParentWindow = None
	__Scene = None

	__SelectedEntity = None
	__SelectedComponent = None

	__StatsTextTemplate = """Draws count: {0}
Vertices count: {1}
Memory used: {2:.2f}kB
Video memory used: {3}
Window size: {4}x{5}"""

	MainWindow = tkinter.Tk()
	MainWindow.title("Imgui")
	MainWindow.grid_rowconfigure(0, weight = 1)
	MainWindow.grid_rowconfigure(1, weight = DONT_RESIZE_OTHERS)
	MainWindow.grid_rowconfigure(2, weight = 1)
	MainWindow.grid_rowconfigure(3, weight = DONT_RESIZE_OTHERS)
	MainWindow.grid_columnconfigure(0, weight = 2)
	MainWindow.grid_columnconfigure(1, weight = 5)
	MainWindow.grid_columnconfigure(2, weight = 5)

	#widgets
	RenderStatsLabel = tkinter.Label(MainWindow, text = "Render stats", bd = 0)
	EntitiesLabel = tkinter.Label(MainWindow, text = "Entities", bd = 0)
	RenderStatsText = tkinter.Text(MainWindow, width = 35, height = 5, relief = "solid", bd = 1)
	ttk.Style().configure("Treeview", bd = 1, relief = "solid")
	EntitiesTree = ttk.Treeview(MainWindow, show = "tree", style = "Treeview")
	InspectorLabel = tkinter.Label(MainWindow, text = "Inspector", bd = 0)
	InspectorFrame = tkinter.Frame(MainWindow, bd = 1, relief = "solid", bg = "white")
	EntityName = tkinter.Label(InspectorFrame, text = "\n", bd = 0, bg = "white", fg = "white")
	ComponentName = tkinter.Label(InspectorFrame, text = "\n", bd = 0, bg = "white")

	#inspector widgets
	ColorEditor = ColorEditor(InspectorFrame)
	TextEditor = TextEditor(InspectorFrame)

	#grid
	RenderStatsLabel.grid(row = 0, column = 0, sticky = "ew")
	RenderStatsText.grid(row = 1, column = 0, sticky = "news")
	EntitiesLabel.grid(row = 0, column = 1, sticky = "ew")
	EntitiesTree.grid(row = 1, column = 1, sticky = "news")
	InspectorLabel.grid(row = 0, column = 2, sticky = "news")
	InspectorFrame.grid(row = 1, column = 2, sticky = "news")

	#inspector grid
	EntityName.pack(fill = "x", expand = True)
	ComponentName.pack(fill = "x", expand = True)

	#region EventHandling
	def __SelectTreeview(event):
		sel = ImGui.EntitiesTree.selection()[0]

		item = ImGui.EntitiesTree.item(sel)
		parent = ImGui.EntitiesTree.parent(sel)

		if not parent:
			ImGui.__SelectedEntity = str(item["values"][0])
			ImGui.__SelectedComponent = None
		else:
			_item = ImGui.EntitiesTree.item(parent)
			ImGui.__SelectedEntity = str(_item["values"][0])

			typeName = item["values"][0]
			compType = eval(typeName.replace("<class 'spyke.ecs.components.", '')[:-2])
			ImGui.__SelectedComponent = ImGui.__Scene.ComponentForEntity(ImGui.__SelectedEntity, compType)

	EntitiesTree.bind('<<TreeviewSelect>>', __SelectTreeview)
	#endregion

	def __UnbindEditors():
		ImGui.ColorEditor.Forget()
		ImGui.TextEditor.Forget()
	
	def BindScene(scene) -> None:
		ImGui.__Scene = scene
		ImGui.__SceneUpdate = True

	def UpdateScene() -> None:
		ImGui.__SceneUpdate = True
	
	def Initialize(parentWindow) -> None:
		ImGui.__Initialized = True
		ImGui.__ParentWindow = parentWindow
	
	def IsInitialized() -> bool:
		return ImGui.__Initialized
	
	def Close() -> None:
		ImGui.__Initialized = False
		try:
			ImGui.MainWindow.destroy()
		except tkinter.TclError:
			pass

	def OnFrame() -> None:
		if not ImGui.__Initialized:
			return

		try:
			ImGui.__HandleRenderStats()
			ImGui.__HandleEntities()
			ImGui.__HandleInspector()
			ImGui.MainWindow.update()
		except tkinter.TclError:
			pass
	
	def __HandleEntities() -> None:
		if not ImGui.__Scene or not ImGui.__SceneUpdate:
			return
		
		for child in ImGui.EntitiesTree.get_children():
			ImGui.EntitiesTree.delete(child)
		
		for ent in ImGui.__Scene._entities:
			entView = ImGui.EntitiesTree.insert("", ent, text = EntityManager.GetEntityName(ent), values = (ent,))
			for comp in ImGui.__Scene.ComponentsForEntity(ent):
				ImGui.EntitiesTree.insert(entView, "end", text = type(comp).__name__.replace("Component", ""), values = (type(comp),))
		
		ImGui.__SceneUpdate = False

	def __HandleRenderStats() -> None:
		if not IS_NVIDIA:
			vidMemUsed = "unavailable"
		else:
			vidMemUsed = f"{((GLInfo.MemoryAvailable - GetVideoMemoryCurrent()) / 1000000.0):.3f} GB"
		
		memUsed = GetMemoryUsed() / 1000.0

		text = ImGui.__StatsTextTemplate.format(Renderer.DrawsCount, Renderer.VertexCount, memUsed, vidMemUsed, ImGui.__ParentWindow.width, ImGui.__ParentWindow.height)

		try:
			ImGui.RenderStatsText.delete(1.0, "end")
			ImGui.RenderStatsText.insert("end", text)
		except tkinter.TclError:
			pass
	
	def __HandleInspector() -> None:
		if not ImGui.__SelectedComponent:
			return
		
		if ImGui.__SelectedEntity:
			ImGui.EntityName.configure(text = EntityManager.GetEntityName(ImGui.__SelectedEntity), bg = "#545659")
		else:
			ImGui.EntityName.configure(text = "\n", bg = "white")

		if type(ImGui.__SelectedComponent) == ColorComponent:
			ImGui.ComponentName.configure(text = "Color")
			ImGui.ColorEditor.SetComp(ImGui.__SelectedComponent)
			ImGui.__UnbindEditors()
			ImGui.ColorEditor.Use()
		elif type(ImGui.__SelectedComponent) == TextComponent:
			ImGui.ComponentName.configure(text = "Text")
			ImGui.TextEditor.SetComp(ImGui.__SelectedComponent)
			ImGui.__UnbindEditors()
			ImGui.TextEditor.Use()
		else:
			ImGui.ComponentName.configure(text = "\n")
			ImGui.ColorEditor.Forget()

if __name__ == "__main__":
	ImGui.Initialize(None)
	while True:
		ImGui.OnFrame()