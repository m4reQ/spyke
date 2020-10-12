from .basicRenderer import BasicRenderer
from .textRenderer import TextRenderer
from .lineRenderer import LineRenderer
from ..texturing.textureUtils import TextureHandle
from ..shader import Shader
from ..text.font import Font
from ...enums import RendererTarget, UniformTarget
from ...debug import Log, LogLevel

import glm

class Renderer(object):
	def __init__(self, shader: Shader):
		self.__basicRenderer = BasicRenderer(shader)
		self.__textRenderer = None
		self.__lineRenderer = None

		self.__viewProjectionMatrix = glm.mat4(1.0)

		self.drawsCount = 0
		self.vertexCount = 0

	def AddComponent(self, componentType: RendererTarget, shader: Shader) -> None:
		if componentType == RendererTarget.BasicRenderer2D:
			self.__basicRenderer = BasicRenderer(shader)
		elif componentType == RendererTarget.TextRenderer:
			self.__textRenderer = TextRenderer(shader)
		elif componentType == RendererTarget.LineRenderer:
			self.__lineRenderer = LineRenderer(shader)
		else:
			raise RuntimeError(f"Invalid component type: {componentType}.")
	
	def BeginScene(self, viewProjection: glm.mat4) -> None:
		try:
			self.__basicRenderer.BeginScene(viewProjection, "uViewProjection")
			self.__textRenderer.BeginScene(viewProjection, "uViewProjection")
			self.__lineRenderer.BeginScene(viewProjection, "uViewProjection")
		except AttributeError:
			pass
	
	def EndScene(self) -> None:
		self.drawsCount = 0
		self.vertexCount = 0

		try:
			stats = self.__basicRenderer.GetStats()
			self.drawsCount += stats.DrawsCount
			self.vertexCount += stats.VertexCount

			stats = self.__textRenderer.GetStats()
			self.drawsCount += stats.DrawsCount
			self.vertexCount += stats.VertexCount

			stats = self.__lineRenderer.GetStats()
			self.drawsCount += stats.DrawsCount
			self.vertexCount += stats.VertexCount
		except AttributeError:
			pass
	
	def RenderQuad(self, transform: glm.mat4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple) -> None:
		try:
			self.__basicRenderer.RenderQuad(transform, color, texHandle, tilingFactor)
		except AttributeError:
			pass
	
	def RenderLine(self, startPos: glm.vec2, endPos: glm.vec2, color: tuple) -> None:
		try:
			self.__lineRenderer.Render(item) ############################CHUUUUJJJJJ
		except AttributeError:
			pass
	
	def RenderText(self, pos: tuple, color: tuple, font: Font, size: int, text: str) -> None:
		try:
			self.__textRenderer.DrawText(pos, color, font, size, text)
		except AttributeError:
			pass
	
	def Resize(self, width: int, height: int) -> None:
		try:
			self.__textRenderer.Resize(width, height)
		except AttributeError:
			pass
