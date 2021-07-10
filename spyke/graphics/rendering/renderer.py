from spyke.utils.functional import Iterator
from .basicRenderer import BasicRenderer
from .postRenderer import PostRenderer
from .particleRenderer import ParticleRenderer
from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..buffers import *
from ..screenInfo import ScreenInfo
from ..contextInfo import ContextInfo
from ...constants import _C_FLOAT_P, _GL_FLOAT_SIZE, _NP_FLOAT
from ...enums import Hint, Vendor, Keys
from ...ecs import components
from ...debugging import Debug, LogLevel
from ...input import EventHook, EventHandler
from ... import resourceManager as ResourceManager

from OpenGL import GL
from PIL import Image
import glm
import time
import numpy as np
import os

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
UNIFORM_BLOCK_INDEX = 0

DEFAULT_RENDER_COLOR_ATTACHMENT = 0

SCREENSHOT_DIRECTORY = "screenshots"

######################################################
# RESTORE PARTICLE RENDERER (REFACTORIZE IT)

class _Renderer(object):
	def __init__(self):
		self.basicRenderer: BasicRenderer = None
		self.particleRenderer: ParticleRenderer = None
		self.postRenderer: PostRenderer = None

		self.ubo: UniformBuffer = None
		self.framebuffer: Framebuffer = None

		self._isInitialized = False

		self._polygonModeIter = Iterator([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

	def Initialize(self, initialWidth: int, initialHeight: int, samples: int) -> None:
		if self._isInitialized:
			Debug.Log("Master renderer already initialized.", LogLevel.Warning)
			return

		self.basicRenderer = BasicRenderer()
		self.postRenderer = PostRenderer()

		self.ubo = UniformBuffer(UNIFORM_BLOCK_SIZE)

		fbSpec = FramebufferSpec(initialWidth, initialHeight)
		fbSpec.color = glm.vec4(1.0)
		fbSpec.samples = samples

		colorAttachmentSpec = FramebufferAttachmentSpec(FramebufferTextureFormat.Rgba)
		
		depthAttachmentSpec = FramebufferAttachmentSpec(FramebufferTextureFormat.Depth24Stencil8)
		depthAttachmentSpec.minFilter = GL.GL_NEAREST
		depthAttachmentSpec.magFilter = GL.GL_NEAREST

		fbSpec.attachmentSpecs = [
			colorAttachmentSpec,
			depthAttachmentSpec
		]

		self.framebuffer = Framebuffer(fbSpec)

		self.basicRenderer.shader.SetUniformBlockBinding("uMatrices", UNIFORM_BLOCK_INDEX)
		self.ubo.BindToUniform(UNIFORM_BLOCK_INDEX)

		if not os.path.exists(SCREENSHOT_DIRECTORY):
			os.mkdir(SCREENSHOT_DIRECTORY)

		if RendererSettings.MultisamplingEnabled:
			GL.glEnable(GL.GL_MULTISAMPLE)

			if ContextInfo.Vendor == Vendor.Nvidia:
				GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_NICEST)
		
		GL.glHint(GL.GL_TEXTURE_COMPRESSION_HINT, GL.GL_NICEST)
		
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glDepthFunc(GL.GL_LEQUAL)
			
		GL.glCullFace(GL.GL_FRONT)
		GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

		GL.glPointSize(4.0)

		GL.glEnable(GL.GL_LINE_SMOOTH)

		GL.glClearColor(0.0, 0.0, 0.0, 1.0)

		GL.glScissor(0, 0, initialWidth, initialHeight)
		GL.glViewport(0, 0, initialWidth, initialHeight)

		EventHandler.WindowResize += EventHook(self.__ResizeCallback, -1)
		EventHandler.WindowResize += EventHook(self.framebuffer.Resize, -1)
		EventHandler.KeyDown += EventHook(self.__KeyDownCallback, -1)

		self._isInitialized = True

		self._currentFillMode = GL.GL_FILL

		Debug.GetGLError()
		Debug.Log("Master renderer fully initialized.", LogLevel.Info)

	def ClearScreen(self) -> None:
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

	def RenderScene(self, scene, viewProjectionMatrix: glm.mat4) -> None:
		RenderStats.Clear()

		data = list(viewProjectionMatrix[0]) + list(viewProjectionMatrix[1]) + list(viewProjectionMatrix[2]) + list(viewProjectionMatrix[3])
		self.ubo.AddData(data, len(data) * _GL_FLOAT_SIZE)

		self.ubo.Bind()

		self.framebuffer.Bind()
		
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

		drawables = [x[1] for x in scene.GetComponents(components.SpriteComponent, components.TransformComponent)]
		opaque = [x for x in drawables if x[0].color.w == 1.0]
		alpha = [x for x in drawables if x not in opaque]

		alpha.sort(key = lambda x: x[0].color.w, reverse = True)

		for (sprite, transform) in opaque:
			self.basicRenderer.RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tilingFactor)
		self.basicRenderer.EndScene()

		GL.glDisable(GL.GL_DEPTH_TEST)
		for (sprite, transform) in alpha:
			self.basicRenderer.RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tilingFactor)
	
		transformNp = np.zeros((4, 4), dtype=_NP_FLOAT)
		transformNp[3, 3] = 1.0
		
		for _, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
			font = ResourceManager.GetFont(text.font)

			advSum = 0.0

			for char in text.text:
				glyph = font.GetGlyph(ord(char))

				adv = advSum / ScreenInfo.width * (text.size / font.baseSize)

				scWidth = glyph.width / ScreenInfo.width * (text.size / font.baseSize)
				scHeight = glyph.height / ScreenInfo.height * (text.size / font.baseSize)

				advSum += glyph.advance

				transformNp[3, 0] = transform.position.x + adv
				transformNp[3, 1] = transform.position.y
				transformNp[3, 2] = transform.position.z
				transformNp[0, 0] = scWidth
				transformNp[1, 1] = scHeight

				self.basicRenderer.RenderQuad(glm.make_mat4x4(transformNp.ctypes.data_as(_C_FLOAT_P)), text.color, font.texture, glm.vec2(1.0, 1.0), glyph.texRect)
			
		self.basicRenderer.EndScene()
		
		# for _, system in scene.GetComponent(components.ParticleSystemComponent):
		# 	for particle in system.particlePool:
		# 		if particle.isAlive:
		# 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

		# Renderer.__ParticleRenderer.EndScene()

		self.framebuffer.Unbind()

		GL.glClear(GL.GL_COLOR_BUFFER_BIT)
		GL.glViewport(0, 0, ScreenInfo.width, ScreenInfo.height)
		GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

		self.postRenderer.RenderFullscreen(self.framebuffer, self.framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT))
		
		GL.glPolygonMode(GL.GL_FRONT_AND_BACK, self._currentFillMode)
		GL.glEnable(GL.GL_DEPTH_TEST)
		
		RenderStats.FrameEnded = True
	
	def __KeyDownCallback(self, key: int, _, repeated: bool) -> bool:
		if repeated:
			return False

		if key == Keys.KeyGrave:
			fillMode = next(self._polygonModeIter)
			
			if fillMode == GL.GL_FILL:
				Debug.Log("Renderer drawing mode set to: FILL", LogLevel.Info)
			elif fillMode == GL.GL_LINE:
				Debug.Log("Renderer drawing mode set to: WIREFRAME", LogLevel.Info)
			elif fillMode == GL.GL_POINT:
				Debug.Log("Renderer drawing mode set to: POINTS", LogLevel.Info)
			
			fillMode = self._currentFillMode
		elif key == Keys.KeyF1:
			self.CaptureFrame()

		return False

	def __ResizeCallback(self, width: int, height: int) -> bool:
		GL.glScissor(0, 0, width, height)
		GL.glViewport(0, 0, width, height)

		self.framebuffer.Resize(width, height)

		return False
	
	def SetClearColor(r: float, g: float, b: float, a: float):
		GL.glClearColor(r, g, b, a)
	
	def CaptureFrame():
		pixels = GL.glReadPixels(0, 0, ScreenInfo.width, ScreenInfo.height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)
		
		img = Image.frombytes("RGB", (ScreenInfo.width, ScreenInfo.height), pixels)
		img = img.transpose(Image.FLIP_TOP_BOTTOM)

		filename = os.path.join(SCREENSHOT_DIRECTORY, "screenshot_" + str(int(time.time()))) + ".jpg"
		img.save(filename, "JPEG")
		Debug.Log(f"Screenshot was saved as '{filename}'.", LogLevel.Info)
	
Renderer = _Renderer()