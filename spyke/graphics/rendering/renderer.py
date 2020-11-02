#region Import
from .basicRenderer import BasicRenderer
from .textRenderer import TextRenderer
from .lineRenderer import LineRenderer
from .postRenderer import PostRenderer
from .particleRenderer import ParticleRenderer
from .renderTarget import RenderTarget
from ..buffers import Framebuffer
from ..texturing.textureUtils import TextureHandle
from ..shader import Shader
from ..text.font import Font
from ..glCommands import GLCommand
from ...enums import UniformTarget, EnableCap, Hint, HintMode
from ...debug import Log, LogLevel
from ...transform import Vector3, Matrix4, Vector2
from ... import USE_FAST_NV_MULTISAMPLE, IS_NVIDIA
#endregion

class Renderer(object):
	def __init__(self):
		self.__renderers = {
			"basic": BasicRenderer(),
			"text": None,
			"line": None,
			"part": None,
			"post": None}

		self.__renderTarget = None
		self.__clearFramebuffers = False

		self.drawsCount = 0
		self.vertexCount = 0

		GLCommand.Enable(EnableCap.MultiSample)
		if IS_NVIDIA:
			if USE_FAST_NV_MULTISAMPLE:
				GLCommand.Hint(Hint.MultisampleFilterNvHint, HintMode.Fastest)
			else:
				GLCommand.Hint(Hint.MultisampleFilterNvHint, HintMode.Nicest)

	def AddComponent(self, component) -> None:
		if isinstance(component, BasicRenderer):
			self.__renderers["basic"] = component
		elif isinstance(component, TextRenderer):
			self.__renderers["text"] = component
		elif isinstance(component, LineRenderer):
			self.__renderers["line"] = component
		elif isinstance(component, ParticleRenderer):
			self.__renderers["part"] = component
		elif isinstance(component, PostRenderer):
			self.__renderers["post"] = component
		else:
			raise RuntimeError(f"Invalid component type: {type(component).__name__}.")
	
	def BeginScene(self, renderTarget: RenderTarget) -> None:
		if renderTarget.HasFramebuffer:
			renderTarget.Framebuffer.Bind()
			self.__clearFramebuffers = True

		for renderer in self.__renderers.values():
			try:
				renderer.BeginScene(renderTarget.Camera.viewProjectionMatrix)
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
	
	def RenderQuad(self, transform: Matrix4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple) -> None:
		self.__renderers["basic"].RenderQuad(transform, color, texHandle, tilingFactor)
	
	def RenderLine(self, startPos: Vector3, endPos: Vector3, color: tuple) -> None:
		try:
			self.__renderers["line"].Render(startPos, endPos, color)
		except (AttributeError, KeyError):
			pass
	
	def RenderText(self, pos: Vector3, color: tuple, font: Font, size: int, text: str) -> None:
		try:
			self.__renderers["text"].DrawText(pos, color, font, size, text)
		except (AttributeError, KeyError):
			pass
	
	def RenderParticle(self, pos: Vector2, size: Vector2, rot: float, color: tuple, texHandle: TextureHandle) -> None:
		try:
			self.__renderers["part"].RenderParticle(pos, size, rot, color, texHandle)
		except (AttributeError, KeyError):
			pass
	
	def RenderFramebuffer(self, transform: Matrix4, framebuffer: Framebuffer, viewProjectionMatrix: Matrix4) -> None:
		try:
			self.__renderers["post"].RenderFramebuffer(transform, framebuffer, viewProjectionMatrix)
		except (AttributeError, KeyError):
			pass
	
	def Resize(self, width: int, height: int) -> None:
		try:
			self.__renderers["text"].Resize(width, height)
		except (AttributeError, KeyError):
			pass
