from .basicRenderer import BasicRenderer
from .textRenderer import TextRenderer
from .lineRenderer import LineRenderer
from .renderTarget import RenderTarget
from ..buffers import Framebuffer
from ..texturing.textureUtils import TextureHandle
from ..shader import Shader
from ..text.font import Font
from ...enums import RendererTarget, UniformTarget
from ...debug import Log, LogLevel

import glm

class Renderer(object):
	def __init__(self, shader: Shader):
		self.__renderers = {
			"basic": BasicRenderer(shader),
			"text": None,
			"line": None,
			"post": None}

		self.__renderTarget = None
		self.__clearFramebuffers = False

		self.drawsCount = 0
		self.vertexCount = 0

	def AddComponent(self, componentType: RendererTarget, shader: Shader) -> None:
		if componentType == RendererTarget.BasicRenderer2D:
			self.__renderers["basic"] = BasicRenderer(shader)
		elif componentType == RendererTarget.TextRenderer:
			self.__renderers["text"] = TextRenderer(shader)
		elif componentType == RendererTarget.LineRenderer:
			self.__renderers["line"] = LineRenderer(shader)
		else:
			raise RuntimeError(f"Invalid component type: {componentType}.")
	
	def BeginScene(self, renderTarget: RenderTarget) -> None:
		if renderTarget.HasFramebuffer:
			renderTarget.Framebuffer.Bind()
			self.__clearFramebuffers = True

		for renderer in self.__renderers.values():
			try:
				renderer.BeginScene(renderTarget.Camera.viewProjectionMatrix, "uViewProjection")
			except AttributeError:
				pass
	
	def EndScene(self) -> None:
		self.drawsCount = 0
		self.vertexCount = 0

		for renderer in self.__renderers.values():
			try:
				renderer.EndScene()
				stats = renderer.GetStats()
				self.drawsCount += stats.DrawsCount
				self.vertexCount += stats.VertexCount
			except AttributeError:
				pass
		
		if self.__clearFramebuffers:
			Framebuffer.UnbindAll()
			self.__clearFramebuffers = False
	
	def RenderQuad(self, transform: glm.mat4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple) -> None:
		self.__renderers["basic"].RenderQuad(transform, color, texHandle, tilingFactor)
	
	def RenderLine(self, startPos: glm.vec3, endPos: glm.vec3, color: tuple) -> None:
		try:
			self.__renderers["line"].Render(startPos, endPos, color)
		except AttributeError:
			pass
	
	def RenderText(self, pos: tuple, color: tuple, font: Font, size: int, text: str) -> None:
		try:
			self.__renderers["text"].DrawText(pos, color, font, size, text)
		except AttributeError:
			pass
	
	def Resize(self, width: int, height: int) -> None:
		try:
			self.__renderers["text"].Resize(width, height)
		except AttributeError:
			pass
