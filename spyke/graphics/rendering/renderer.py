from ..rectangle import RectangleF
from ..texturing import Texture
from ..vertexArray import VertexArray
from ...utils import Iterator
from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import *
from ..screenStats import ScreenStats
from ..contextInfo import ContextInfo
from ...constants import _C_FLOAT_P, _GL_FILL_MODE_NAMES_MAP, _GL_FLOAT_SIZE, _NP_FLOAT, _NP_UINT, _THREAD_SYNC
from ...enums import Hint, NvidiaIntegerName, Vendor, Keys
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

##############################################
# RESTORE PARTICLE RENDERER (REFACTORIZE IT) #
##############################################

SCREENSHOT_DIRECTORY = "screenshots/"
SHADER_SOURCES_DIRECTORY = "spyke/graphics/shaderSources/"

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
MATRICES_UNIFORM_BLOCK_INDEX = 0

DEFAULT_RENDER_COLOR_ATTACHMENT = 0

MAX_QUADS_COUNT = 400
VERTICES_PER_QUAD = 4
INDICES_PER_QUAD = 6

POS_VERTEX_VALUES_COUNT = 3

BASIC_INSTANCE_VERTEX_VALUES_COUNT = 4 + 2 + 1 + 16
BASIC_VERTEX_VERTEX_VALUES_COUNT = 2

POST_VERTEX_VERTEX_VALUES_COUNT = 3 + 2

POS_DATA_VERTEX_SIZE = POS_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

BASIC_INSTANCE_DATA_VERTEX_SIZE = BASIC_INSTANCE_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE
BASIC_VERTEX_DATA_VERTEX_SIZE = BASIC_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POST_VERTEX_DATA_VERTEX_SIZE = POST_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1
POST_DATA_BUFFER_BINDING = 0

MAX_TEXTURES_COUNT = 16
AVAILABLE_USER_TEXTURES_COUNT = 16 - 4

MULTISAMPLE_TEXTURE_SAMPLER = 0
NORMAL_TEXTURE_SAMPLER = 1
WHITE_TEXTURE_SAMPLER = 14
BUFFER_TEXTURE_SAMPLER = 15

_quadVertices = [
	0.0, 0.0, 0.0,
	0.0, 1.0, 0.0,
	1.0, 1.0, 0.0,
	1.0, 0.0, 0.0]
	
_postData = [
	0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 1.0, 0.0, 0.0, 1.0,
	1.0, 1.0, 0.0, 1.0, 1.0,
	1.0, 0.0, 0.0, 1.0, 0.0 
]

_vertexData = np.empty(BASIC_VERTEX_VERTEX_VALUES_COUNT * MAX_QUADS_COUNT * VERTICES_PER_QUAD, dtype=_NP_FLOAT)
_instanceData = np.empty(BASIC_INSTANCE_VERTEX_VALUES_COUNT * MAX_QUADS_COUNT, dtype=_NP_FLOAT)

_lastVertexPos = 0
_lastInstancePos = 0

_textures = [0] * AVAILABLE_USER_TEXTURES_COUNT
_lastTexture = 0

_quadsCount = 0

_isInitialized = False
_polygonModeIter = Iterator([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL], looping=True)
_currentFillMode = GL.GL_FILL

_basicShader: Shader = None
_postProcessShader: Shader = None
_posVbo: StaticVertexBuffer = None
_instanceDataVbo: VertexBuffer = None
_vertexDataTbo: TextureBuffer = None
_postDataVbo: StaticVertexBuffer = None
_ibo: IndexBuffer = None
_ubo: UniformBuffer = None
_basicVao: VertexArray = None
_postProcessVao: VertexArray = None
_whiteTexture: Texture = None
_framebuffer: Framebuffer = None

renderStats = RenderStats()
screenStats = ScreenStats()
contextInfo = ContextInfo()

