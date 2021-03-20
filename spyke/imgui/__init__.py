#region Import
from .widgets import *
from .dialogWindow import DialogWindow
from ..debugging import Debug, LogLevel
from ..ecs.components import *
from ..graphics import Renderer
from ..graphics.contextInfo import ContextInfo
#from ..sceneLoader import SaveScene

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import random
from pydoc import locate
import threading
import gc
#endregion

#This is just a large weight which forces other widgets with
#weight 1 to be practically not resizable. Add this to widgets
#that should be able to resize as grid_configure "weight" parameter.
DONT_RESIZE_OTHERS = 450

class ImGui:
	__Initialized = False
	__IsRunning = False
	__NeedsUpdate = True

	__Thread = None

	__Window = None

	#region Menus
	__Menu = None
	__FileMenu = None
	__TreeviewPopupMenu = None
	#endregion
	#region Frames
	__StatsFrame = None
	__InspectorFrame = None
	__TreeviewFrame = None
	#endregion
	#region Widgets
	__EntitiesTree = None
	__RenderStatsLabel = None
	__InspectorLabel = None
	__RenderStatsWidget = None
	#endregion

	__MainFont = ("Helvetica", 9)

	def Initialize():
		if ImGui.__Initialized:
			return
		
		ImGui.__IsRunning = True
		ImGui.__Thread = threading.Thread(target = ImGui.__Run, name = "spyke.imgui")

		ImGui.__Initialized = True

		ImGui.__Thread.start()
		Debug.Log("Imgui started.", LogLevel.Info)
	
	def TryClose():
		if not ImGui.__IsRunning:
			return
			
		ImGui.__IsRunning = False
		ImGui.__Thread.join()
	
	#region Callbacks
	def __Close():
		if not ImGui.__Initialized:
			return

		ImGui.__IsRunning = False
		ImGui.__Initialized = False

		ImGui.__Window.quit()

		del ImGui.__Window
		gc.collect()

		Log("ImGui closed", LogLevel.Info)
	
	def __SaveScene():
		f = filedialog.asksaveasfilename(parent = ImGui.__Window, initialdir = "./", title = "Select file", filetypes = (("spyke scene files", "*.scn"), ("all files", "*.*")))
		if not f:
			return
		
		SaveScene(SceneManager.Current, f)

	def __OpenScene() -> None:
		f = filedialog.askopenfilename(parent = ImGui.__Window, initialdir = "./", title = "Select file", filetypes = (("spyke scene files", "*.scn"), ("all files", "*.*")))
		if not f:
			return
		
		LoadScene(f)

	def __AddEntity():
		win = DialogWindow(ImGui.__Window, "Create Enitity", "Entity name: ")
		win.AwaitWindow()

		SceneManager.Current.CreateEntity(TagComponent(win.value))

		ImGui.__NeedsUpdate = True
	
	def __PopTreeviewMenu(event):
		if ImGui.__EntitiesTree.identify("region", event.x, event.y) != "nothing":
			return
		
		try:
			ImGui.__TreeviewPopupMenu.tk_popup(event.x_root, event.y_root)
		finally:
			ImGui.__TreeviewPopupMenu.grab_release()
	#endregion
	
	def __Setup():
		ImGui.__Window = tk.Tk()
		ImGui.__Window.title("ImGui")
		ImGui.__Window.geometry("850x280")
		ImGui.__Window.protocol("WM_DELETE_WINDOW", ImGui.__Close)

		ImGui.__Menu = tk.Menu(ImGui.__Window)

		ImGui.__FileMenu = tk.Menu(ImGui.__Menu, tearoff = 0)
		ImGui.__FileMenu.add_command(label = "New Scene")
		ImGui.__FileMenu.add_command(label = "Open Scene...", command = ImGui.__OpenScene)
		ImGui.__FileMenu.add_command(label = "Save Scene...", command = ImGui.__SaveScene)
		ImGui.__FileMenu.add_separator()
		ImGui.__FileMenu.add_command(label = "Exit", command = ImGui.__Close)

		ImGui.__Menu.add_cascade(label = "File", menu = ImGui.__FileMenu)

		ImGui.__Window.config(menu = ImGui.__Menu)

		ImGui.__TreeviewPopupMenu = tk.Menu(ImGui.__Window, tearoff = 0)
		ImGui.__TreeviewPopupMenu.add_command(label = "AddEntity", command = ImGui.__AddEntity)

		ttk.Style().configure("Treeview", bd = 1, relief = "solid")

		ImGui.__EntitiesTree = ttk.Treeview(ImGui.__Window, show = "tree", style = "Treeview")

		ImGui.__StatsFrame = tk.Frame(ImGui.__Window, bd = 1, relief = "solid", bg = "white")
		ImGui.__InspectorFrame = tk.Frame(ImGui.__Window, bd = 1, relief = "solid", bg = "white")
		ImGui.__TreeviewFrame = tk.Frame(ImGui.__Window, bd = 1, relief = "solid", bg = "white")

		ImGui.__RenderStatsLabel = tk.Label(ImGui.__StatsFrame, text = "Render stats", bd = 0, bg = "white", font = (*ImGui.__MainFont, "bold"))
		ImGui.__RenderStatsWidget = StatsWidget(ImGui.__StatsFrame)
		ImGui.__RenderStatsLabel.grid(row = 0, column = 0, sticky = "we")
		ImGui.__RenderStatsWidget.grid(row = 1, column = 0, sticky = "nswe")
		ImGui.__StatsFrame.grid(row = 0, column = 0, sticky = "nswe")

		ImGui.__InspectorLabel = tk.Label(ImGui.__InspectorFrame, text = "Inspector", bd = 0, bg = "white")
	
	def __OnFrame():
		ImGui.__RenderStatsWidget.Update()
	
	def __Run():
		ImGui.__Setup()

		while ImGui.__IsRunning:
			try:
				ImGui.__OnFrame()
				ImGui.__Window.update()
			except tk.TclError:
				pass
			except Exception as e:
				Debug.Log(f"ImGui error: {e}.", LogLevel.Error)
		
		ImGui.__Close()