from spyke.ecs.components import ColorComponent, TextComponent
from spyke.input import InputHandler, EventHandler
from spyke.utils import Delayer

def OnInit(self):
	self.name = "Test"
	self.delayer = Delayer(2.0)

def OnProcess(self, *args, **kwargs):
	textComp = self.GetComponent(TextComponent)
	colorComp = self.GetComponent(ColorComponent)
	fps = 1.0 / self.world.GetFrameTime()

	textComp.Text = f"FPS: {fps:.2f}"

	if fps < 60:
		colorComp.R = 1.0
		colorComp.G = 0.0
		colorComp.B = 0.0
	elif fps < 240:
		colorComp.R = 1.0
		colorComp.G = 1.0
		colorComp.B = 0.0
	else:
		colorComp.R = 1.0
		colorComp.G = 1.0
		colorComp.B = 1.0