def Initialize(initialWidth: int, initialHeight: int, samples: int) -> None:
	global _basicRenderer, _postRenderer, _ubo, _framebuffer, _isInitialized, _basicShader, \
		_posVbo, _instanceDataVbo, _vertexDataTbo, _ibo, _basicVao, _postProcessVao, _whiteTexture, _postProcessShader, _postDataVbo

	if _isInitialized:
		Debug.Log("Renderer already initialized.", LogLevel.Warning)
		return
	
	########################################
	_basicShader = Shader()
	_basicShader.AddStage(GL.GL_VERTEX_SHADER, SHADER_SOURCES_DIRECTORY + "basic.vert")
	_basicShader.AddStage(GL.GL_FRAGMENT_SHADER, SHADER_SOURCES_DIRECTORY + "basic.frag")
	_basicShader.Compile()

	_postProcessShader = Shader()
	_postProcessShader.AddStage(GL.GL_VERTEX_SHADER, SHADER_SOURCES_DIRECTORY + "post.vert")
	_postProcessShader.AddStage(GL.GL_FRAGMENT_SHADER, SHADER_SOURCES_DIRECTORY + "post.frag")
	_postProcessShader.Compile()

	_posVbo = StaticVertexBuffer(_quadVertices)
	_instanceDataVbo = VertexBuffer(BASIC_INSTANCE_DATA_VERTEX_SIZE * MAX_QUADS_COUNT, memoryview(_instanceData))
	_vertexDataTbo = TextureBuffer(BASIC_VERTEX_DATA_VERTEX_SIZE * MAX_QUADS_COUNT * VERTICES_PER_QUAD, GL.GL_RG32F, memoryview(_vertexData))
	_postDataVbo = StaticVertexBuffer(_postData)
	_ibo = IndexBuffer(IndexBuffer.CreateQuadIndices(MAX_QUADS_COUNT), GL.GL_UNSIGNED_INT)

	_basicVao = VertexArray()

	_basicVao.BindVertexBuffer(POS_DATA_BUFFER_BINDING, _posVbo.ID, 0, POS_DATA_VERTEX_SIZE)
	_basicVao.BindVertexBuffer(INSTANCE_DATA_BUFFER_BINDING, _instanceDataVbo.ID, 0, BASIC_INSTANCE_DATA_VERTEX_SIZE)
	_basicVao.BindElementBuffer(_ibo.ID)

	_basicVao.AddLayout(_basicShader.GetAttribLocation("aPosition"), POS_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)
	_basicVao.AddLayout(_basicShader.GetAttribLocation("aColor"), INSTANCE_DATA_BUFFER_BINDING, 4, GL.GL_FLOAT, False, 1)
	_basicVao.AddLayout(_basicShader.GetAttribLocation("aTilingFactor"), INSTANCE_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False, 1)
	_basicVao.AddLayout(_basicShader.GetAttribLocation("aTexIdx"), INSTANCE_DATA_BUFFER_BINDING, 1, GL.GL_FLOAT, False, 1)
	_basicVao.AddMatrixLayout(_basicShader.GetAttribLocation("aTransform"), INSTANCE_DATA_BUFFER_BINDING, 4, 4, GL.GL_FLOAT, False, 1)

	_postProcessVao = VertexArray()

	_postProcessVao.BindVertexBuffer(POST_DATA_BUFFER_BINDING, _postDataVbo.ID, 0, POST_VERTEX_DATA_VERTEX_SIZE)
	_postProcessVao.BindElementBuffer(_ibo.ID)

	_postProcessVao.AddLayout(_postProcessShader.GetAttribLocation("aPosition"), POST_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)
	_postProcessVao.AddLayout(_postProcessShader.GetAttribLocation("aTexCoord"), POST_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False)

	_whiteTexture = Texture.CreateWhiteTexture()

	samplers = [x for x in range(MAX_TEXTURES_COUNT)]
	samplers.remove(BUFFER_TEXTURE_SAMPLER)

	_basicShader.SetUniformIntArray("uTextures", samplers)
	_basicShader.SetUniform1i("uTexCoordsBuffer", BUFFER_TEXTURE_SAMPLER)
	_basicShader.SetUniformBlockBinding("uMatrices", MATRICES_UNIFORM_BLOCK_INDEX)
	_basicShader.Validate()

	_postProcessShader.SetUniform1i("uTexture", NORMAL_TEXTURE_SAMPLER)
	_postProcessShader.SetUniform1i("uTextureMS", MULTISAMPLE_TEXTURE_SAMPLER)
	_postProcessShader.SetUniformBlockBinding("uMatrices", MATRICES_UNIFORM_BLOCK_INDEX)
	_postProcessShader.Validate()

	_ubo = UniformBuffer(UNIFORM_BLOCK_SIZE)
	_ubo.BindToUniform(MATRICES_UNIFORM_BLOCK_INDEX)

	contextInfo.GetInfo()

	_CreateFramebuffer(initialWidth, initialHeight, samples)
	_SetGLSettings()
	_SetRendererCallbacks()

	if not os.path.exists(SCREENSHOT_DIRECTORY):
		os.mkdir(SCREENSHOT_DIRECTORY)

	_isInitialized = True

	Debug.GetGLError()
	Debug.Log("Master renderer fully initialized.", LogLevel.Info)

