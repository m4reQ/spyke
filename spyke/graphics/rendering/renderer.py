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
from ...transform import Vector3, Matrix4, Vector2, Vector4
from ... import USE_FAST_NV_MULTISAMPLE, IS_NVIDIA
from ...utils import Static

from OpenGL import GL
#endregion

class Renderer(Static):
	__Renderers = {
		"basic": None,
		"text": None,
		"line": None,
		"part": None,
		"post": None}
	
	__RenderTarget = None

	VertexCount = 0
	DrawsCount = 0

	def Initialize(multisample: bool) -> None:
		Renderer.__Renderers["basic"] = BasicRenderer()
		Renderer.__Renderers["text"] = TextRenderer()
		Renderer.__Renderers["line"] = LineRenderer()
		Renderer.__Renderers["part"] = ParticleRenderer()
		Renderer.__Renderers["post"] = PostRenderer()

		if multisample:
			GLCommand.Enable(EnableCap.MultiSample)
			if IS_NVIDIA:
				if USE_FAST_NV_MULTISAMPLE:
					GLCommand.Hint(Hint.MultisampleFilterNvHint, HintMode.Fastest)
				else:
					GLCommand.Hint(Hint.MultisampleFilterNvHint, HintMode.Nicest)
		
		GL.glCullFace(GL.GL_FRONT)
		GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)

	def BeginScene(renderTarget: RenderTarget) -> None:
		Renderer.__RenderTarget = renderTarget

		for renderer in Renderer.__Renderers.values():
			renderer.BeginScene(renderTarget.Camera.viewProjectionMatrix)
	
	def EndScene() -> None:
		Renderer.DrawsCount = 0
		Renderer.VertexCount = 0

		if Renderer.__RenderTarget:
			Renderer.__RenderTarget.ContainsPass = False

			if Renderer.__RenderTarget.HasFramebuffer:
				Renderer.__RenderTarget.Framebuffer.Bind()
				Renderer.__RenderTarget.ContainsPass = True

		for renderer in Renderer.__Renderers.values():
			renderer.EndScene()
			stats = renderer.GetStats()
			Renderer.DrawsCount += stats.DrawsCount
			Renderer.VertexCount += stats.VertexCount
		
		if Renderer.__RenderTarget:
			if Renderer.__RenderTarget.HasFramebuffer:
				Renderer.__RenderTarget.Framebuffer.Unbind()
	
	def RenderQuad(transform: Matrix4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple) -> None:
		Renderer.__Renderers["basic"].RenderQuad(transform, color, texHandle, tilingFactor)
	
	def RenderLine(startPos: Vector3, endPos: Vector3, color: tuple) -> None:
		Renderer.__Renderers["line"].Render(startPos, endPos, color)
	
	def RenderText(pos: Vector3, color: tuple, font: Font, size: int, text: str) -> None:
		Renderer.__Renderers["text"].DrawText(pos, color, font, size, text)
	
	def RenderParticle(pos: Vector2, size: Vector2, rot: float, color: tuple, texHandle: TextureHandle) -> None:
		Renderer.__Renderers["part"].RenderParticle(pos, size, rot, color, texHandle)
	
	def PostRender(transform: Matrix4, renderTarget: RenderTarget, color: Vector4) -> None:
		Renderer.__Renderers["post"].Render(transform, renderTarget, color)
	
	def Resize(width: int, height: int) -> None:
		Renderer.__Renderers["text"].Resize(width, height)
