from spyke.imgui.widgets.contextInfo import ContextInfoWidget
from .widgets import *
from .dialogWindow import DialogWindow
from ..debugging import Debug, LogLevel
from ..ecs.components import *
from ..constants import DEFAULT_IMGUI_BG_COLOR, _MAIN_PROCESS
from ..graphics import Renderer
from .. import ResourceManager

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import gc

#This is just a large weight which forces other widgets with
#weight 1 to be practically not resizable. Add this to widgets
#that should be able to resize as grid_configure "weight" parameter.
DONT_RESIZE_OTHERS = 450

DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 280

DEFAULT_COLUMN_WEIGHT = 1
DEFAULT_ROW_WEIGHT = 1

_isInitialized = False
_isRunning = False

_window: tk.Tk = None

_menu: tk.Menu = None
_fileMenu: tk.Menu = None
_treeviewMenu: tk.Menu = None

_entitiesTree: ttk.Treeview = None

_infoFrame: tk.Frame = None
_inspectorFrame: tk.Frame = None
_treeviewFrame: tk.Frame = None

_renderStatsWidget: RenderStatsWidget = None
_contextInfoWidget: ContextInfoWidget = None

def _OnFrame() -> None:
	if not _isRunning:
		return

	_renderStatsWidget.Update(Renderer.renderStats.drawsCount, Renderer.renderStats.vertexCount, Renderer.renderStats.drawTime, \
		_MAIN_PROCESS.memory_full_info().uss, Renderer.renderStats.videoMemoryUsed, (Renderer.screenStats.width, Renderer.screenStats.height), \
		Renderer.screenStats.vsync, Renderer.screenStats.refreshRate)
	_window.update()

def Initialize() -> None:
	global _isRunning, _isInitialized
	
	if _isInitialized:
		Debug.Log("Imgui already initialized.", LogLevel.Warning)
		return

	_Setup()
	_isRunning = True
	_isInitialized = True

	Debug.Log("Imgui initialized.", LogLevel.Info)

def Close() -> None:
	global _isRunning, _isInitialized, _window

	if not _isInitialized:
		return

	_isRunning = False
	_isInitialized = False

	_window.destroy()
	del _window

	Debug.Log("ImGui closed", LogLevel.Info)

def _Setup() -> None:
	global _window, _menu, _fileMenu, _treeviewMenu, _entitiesTree, _inspectorFrame, \
		_treeviewFrame, _renderStatsWidget, _inspectorLabel, _infoFrame, _contextInfoWidget

	_window = tk.Tk()
	_window.title("ImGui")
	# _window.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
	_window.protocol("WM_DELETE_WINDOW", Close)
	_window.config(bg = DEFAULT_IMGUI_BG_COLOR)

	_window.columnconfigure(0, weight = DEFAULT_COLUMN_WEIGHT)
	_window.columnconfigure(1, weight = DEFAULT_COLUMN_WEIGHT)
	_window.columnconfigure(2, weight = DEFAULT_COLUMN_WEIGHT)
	_window.rowconfigure(0, weight = DEFAULT_ROW_WEIGHT)

	_menu = tk.Menu(_window)

	_fileMenu = tk.Menu(_menu, tearoff = 0)
	_fileMenu.add_command(label = "New Scene")
	_fileMenu.add_command(label = "Open Scene...", command = _OpenScene)
	_fileMenu.add_command(label = "Save Scene...", command = _SaveScene)
	_fileMenu.add_separator()
	_fileMenu.add_command(label = "Exit", command = Close)

	_menu.add_cascade(label = "File", menu = _fileMenu)
	_window.config(menu = _menu)

	_treeviewMenu = tk.Menu(_window, tearoff = 0)
	_treeviewMenu.add_command(label = "AddEntity", command = _AddEntity)

	ttk.Style().configure("Treeview", bd = 1, relief = "solid")

	_entitiesTree = ttk.Treeview(_window, show = "tree", style = "Treeview")
	_entitiesTree.bind("<Button-3>", _PopTreeviewMenu)

	_infoFrame = tk.Frame(_window, bd = 1, relief = "solid", bg = DEFAULT_IMGUI_BG_COLOR)
	_inspectorFrame = tk.Frame(_window, bd = 1, relief = "solid", bg = DEFAULT_IMGUI_BG_COLOR)
	_treeviewFrame = tk.Frame(_window, bd = 1, relief = "solid", bg = DEFAULT_IMGUI_BG_COLOR)

	_renderStatsWidget = RenderStatsWidget(_infoFrame)
	_contextInfoWidget = ContextInfoWidget(_infoFrame, Renderer.contextInfo.renderer, Renderer.contextInfo.version, Renderer.contextInfo.glslVersion, Renderer.contextInfo.vendor, Renderer.contextInfo.memoryAvailable)
	
	_infoFrame.rowconfigure(0, weight = DEFAULT_ROW_WEIGHT)
	_infoFrame.rowconfigure(1, weight = DEFAULT_ROW_WEIGHT)

	_renderStatsWidget.grid(row = 0, column = 0, sticky = "news")
	_contextInfoWidget.grid(row = 1, column = 0, sticky = "news")

	_infoFrame.grid(row = 0, column = 0, sticky = "wn")

	_inspectorLabel = tk.Label(_inspectorFrame, text = "Inspector", bd = 0, bg = DEFAULT_IMGUI_BG_COLOR)

def _OpenScene() -> None:
	f = filedialog.askopenfilename(parent = _window, initialdir = "./", title = "Select file", filetypes = (("spyke scene files", "*.scn"), ("all files", "*.*")))
	if not f:
		return
		
	ResourceManager.LoadScene(f)

def _SaveScene() -> None:
	f = filedialog.asksaveasfilename(parent = _window, initialdir = "./", title = "Select file", filetypes = (("spyke scene files", "*.scn"), ("all files", "*.*")))
	if not f:
		return
	
	if not f.endswith(".scn"):
		f += ".scn"
		
	ResourceManager.SaveScene(f, ResourceManager.GetCurrentScene())

def _AddEntity() -> None:
	win = DialogWindow(_window, "Create Enitity", "Entity name: ")
	win.AwaitWindow()

	ResourceManager.GetCurrentScene().CreateEntity(TagComponent(win.returnValue))

def _PopTreeviewMenu(event: tk.Event) -> None:
	if _entitiesTree.identify("region", event.x, event.y) != "nothing":
		return
		
	try:
		_treeviewMenu.tk_popup(event.x_root, event.y_root)
	finally:
		_treeviewMenu.grab_release()