def CaptureFrame():
	pixels = GL.glReadPixels(0, 0, screenStats.width, screenStats.height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)
	
	img = Image.frombytes("RGB", (screenStats.width, screenStats.height), pixels)
	img = img.transpose(Image.FLIP_TOP_BOTTOM)

	filename = os.path.join(SCREENSHOT_DIRECTORY, "screenshot_" + str(int(time.time()))) + ".jpg"
	img.save(filename, "JPEG")
	Debug.Log(f"Screenshot was saved as '{filename}'.", LogLevel.Info)

def ClearScreen() -> None:
	GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

def SetClearColor(r: float, g: float, b: float, a: float):
	GL.glClearColor(r, g, b, a)

def RenderScene(scene, viewProjectionMatrix: glm.mat4) -> None:
	global _acumVertexCount, _acumDrawsCount

	renderStats.Clear()
	start = time.perf_counter()

	data = np.asarray(viewProjectionMatrix, dtype=_NP_FLOAT)
	_ubo.AddData(memoryview(data), data.size * _GL_FLOAT_SIZE)
	
	_ubo.Bind()

	_framebuffer.Bind()
	
	ClearScreen()

	drawables = [x[1] for x in scene.GetComponents(components.SpriteComponent, components.TransformComponent)]
	opaque = [x for x in drawables if x[0].color.w == 1.0]
	alpha = [x for x in drawables if x not in opaque]

	alpha.sort(key = lambda x: x[0].color.w, reverse = True)

	for (sprite, transform) in opaque:
		_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tilingFactor)

	_FlushNormal()

	GL.glDisable(GL.GL_DEPTH_TEST)
	for (sprite, transform) in alpha:
		_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tilingFactor)

	transformNp = np.zeros((4, 4), dtype=_NP_FLOAT)
	transformNp[3, 3] = 1.0
	
	for _, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
		font = ResourceManager.GetFont(text.font)

		advSum = 0.0

		for char in text.text:
			glyph = font.GetGlyph(ord(char))

			adv = advSum / screenStats.width * (text.size / font.baseSize)

			scWidth = glyph.width / screenStats.width * (text.size / font.baseSize)
			scHeight = glyph.height / screenStats.height * (text.size / font.baseSize)

			advSum += glyph.advance

			transformNp[3, 0] = transform.position.x + adv
			transformNp[3, 1] = transform.position.y
			transformNp[3, 2] = transform.position.z
			transformNp[0, 0] = scWidth
			transformNp[1, 1] = scHeight

			_RenderQuad(glm.make_mat4x4(transformNp.ctypes.data_as(_C_FLOAT_P)), text.color, font.texture, glm.vec2(1.0, 1.0), glyph.texRect)
		
	_FlushNormal()
	
	# for _, system in scene.GetComponent(components.ParticleSystemComponent):
	# 	for particle in system.particlePool:
	# 		if particle.isAlive:
	# 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

	# Renderer.__ParticleRenderer.EndScene()

	# _basicRenderer.RenderQuad(glm.mat4(1.0), glm.vec4(1.0), _framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT), glm.vec2(1.0))
	# _basicRenderer.EndScene()

	_framebuffer.Unbind()

	ClearScreen()
	GL.glViewport(0, 0, screenStats.width, screenStats.height)
	GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

	_RenderFramebuffer(_framebuffer.specification.samples, _framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT))
	
	GL.glPolygonMode(GL.GL_FRONT_AND_BACK, _currentFillMode)
	GL.glEnable(GL.GL_DEPTH_TEST)

	if contextInfo.vendor == Vendor.Nvidia:
		renderStats.videoMemoryUsed = contextInfo.memoryAvailable - GL.glGetInteger(NvidiaIntegerName.GpuMemInfoCurrentAvailable)

	renderStats.drawTime = time.perf_counter() - start

	_THREAD_SYNC.set()

def _ResetCounters() -> None:
	global _quadsCount, _lastTexture, _lastVertexPos, _lastInstancePos

	_quadsCount = 0
	_lastTexture = 0
	_lastVertexPos = 0
	_lastInstancePos = 0

def _FlushNormal():
	global _acumVertexCount, _acumDrawsCount

	if not _quadsCount:
		return

	_basicVao.Bind()

	_basicShader.Use()
		
	textures = _textures[:_lastTexture]
	GL.glBindTextures(0, len(textures), np.asarray(textures, dtype=_NP_UINT))
	GL.glBindTextures(14, 2, np.asarray([_whiteTexture.ID, _vertexDataTbo.TextureID], dtype=_NP_UINT))

	_instanceDataVbo.TransferData(_lastInstancePos * _GL_FLOAT_SIZE)
	_vertexDataTbo.TransferData(_lastVertexPos * _GL_FLOAT_SIZE)
		
	GL.glDrawElementsInstanced(GL.GL_TRIANGLES, _quadsCount * INDICES_PER_QUAD, _ibo.Type, None, _quadsCount)

	renderStats.drawsCount += 1
	renderStats.vertexCount += _quadsCount * VERTICES_PER_QUAD
	_ResetCounters()

