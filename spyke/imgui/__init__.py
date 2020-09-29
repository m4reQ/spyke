from .inspectorWindow import InspectorWindow
from .entitiesWindow import EntitiesWindow
from .imguiWindow import ImguiWindow
from ..debug import Log, LogLevel
from ..ecs import Scene

class ImGui(object):
	def __init__(self, x, y, width, height):
		self.window = ImguiWindow(self, x, y, width, height)
		self.window.OnFrame = self.OnFrame
		self.window.Setup = self.Setup()
	
	def OnFrame(self):
		pass

	def Setup(self):
		self.window.Handle.title("Imgui")
		self.window.Handle.overrideredirect(True)
		self.window.Handle.geometry(f"{self.width}x{self.height}+{self.winX}+{self.winY}")

		titleBar = tkinter.Frame(self.Handle, bg = "#090a29", relief = "raised", bd = 2, highlightbackground = "#dadbe0")
		title = tkinter.Label(titleBar, text = self.Title ,bg = "#090a29", fg = "#edeef2")
		closeButton = tkinter.Button(titleBar, text = 'x', fg = "#edeef2", bg = "#090a29", bd = 0, command = self.OnClose)

		titleBar.pack(side = "top", fill = "x")
		title.pack(side = "left")
		closeButton.pack(side = "right")

		titleBar.bind("<B1-Motion>", self.Move)
		title.bind("<B1-Motion>", self.Move)

		self.Handle.configure(bg = "#090a29")


class __ImGui(object):
	BaseWidth = 300
	
	def __init__(self, width, height, posX, posY):
		self.inspector = InspectorWindow(width, height, posX, posY)
		self.entities = EntitiesWindow(width, height, posX + ImGui.BaseWidth, posY)

		self.isRunning = True
		
		self.__scene = None

	def OnUpdate(self):
		self.inspector.OnUpdate()
		self.entities.OnUpdate()

		self.isRunning = self.inspector.isRunning or self.entities.isRunning
	
	def Close(self):
		self.inspector.OnClose()
		self.entities.OnClose()

		Log("Imgui closed succesfully", LogLevel.Info)
	
	def SetScene(self, scene: Scene):
		self.entities.SetScene(scene)
		self.entities.Reorganize()
	
if __name__ == '__main__':
	g = ImGui(200, 200)
	g.Run()