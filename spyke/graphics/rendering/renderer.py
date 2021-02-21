#region Import
from .basicRenderer import BasicRenderer
from ...input import EventHook, EventHandler, EventType
from .textRenderer import TextRenderer
from .postRenderer import PostRenderer
from .particleRenderer import ParticleRenderer
from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..buffers import Framebuffer, UniformBuffer, FramebufferSpec, FramebufferAttachmentSpec, FramebufferTextureFormat
from ..contextInfo import ContextInfo
from ...constants import USE_FAST_NV_MULTISAMPLE, _GL_FLOAT_SIZE
from ...enums import Hint, Vendor, Keys
from ...utils import Static
from ...ecs import components
from ...debugging import Log, LogLevel

from OpenGL import GL
import glm
import time
#endregion

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
UNIFORM_BLOCK_INDEX = 0

######################################################
# RESTORE PARTICLE RENDERER (REFACTORIZE IT)

class Renderer(Static):
	__BasicRenderer = None
	__TextRenderer = None
	__ParticleRenderer = None
	__PostRenderer = None

	__Ubo = None

	__Framebuffer = None

	__Initialized = False

	ClearColor = (0.0, 0.0, 0.0, 0.0)

	def __DrawTypeGeneratorFn():
		while True:
			yield GL.GL_LINES
			yield GL.GL_POINTS
			yield GL.GL_TRIANGLES
	
	__DrawTypeGenerator = __DrawTypeGeneratorFn()

	def Initialize(initialWidth: int, initialHeight: int) -> None:
		if Renderer.__Initialized:
			Log("Renderer already initialized.", LogLevel.Warning)
			return

		Renderer.__BasicRenderer = BasicRenderer()
		Renderer.__TextRenderer = TextRenderer(initialWidth, initialHeight)
		# Renderer.__ParticleRenderer = ParticleRenderer()
		Renderer.__PostRenderer = PostRenderer()
		
		Renderer.__Ubo = UniformBuffer(UNIFORM_BLOCK_SIZE)

		fbSpec = FramebufferSpec(initialWidth, initialHeight)
		fbSpec.color = glm.vec4(1.0, 0.0, 1.0, 1.0)
		fbSpec.attachmentsSpecs = [
			FramebufferAttachmentSpec(FramebufferTextureFormat.Rgba8),
			FramebufferAttachmentSpec(FramebufferTextureFormat.Depth)]

		Renderer.__Framebuffer = Framebuffer(fbSpec)

		Renderer.__BasicRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__TextRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		# Renderer.__ParticleRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		Renderer.__PostRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)

		Renderer.__Ubo.BindToUniform(UNIFORM_BLOCK_INDEX)

		if RendererSettings.MultisamplingEnabled:
			GL.glEnable(GL.GL_MULTISAMPLE)

			if ContextInfo.Vendor == Vendor.Nvidia:
				if USE_FAST_NV_MULTISAMPLE:
					GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_FASTEST)
				else:
					GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_NICEST)
		
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glDepthFunc(GL.GL_LEQUAL)
		
		GL.glCullFace(GL.GL_FRONT)
		GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

		GL.glPointSize(3.0)

		lineWidth = 2.0
		lineRange = GL.glGetFloatv(GL.GL_LINE_WIDTH_RANGE)
		if lineWidth <= lineRange[1] and lineWidth >= lineRange[0]:
			GL.glLineWidth(lineWidth)

		GL.glClearColor(0.0, 0.0, 0.0, 1.0)

		GL.glScissor(0, 0, initialWidth, initialHeight)
		GL.glViewport(0, 0, initialWidth, initialHeight)

		EventHandler.BindHook(EventHook(Renderer.ResizeCallback, -1), EventType.WindowResize)
		EventHandler.BindHook(EventHook(Renderer.__TextRenderer.ResizeCallback, -1), EventType.WindowResize)
		EventHandler.BindHook(EventHook(Renderer.KeyDownCallback, -1), EventType.KeyDown)

		Renderer.__Initialized = True

		Log("Renderer fully initialized.", LogLevel.Info)

	def ClearScreen() -> None:
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

	def RenderScene(scene, viewProjectionMatrix: glm.mat4) -> None:
		RenderStats.Clear()
		start = time.perf_counter()

		Renderer.__Ubo.Bind()

		data = list(viewProjectionMatrix[0]) + list(viewProjectionMatrix[1]) + list(viewProjectionMatrix[2]) + list(viewProjectionMatrix[3])
		Renderer.__Ubo.AddData(data, len(data) * _GL_FLOAT_SIZE)

		#Renderer.__Framebuffer.Bind()
	
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

		drawables = [x[1] for x in scene.GetComponents(components.SpriteComponent, components.TransformComponent)]
		opaque = [x for x in drawables if x[0].Color.w == 1.0]
		alpha = [x for x in drawables if x not in opaque]

		alpha.sort(key = lambda x: x[0].Color.w, reverse = True)

		for (sprite, transform) in opaque:
			Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.Texture, sprite.TilingFactor)
		Renderer.__BasicRenderer.EndScene()

		GL.glDisable(GL.GL_DEPTH_TEST)
		for (sprite, transform) in alpha:
			Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.Texture, sprite.TilingFactor)
		Renderer.__BasicRenderer.EndScene()
		GL.glEnable(GL.GL_DEPTH_TEST)

		# for _, (sprite, transform) in scene.GetComponents(components.SpriteComponent, components.TransformComponent):
		# 	Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.Texture, sprite.TilingFactor)
		# Renderer.__BasicRenderer.EndScene()
		
		# for _, line in scene.GetComponent(components.LineComponent):
		# 	#REIMPLEMENT LINE RENDERER
		# 	continue
		# 	Renderer.__LineRenderer.RenderLine(line.StartPos, line.EndPos, line.Color)
		
		# for _, system in scene.GetComponent(components.ParticleSystemComponent):
		# 	for particle in system.particlePool:
		# 		if not particle.isAlive:
		# 			continue

		# 		Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)
		
		for _, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
			Renderer.__TextRenderer.RenderText(transform.Position, text.Color, text.Font, text.Size, text.Text)

		Renderer.__TextRenderer.EndScene()
		# Renderer.__ParticleRenderer.EndScene()

		#Renderer.__Framebuffer.Unbind()

		#GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		#Renderer.__PostRenderer.Render(glm.vec3(0.0, 0.0, 0.0), glm.vec3(1.0, 1.0, 0.0), glm.vec3(0.0), Renderer.__Framebuffer, passIdx=0)

		RenderStats.DrawTime = time.perf_counter() - start
		RenderStats.FrameEnded = True
	
	def KeyDownCallback(key: int, _, repeated: bool) -> bool:
		if key == Keys.KeyGrave:
			drawType = next(Renderer.__DrawTypeGenerator)
			
			Renderer.__BasicRenderer.drawType = drawType
			Renderer.__TextRenderer.drawType = drawType
			
			if drawType == GL.GL_TRIANGLES:
				Log("Renderer draw type set to: FILL", LogLevel.Info)
			elif drawType == GL.GL_LINES:
				Log("Renderer draw type set to: WIREFRAME", LogLevel.Info)
			elif drawType == GL.GL_POINTS:
				Log("Renderer draw type set to: POINTS", LogLevel.Info)

		return False

	def ResizeCallback(width: int, height: int) -> bool:
		GL.glScissor(0, 0, width, height)
		GL.glViewport(0, 0, width, height)

		#Renderer.__Framebuffer.Resize(width, height)

		return False
	
	def SetClearColor(r: float, g: float, b: float, a: float):
		GL.glClearColor(r, g, b, a)