def _RenderQuad(transform: glm.mat4, color: glm.vec4, texture: Texture or int, tilingFactor: glm.vec2, texRect: RectangleF = RectangleF.One()):
	global _lastTexture, _lastVertexPos, _lastInstancePos, _quadsCount

	if _quadsCount >= MAX_QUADS_COUNT:
		_FlushNormal()

	texIdx = WHITE_TEXTURE_SAMPLER

	if isinstance(texture, Texture):
		tId = texture.ID
	else:
		tId = texture

	if texture:
		for i in range(_lastTexture):
			if _textures[i] == tId:
				texIdx = i
				break
		
		if texIdx == WHITE_TEXTURE_SAMPLER:
			if _lastTexture >= AVAILABLE_USER_TEXTURES_COUNT:
				_FlushNormal()
			
			texIdx = _lastTexture
			_textures[_lastTexture] = tId
			_lastTexture += 1

	_vertexData[_lastVertexPos:_lastVertexPos + BASIC_VERTEX_VERTEX_VALUES_COUNT * VERTICES_PER_QUAD] = (
		texRect.left, texRect.top,
		texRect.left, texRect.bottom,
		texRect.right, texRect.bottom,
		texRect.right, texRect.top
	)

	_instanceData[_lastInstancePos:_lastInstancePos + BASIC_INSTANCE_VERTEX_VALUES_COUNT] = (
		color.x, color.y, color.z, color.w, tilingFactor.x, tilingFactor.y, texIdx) + tuple(transform[0]) + tuple(transform[1]) + tuple(transform[2]) + tuple(transform[3]
	)

	_lastVertexPos += BASIC_VERTEX_VERTEX_VALUES_COUNT * VERTICES_PER_QUAD
	_lastInstancePos += BASIC_INSTANCE_VERTEX_VALUES_COUNT
	_quadsCount += 1

def _RenderFramebuffer(samplesToRender: int, attachmentToRender: int) -> None:
	global _acumVertexCount, _acumDrawsCount

	_postProcessVao.Bind()

	_postProcessShader.Use()
	_postProcessShader.SetUniform1i("uSamples", samplesToRender)

	GL.glBindTextureUnit(MULTISAMPLE_TEXTURE_SAMPLER if samplesToRender > 1 else NORMAL_TEXTURE_SAMPLER, attachmentToRender)

	GL.glDrawElementsInstanced(GL.GL_TRIANGLES, INDICES_PER_QUAD, _ibo.Type, None, 1)

	renderStats.drawsCount += 1
	renderStats.vertexCount += VERTICES_PER_QUAD
	_ResetCounters()

def _KeyDownCallback(key: int, _, repeated: bool) -> bool:
	global _currentFillMode

	if repeated:
		return False

	if key == Keys.KeyGrave:
		_currentFillMode = next(_polygonModeIter)
		Debug.Log(f"Renderer drawing mode set to: {_GL_FILL_MODE_NAMES_MAP}", LogLevel.Info)
	elif key == Keys.KeyF1:
		CaptureFrame()

	return False

def _ResizeCallback(width: int, height: int) -> bool:
	if width == 0 or height == 0:
		return False

	GL.glScissor(0, 0, width, height)
	GL.glViewport(0, 0, width, height)

	_framebuffer.Resize(width, height)

	return False

def _SetGLSettings() -> None:
	GL.glEnable(GL.GL_MULTISAMPLE)

	if contextInfo.vendor == Vendor.Nvidia:
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

def _CreateFramebuffer(initialWidth: int, initialHeight: int, samples: int) -> None:
	global _framebuffer

	fbSpec = FramebufferSpec(initialWidth, initialHeight)
	fbSpec.samples = samples

	colorAttachmentSpec = FramebufferAttachmentSpec(FramebufferTextureFormat.Rgba)
	
	depthAttachmentSpec = FramebufferAttachmentSpec(FramebufferTextureFormat.Depth24Stencil8)
	depthAttachmentSpec.minFilter = GL.GL_NEAREST
	depthAttachmentSpec.magFilter = GL.GL_NEAREST

	fbSpec.attachmentSpecs = [
		colorAttachmentSpec,
		depthAttachmentSpec
	]

	_framebuffer = Framebuffer(fbSpec)

def _SetRendererCallbacks() -> None:
	EventHandler.WindowResize += EventHook(_ResizeCallback, -1)
	EventHandler.KeyDown += EventHook(_KeyDownCallback, -1)