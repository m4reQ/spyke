from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray
from ..buffers import VertexBuffer, TextureBuffer, StaticVertexBuffer, IndexBuffer
from ..texturing.texture import Texture
from ..rectangle import RectangleF
from ...debugging import Debug, LogLevel
from ...constants import _GL_FLOAT_SIZE, _NP_FLOAT, _NP_UINT

from OpenGL import GL
import glm
import numpy as np
import struct

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * _GL_FLOAT_SIZE

POS_VERTEX_SIZE = 3 * _GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = (4 + 2 + 1 + 16) * _GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = 2 * _GL_FLOAT_SIZE

INSTANCE_VERTEX_VALUES_COUNT = 4 + 2 + 1 + 16
VERTEX_VERTEX_VALUES_COUNT = 2

VERTICES_PER_QUAD = 4

WHITE_TEXTURE_SAMPLER = 14
BUFFER_TEXTURE_SAMPLER = 15

AVAILABLE_USER_TEXTURES_COUNT = RendererSettings.MaxTextures - 2

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1

class BasicRenderer(object):
	_QuadVertices = [
		0.0, 0.0, 0.0,
		0.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 0.0, 0.0]

	def __init__(self):
		self._vertexData = np.empty(VERTEX_VERTEX_VALUES_COUNT * RendererSettings.MaxQuadsCount * VERTICES_PER_QUAD, dtype=_NP_FLOAT)
		self._instanceData = np.empty(INSTANCE_VERTEX_VALUES_COUNT * RendererSettings.MaxQuadsCount, dtype=_NP_FLOAT)

		self._lastVertexPos = 0
		self._lastInstancePos = 0

		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstanced.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstanced.frag")
		self.shader.Compile()

		self.posVbo = StaticVertexBuffer(BasicRenderer._QuadVertices)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount, memoryview(self._instanceData))
		self.vertexDataTbo = TextureBuffer(VERTEX_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * VERTICES_PER_QUAD, GL.GL_RG32F, memoryview(self._vertexData))

		self.ibo = IndexBuffer(IndexBuffer.CreateQuadIndices(RendererSettings.MaxQuadsCount), GL.GL_UNSIGNED_SHORT)

		self.vao = VertexArray()

		self.vao.BindVertexBuffer(POS_DATA_BUFFER_BINDING, self.posVbo.ID, 0, POS_VERTEX_SIZE)
		self.vao.BindVertexBuffer(INSTANCE_DATA_BUFFER_BINDING, self.instanceDataVbo.ID, 0, INSTANCE_DATA_VERTEX_SIZE)
		self.vao.BindElementBuffer(self.ibo.ID)

		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), POS_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)

		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), INSTANCE_DATA_BUFFER_BINDING, 4, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTilingFactor"), INSTANCE_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexIdx"), INSTANCE_DATA_BUFFER_BINDING, 1, GL.GL_FLOAT, False, 1)
		self.vao.AddMatrixLayout(self.shader.GetAttribLocation("aTransform"), INSTANCE_DATA_BUFFER_BINDING, 4, 4, GL.GL_FLOAT, False, 1)

		self._vertexCount = 0

		self.__textures = [0] * AVAILABLE_USER_TEXTURES_COUNT
		self._lastTexture = 0

		self.__whiteTexture = Texture.CreateWhiteTexture()

		samplers = [x for x in range(AVAILABLE_USER_TEXTURES_COUNT)]
		samplers.append(WHITE_TEXTURE_SAMPLER)

		self.shader.Use()
		self.shader.SetUniformIntArray("uTextures", samplers)
		self.shader.SetUniform1i("uTexCoordsBuffer", BUFFER_TEXTURE_SAMPLER)

		self.shader.Validate()
		Debug.GetGLError()
		Debug.Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		if self._vertexCount != 0:
			self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		GL.glBindTextureUnit(WHITE_TEXTURE_SAMPLER, self.__whiteTexture.ID)
		GL.glBindTextureUnit(BUFFER_TEXTURE_SAMPLER, self.vertexDataTbo.TextureID)

		textures = self.__textures[:self._lastTexture]
		GL.glBindTextures(0, len(textures), np.asarray(textures, dtype=_NP_UINT))

		self.vao.Bind()

		self.instanceDataVbo.TransferData(self._lastInstancePos * _GL_FLOAT_SIZE)
		self.vertexDataTbo.TransferData(self._lastVertexPos * _GL_FLOAT_SIZE)
		
		GL.glDrawElementsInstanced(GL.GL_TRIANGLES, self._vertexCount, self.ibo.Type, None, self._vertexCount // VERTICES_PER_QUAD)

		RenderStats.drawsCount += 1
		RenderStats.vertexCount += self._vertexCount

		self._vertexCount = 0
		self._lastTexture = 0
		self._lastVertexPos = 0
		self._lastInstancePos = 0
		
	def RenderQuad(self, transform: glm.mat4, color: glm.vec4, texture: Texture or int, tilingFactor: glm.vec2, texRect: RectangleF = RectangleF.One()):
		if RenderStats.quadsCount >= RendererSettings.MaxQuadsCount:
			self.__Flush()

		texIdx = WHITE_TEXTURE_SAMPLER

		if isinstance(texture, Texture):
			tId = texture.ID
		else:
			tId = texture

		if texture:
			for i in range(self._lastTexture):
				if self.__textures[i] == tId:
					texIdx = i
					break
			
			if texIdx == WHITE_TEXTURE_SAMPLER:
				if self._lastTexture >= AVAILABLE_USER_TEXTURES_COUNT:
					self.__Flush()
				
				texIdx = self._lastTexture
				self.__textures[self._lastTexture] = tId
				self._lastTexture += 1

		vertexData = (
			texRect.left, texRect.top,
			texRect.left, texRect.bottom,
			texRect.right, texRect.bottom,
			texRect.right, texRect.top
		)
		
		instanceData = (color.x, color.y, color.z, color.w, tilingFactor.x, tilingFactor.y, texIdx) + tuple(transform[0]) + tuple(transform[1]) + tuple(transform[2]) + tuple(transform[3])

		self._vertexData[self._lastVertexPos:self._lastVertexPos + VERTEX_VERTEX_VALUES_COUNT * VERTICES_PER_QUAD] = vertexData
		self._instanceData[self._lastInstancePos:self._lastInstancePos + INSTANCE_VERTEX_VALUES_COUNT] = instanceData

		self._lastVertexPos += VERTEX_VERTEX_VALUES_COUNT * VERTICES_PER_QUAD
		self._lastInstancePos += INSTANCE_VERTEX_VALUES_COUNT
		
		RenderStats.quadsCount += 1
		self._vertexCount += VERTICES_PER_QUAD