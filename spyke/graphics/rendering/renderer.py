#region Import
from .basicRenderer import BasicRenderer
from .postRenderer import PostRenderer
from .particleRenderer import ParticleRenderer
from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..buffers import *
from ..screenInfo import ScreenInfo
from ..contextInfo import ContextInfo
from ...constants import USE_FAST_NV_MULTISAMPLE, _GL_FLOAT_SIZE
from ...enums import Hint, Vendor, Keys
from ...utils import Static
from ...ecs import components
from ...debugging import Debug, LogLevel
from ...input import EventHook, EventHandler, EventType

from OpenGL import GL
from PIL import Image
import glm
import time
import numpy as np
import os
import ctypes
#endregion

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
UNIFORM_BLOCK_INDEX = 0

######################################################
# RESTORE PARTICLE RENDERER (REFACTORIZE IT)

class Renderer(Static):
	__BasicRenderer: BasicRenderer = None
	__ParticleRenderer: ParticleRenderer = None
	__PostRenderer: PostRenderer = None

	__Ubo: UniformBuffer = None
	__Framebuffer: Framebuffer = None

	__Initialized = False

	def __PolygonModeGeneratorFn():
		while True:
			yield GL.GL_LINE
			yield GL.GL_POINT
			yield GL.GL_FILL
	
	__PolygonModeGenerator = __PolygonModeGeneratorFn()

	def Initialize(initialWidth: int, initialHeight: int) -> None:
		if Renderer.__Initialized:
			Debug.Log("Master renderer already initialized.", LogLevel.Warning)
			return
		
		if not os.path.exists(RendererSettings.ScreenCaptureDirectory):
			os.mkdir(RendererSettings.ScreenCaptureDirectory)

		Renderer.__BasicRenderer = BasicRenderer()
		# Renderer.__ParticleRenderer = ParticleRenderer()
		Renderer.__PostRenderer = PostRenderer()
		
		Renderer.__Ubo = UniformBuffer(UNIFORM_BLOCK_SIZE)

		fbSpec = FramebufferSpec(initialWidth, initialHeight)
		fbSpec.color = glm.vec4(1.0, 0.0, 1.0, 1.0)
		fbSpec.attachmentsSpecs = [
			FramebufferColorTexture(FramebufferTextureFormat.Rgba8),
			FramebufferDepthTexture(True)]

		Renderer.__Framebuffer = Framebuffer(fbSpec)

		Renderer.__BasicRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
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
		EventHandler.BindHook(EventHook(Renderer.KeyDownCallback, -1), EventType.KeyDown)

		Renderer.__Initialized = True

		Debug.GetGLError()
		Debug.Log("Master renderer fully initialized.", LogLevel.Info)

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
			Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.Texture, sprite.TilingFactor, None)
		Renderer.__BasicRenderer.EndScene()

		GL.glDisable(GL.GL_DEPTH_TEST)
		for (sprite, transform) in alpha:
			Renderer.__BasicRenderer.RenderQuad(transform.Matrix, sprite.Color, sprite.Texture, sprite.TilingFactor, None)
		
		for _, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
			transformNp = np.zeros((4, 4))
			transformNp[0, 0] = 1.0
			transformNp[1, 1] = 1.0
			transformNp[2, 2] = 1.0
			transformNp[3, 3] = 1.0

			advSum = 0.0

			for char in text.Text:
				glyph = text.Font.GetGlyph(ord(char))

				adv = advSum / ScreenInfo.Width * (text.Size / text.Font.baseSize)

				scWidth = glyph.width / ScreenInfo.Width * (text.Size / text.Font.baseSize)
				scHeight = glyph.height / ScreenInfo.Height * (text.Size / text.Font.baseSize)

				advSum += glyph.advance

				transformNp[3, 0] = transform.Position.x + adv
				transformNp[3, 1] = transform.Position.y
				transformNp[3, 2] = transform.Position.z
				transformNp[0, 0] = scWidth
				transformNp[1, 1] = scHeight

				Renderer.__BasicRenderer.RenderQuad(transformNp, text.Color, text.Font.texture, glm.vec2(1.0, 1.0), glyph.texRect)
			
		Renderer.__BasicRenderer.EndScene()
		GL.glEnable(GL.GL_DEPTH_TEST)

		# for _, system in scene.GetComponent(components.ParticleSystemComponent):
		# 	for particle in system.particlePool:
		# 		if particle.isAlive:
		# 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

		# Renderer.__TextRenderer.EndScene()
		# Renderer.__ParticleRenderer.EndScene()

		#Renderer.__Framebuffer.Unbind()

		#GL.glClear(GL.GL_COLOR_BUFFER_BIT)

		#Renderer.__PostRenderer.Render(glm.vec3(0.0, 0.0, 0.0), glm.vec3(1.0, 1.0, 0.0), glm.vec3(0.0), Renderer.__Framebuffer, passIdx=0)

		RenderStats.DrawTime = time.perf_counter() - start
		RenderStats.FrameEnded = True
	
	def KeyDownCallback(key: int, _, repeated: bool) -> bool:
		if repeated:
			return False

		if key == Keys.KeyGrave:
			mode = next(Renderer.__PolygonModeGenerator)

			GL.glPolygonMode(GL.GL_FRONT_AND_BACK, mode)
			
			if mode == GL.GL_FILL:
				Debug.Log("Renderer drawing mode set to: FILL", LogLevel.Info)
			elif mode == GL.GL_LINE:
				Debug.Log("Renderer drawing mode set to: WIREFRAME", LogLevel.Info)
			elif mode == GL.GL_POINT:
				Debug.Log("Renderer drawing mode set to: POINTS", LogLevel.Info)
		elif key == Keys.KeyF1:
			Renderer.CaptureFrame()

		return False

	def ResizeCallback(width: int, height: int) -> bool:
		GL.glScissor(0, 0, width, height)
		GL.glViewport(0, 0, width, height)

		Renderer.__Framebuffer.Resize(width, height)

		return False
	
	def SetClearColor(r: float, g: float, b: float, a: float):
		GL.glClearColor(r, g, b, a)
	
	def CaptureFrame():
		pixels = GL.glReadPixels(0, 0, ScreenInfo.Width, ScreenInfo.Height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)
		
		img = Image.frombytes("RGB", (ScreenInfo.Width, ScreenInfo.Height), pixels)
		img = img.transpose(Image.FLIP_TOP_BOTTOM)

		filename = os.path.join(RendererSettings.ScreenCaptureDirectory, "screenshot_" + str(int(time.time()))) + ".jpg"
		img.save(filename, "JPEG")