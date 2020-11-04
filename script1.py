from spyke.ecs.components import ColorComponent
from spyke.input import InputHandler, EventHandler, EventType, Keys
from spyke.utils import Delayer

def OnInit(self):
	self.name = "Test"
	self.delayer = Delayer(2.0)

def OnProcess(self, *args, **kwargs):
	if self.delayer.IsWaiting():
		return
		
	if InputHandler.IsKeyPressed(Keys.KeyA.Glfw):
		color = self.GetComponent(ColorComponent)
		print(f"{self.name}'s alpha: {color.A}")