from .inspectorWindow import InspectorWindow
from .entitiesWindow import EntitiesWindow
from ..debug import Log, LogLevel

class ImGui(object):
	BaseWidth = 300
	
	def __init__(self, width, height, posX, posY):
		self.inspector = InspectorWindow(width, height, posX, posY)
		self.entities = EntitiesWindow(width, height, posX + ImGui.BaseWidth, posY)

		self.isRunning = True

	def OnUpdate(self):
		self.inspector.OnUpdate()
		self.entities.OnUpdate()

		self.isRunning = self.inspector.isRunning or self.entities.isRunning
	
	def Close(self):
		self.inspector.OnClose()
		self.entities.OnClose()

		Log("Imgui closed succesfully", LogLevel.Info)
	
if __name__ == '__main__':
	g = ImGui(200, 200)
	g.Run()