#region Import
from . import IS_NVIDIA
from .debug import GetMemoryUsed, GetVideoMemoryCurrent, GLInfo
from .ecs.entityManager import EntityManager
from .graphics import Renderer

import tkinter
from tkinter import ttk
#endregion

class ImGui:
	__Initialized = False
	__SceneUpdate = False

	__ParentWindow = None
	__Scene = None

	__StatsTextTemplate = """Draws count: {0}
Vertices count: {1}
Memory used: {2:.2f}kB
Video memory used: {3}
Window size: {4}x{5}"""

	MainWindow = tkinter.Tk()
	MainWindow.title("Imgui")
	MainWindow.grid_rowconfigure(0, weight = 1)
	MainWindow.grid_rowconfigure(1, weight = 5)
	MainWindow.grid_rowconfigure(2, weight = 1)
	MainWindow.grid_columnconfigure(1, weight = 1)

	#widgets
	RenderStatsLabel = tkinter.Label(MainWindow, text = "Render stats", bd = 0)
	EntitiesLabel = tkinter.Label(MainWindow, text = "Entities", bd = 0)
	RenderStatsText = tkinter.Text(MainWindow, width = 35, height = 5)
	EntitiesTree = ttk.Treeview(MainWindow, show = "tree")
	InspectorFrame = tkinter.Frame(MainWindow)

	#inspector widgets


	#grid
	RenderStatsLabel.grid(row = 0, column = 0, sticky = "n")
	RenderStatsText.grid(row = 1, column = 0, sticky = "news", padx = 1)
	EntitiesLabel.grid(row = 0, column = 1, sticky = "n")
	EntitiesTree.grid(row = 1, column = 1, sticky = "news", padx = 1)
	InspectorFrame.grid(row = 2, column = 1, sticky = "news")
	
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

		ImGui.__HandleRenderStats()
		ImGui.__HandleEntities()
		
		try:
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
				ImGui.EntitiesTree.insert(entView, "end", text = type(comp).__name__.replace("Component", ""))
		
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

if __name__ == "__main__":
	ImGui.Initialize(None)
	while True:
		ImGui.OnFrame()