from .basicRenderer import BasicRenderer
from .textRenderer import TextRenderer
from .lineRenderer import LineRenderer
from ..shader import Shader
from ...text.font import Font
from ....enums import RendererTarget, UniformTarget
from ....debug import Log, LogLevel

import glm

class Renderer(object):
	def __init__(self, shader: Shader):
		self.__basicRenderer = BasicRenderer(shader)
		self.__textRenderer = None
		self.__lineRenderer = None

		self.__viewProjectionMatrix = glm.mat4(1.0)

	def AddComponent(self, componentType: RendererTarget, shader: Shader):
		if componentType == RendererTarget.BasicRenderer2D:
			self.__basicRenderer = BasicRenderer(shader)
		elif componentType == RendererTarget.TextRenderer:
			self.__textRenderer = TextRenderer(shader)
		elif componentType == RendererTarget.LineRenderer:
			self.__lineRenderer = LineRenderer(shader)
		else:
			raise RuntimeError(f"Invalid component type: {componentType}.")
	
	def BeginScene(self, viewProjection: glm.mat4):
		try:
			self.__basicRenderer.BeginScene(viewProjection, "uViewProjection")
			self.__textRenderer.BeginScene(viewProjection, "uViewProjection")
			self.__lineRenderer.BeginScene(viewProjection, "uViewProjection")
		except AttributeError:
			pass
	
		self.drawsCount = 0
	
	def EndScene(self):
		try:
			self.__basicRenderer.EndScene()
			self.__textRenderer.EndScene()
			self.__lineRenderer.EndScene()
		except AttributeError:
			pass
	
	def RenderQuad(self, item):
		try:
			self.__basicRenderer.Render(item)
		except AttributeError:
			pass
	
	def RenderLine(self, item):
		try:
			self.__lineRenderer.Render(item)
		except AttributeError:
			pass
	
	def RenderText(self, pos: tuple, color: tuple, font: Font, size: int, text: str):
		try:
			self.__textRenderer.DrawText(pos, color, font, size, text)
		except AttributeError:
			pass
	
	def Resize(self, width: int, height: int):
		try:
			self.__textRenderer.Resize(width, height)
		except AttributeError:
			pass
