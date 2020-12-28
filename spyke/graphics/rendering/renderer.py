#region Import
from .basicRenderer import BasicRenderer
from .textRenderer import TextRenderer
from .lineRenderer import LineRenderer
from .postRenderer import PostRenderer
from .particleRenderer import ParticleRenderer
from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..buffers import Framebuffer, UniformBuffer
from ... import USE_FAST_NV_MULTISAMPLE, IS_NVIDIA
from ...enums import Hint
from ...utils import Static, Mat4ToTuple, GL_FLOAT_SIZE
from ...ecs import components

from OpenGL import GL
import glm
import time
#endregion

UNIFORM_BLOCK_SIZE = 16 * GL_FLOAT_SIZE
UNIFORM_BLOCK_INDEX = 0

class Renderer(Static):
	__BasicRenderer = None
	__TextRenderer = None
	__LineRenderer = None
	__ParticleRenderer = None
	__PostRenderer = None

	__ubo = None

	def Initialize() -> None:
		Renderer.__BasicRenderer = BasicRenderer()
		Renderer.__TextRenderer = TextRenderer()
		Renderer.__LineRenderer = LineRenderer()
		Renderer.__ParticleRenderer = ParticleRenderer()
		Renderer.__PostRenderer = PostRenderer()
		
		Renderer.__ubo = UniformBuffer(UNIFORM_BLOCK_SIZE)

		Renderer.__BasicRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__TextRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__LineRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__ParticleRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__PostRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)

		Renderer.__ubo.BindToUniform(UNIFORM_BLOCK_INDEX)

		if RendererSettings.MultisamplingEnabled:
			GL.glEnable(GL.GL_MULTISAMPLE)
			if IS_NVIDIA:
				if USE_FAST_NV_MULTISAMPLE:
					GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_FASTEST)
				else:
					GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_NICEST)
		
		if RendererSettings.BlendingEnabled:
			GL.glEnable(GL.GL_BLEND)
			GL.glBlendFunc(*RendererSettings.BlendingFunc)
		
		GL.glCullFace(GL.GL_FRONT)
		GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
	
	def RenderFramebuffer(pos: glm.vec3, size: glm.vec3, rotation: glm.vec3, framebuffer: Framebuffer):
		Renderer.__PostRenderer.Render(pos, size, rotation, framebuffer)

	def RenderScene(scene, viewProjectionMatrix: glm.mat4, framebuffer: Framebuffer = None) -> None:
		RenderStats.Clear()
		start = time.perf_counter()

		Renderer.__ubo.Bind()

		data = Mat4ToTuple(viewProjectionMatrix)
		Renderer.__ubo.AddData(data, len(data) * GL_FLOAT_SIZE)

		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		
		try:
			framebuffer.Bind()
			GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		except AttributeError:
			pass

		for _, (sprite, transform) in scene.GetComponents(components.SpriteComponent, components.TransformComponent):
			Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.TextureHandle, sprite.TilingFactor)
		
		for _, line in scene.GetComponent(components.LineComponent):
			Renderer.__LineRenderer.RenderLine(line.StartPos, line.EndPos, line.Color)
		
		for _, system in scene.GetComponent(components.ParticleSystemComponent):
			for particle in system.particlePool:
				if not particle.isAlive:
					continue

				Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)
		
		for _, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
			Renderer.__TextRenderer.RenderText(transform.Position, text.Color, text.Font, text.Size, text.Text)

		Renderer.__BasicRenderer.EndScene()
		Renderer.__TextRenderer.EndScene()
		Renderer.__LineRenderer.EndScene()
		Renderer.__ParticleRenderer.EndScene()

		try:
			framebuffer.Unbind()
		except AttributeError:
			pass

		RenderStats.DrawTime = time.perf_counter() - start
	
	def Resize(width: int, height: int) -> None:
		GL.glScissor(0, 0, width, height)
		GL.glViewport(0, 0, width, height)

		Renderer.__TextRenderer.Resize(width, height)