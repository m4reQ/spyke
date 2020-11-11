#region Import
from .editors import *
from .. import IS_NVIDIA
from ..debug import GetMemoryUsed, GetVideoMemoryCurrent, GLInfo
from ..ecs.entityManager import EntityManager
from ..ecs.components import *
from ..graphics import Renderer
from ..utils import RequestGC

import tkinter
from tkinter import ttk
#endregion

#This is just a large weight which forces other widgets with
#weight 1 to be practically not resizable. Add this to widgets
#that should be able to resize as grid_configure "weight" parameter.
DONT_RESIZE_OTHERS = 450

class ImGui:
	__Initialized = False
	__SceneUpdate = False
	__InspectorUpdate = False

	__ParentWindow = None
	__Scene = None

	__SelectedEntity = None
	__LastSelectedEntity = None
	__SelectedComponent = None

	__Font = ("Helvetica", 9)

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

	MainWindow.geometry("850x280")

	#widgets
	RenderStatsLabel = tkinter.Label(MainWindow, text = "Render stats", bd = 0)
	EntitiesLabel = tkinter.Label(MainWindow, text = "Entities", bd = 0)
	RenderStatsText = tkinter.Text(MainWindow, width = 35, height = 5, relief = "solid", bd = 1)
	ttk.Style().configure("Treeview", bd = 1, relief = "solid")
	EntitiesTree = ttk.Treeview(MainWindow, show = "tree", style = "Treeview")
	InspectorLabel = tkinter.Label(MainWindow, text = "Inspector", bd = 0)
	InspectorFrame = tkinter.Frame(MainWindow, bd = 1, relief = "solid", bg = "white")
	EntityName = tkinter.Label(InspectorFrame, text = "\n", bd = 0, bg = "white", fg = "white")
	ComponentName = tkinter.Label(InspectorFrame, text = "\n", bd = 0, bg = "white", font = (*__Font, "bold"), anchor = "w")

	#inspector widgets
	Inspectors = {
		"Color": ColorEditor(InspectorFrame),
		"Text": TextEditor(InspectorFrame)}

	#grid
	RenderStatsLabel.grid(row = 0, column = 0, sticky = "ew")
	RenderStatsText.grid(row = 1, column = 0, sticky = "news")
	EntitiesLabel.grid(row = 0, column = 1, sticky = "ew")
	EntitiesTree.grid(row = 1, column = 1, sticky = "news")
	InspectorLabel.grid(row = 0, column = 2, sticky = "news")
	InspectorFrame.grid(row = 1, column = 2, sticky = "news")

	#inspector grid
	EntityName.pack(fill = "x", expand = False)
	ComponentName.pack(fill = "x", expand = False)

	#region EventHandling
	def __SelectTreeview(event):
		sel = ImGui.EntitiesTree.selection()[0]

		item = ImGui.EntitiesTree.item(sel)
		parent = ImGui.EntitiesTree.parent(sel)

		if not parent:
			ent = str(item["values"][0])
			if ent != ImGui.__SelectedEntity:
				ImGui.ComponentName.configure(text = "\n")
				ImGui.__UnbindEditors()

			ImGui.__SelectedEntity = ent
			ImGui.__SelectedComponent = None
		else:
			_item = ImGui.EntitiesTree.item(parent)
			ImGui.__SelectedEntity = str(_item["values"][0])

			typeName = item["values"][0]
			compType = eval(typeName.replace("<class 'spyke.ecs.components.", '')[:-2])
			ImGui.__SelectedComponent = ImGui.__Scene.ComponentForEntity(ImGui.__SelectedEntity, compType)
		
		ImGui.__InspectorUpdate = True

	EntitiesTree.bind('<<TreeviewSelect>>', __SelectTreeview)
	#endregion

	def __UnbindEditors():
		for e in ImGui.Inspectors.values():
			e.Forget()
	
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

		RequestGC()

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
		if not ImGui.__InspectorUpdate:
			return
		
		if ImGui.__SelectedEntity:
			ImGui.EntityName.configure(text = EntityManager.GetEntityName(ImGui.__SelectedEntity), bg = "#545659")
		else:
			ImGui.EntityName.configure(text = "\n", bg = "white")
		
		if not ImGui.__SelectedComponent:
			ImGui.__InspectorUpdate = False
			return

		if type(ImGui.__SelectedComponent) == ColorComponent:
			ImGui.ComponentName.configure(text = "Color")
			ImGui.Inspectors["Color"].SetComp(ImGui.__SelectedComponent)
			ImGui.__UnbindEditors()
			ImGui.Inspectors["Color"].Use()
		elif type(ImGui.__SelectedComponent) == TextComponent:
			ImGui.ComponentName.configure(text = "Text")
			ImGui.Inspectors["Text"].SetComp(ImGui.__SelectedComponent)
			ImGui.__UnbindEditors()
			ImGui.Inspectors["Text"].Use()
		else:
			ImGui.ComponentName.configure(text = "\n")
			ImGui.__UnbindEditors()
		
		ImGui.__InspectorUpdate = False