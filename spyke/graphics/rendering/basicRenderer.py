from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray
from ..buffers import VertexBuffer, TextureBuffer, IndexBuffer
from ..texturing.texture import Texture
from ..rectangle import RectangleF
from ...debugging import Debug, LogLevel
from ...constants import _GL_FLOAT_SIZE, _NP_UINT

from OpenGL import GL
import glm
import numpy as np

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * _GL_FLOAT_SIZE

POS_VERTEX_SIZE = 3 * _GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = (4 + 2 + 1 + 16) * _GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = 2 * _GL_FLOAT_SIZE

VERTICES_PER_QUAD = 6

WHITE_TEXTURE_SAMPLER = 14
BUFFER_TEXTURE_SAMPLER = 15

AVAILABLE_USER_TEXTURES_COUNT = RendererSettings.MaxTextures - 2

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1

class BasicRenderer(object):
	__QuadVertices = [
		0.0, 0.0, 0.0,
		0.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 0.0, 0.0,
		0.0, 0.0, 0.0]

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstanced.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstanced.frag")
		self.shader.Compile()

		self.posVbo = VertexBuffer(POS_VERTEX_SIZE * VERTICES_PER_QUAD, GL.GL_STATIC_DRAW)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount)
		self.vertexDataTbo = TextureBuffer(VERTEX_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * VERTICES_PER_QUAD, GL.GL_RG32F)

		self.posVbo.AddData(BasicRenderer.__QuadVertices, len(BasicRenderer.__QuadVertices) * _GL_FLOAT_SIZE)

		self.vao = VertexArray()

		self.vao.BindVertexBuffer(POS_DATA_BUFFER_BINDING, self.posVbo.ID, 0, POS_VERTEX_SIZE)
		self.vao.BindVertexBuffer(INSTANCE_DATA_BUFFER_BINDING, self.instanceDataVbo.ID, 0, INSTANCE_DATA_VERTEX_SIZE)

		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), POS_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)

		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), INSTANCE_DATA_BUFFER_BINDING, 4, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTilingFactor"), INSTANCE_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexIdx"), INSTANCE_DATA_BUFFER_BINDING, 1, GL.GL_FLOAT, False, 1)
		self.vao.AddMatrixLayout(self.shader.GetAttribLocation("aTransform"), INSTANCE_DATA_BUFFER_BINDING, 4, 4, GL.GL_FLOAT, False, 1)

		self.__vertexData = []
		self.__instanceData = []
		self.__vertexCount = 0

		self.__textures = [0] * AVAILABLE_USER_TEXTURES_COUNT
		self.__lastTexture = 0

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
		if self.__vertexCount != 0:
			self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		GL.glBindTextureUnit(WHITE_TEXTURE_SAMPLER, self.__whiteTexture.ID)
		GL.glBindTextureUnit(BUFFER_TEXTURE_SAMPLER, self.vertexDataTbo.TextureID)

		textures = self.__textures[:self.__lastTexture]
		GL.glBindTextures(0, len(textures), np.asarray(textures, dtype=_NP_UINT))

		self.vao.Bind()

		self.instanceDataVbo.AddData(self.__instanceData, len(self.__instanceData) * _GL_FLOAT_SIZE)
		self.vertexDataTbo.AddData(self.__vertexData, len(self.__vertexData) * _GL_FLOAT_SIZE)

		GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, self.__vertexCount, self.__vertexCount // VERTICES_PER_QUAD)

		RenderStats.drawsCount += 1
		RenderStats.vertexCount += self.__vertexCount

		self.__vertexData.clear()
		self.__instanceData.clear()
		self.__vertexCount = 0
		self.__lastTexture = 0
		
	def RenderQuad(self, transform: glm.mat4, color: glm.vec4, texture: Texture, tilingFactor: glm.vec2, texRect: RectangleF = RectangleF.One()):
		if RenderStats.quadsCount >= RendererSettings.MaxQuadsCount:
			self.__Flush()

		texIdx = WHITE_TEXTURE_SAMPLER

		if texture:
			for i in range(self.__lastTexture):
				if self.__textures[i] == texture.ID:
					texIdx = i
					break
			
			if texIdx == WHITE_TEXTURE_SAMPLER:
				if self.__lastTexture >= AVAILABLE_USER_TEXTURES_COUNT:
					self.__Flush()
				
				texIdx = self.__lastTexture
				self.__textures[self.__lastTexture] = texture.ID
				self.__lastTexture += 1

		vertexData = [
			texRect.left, texRect.top,
			texRect.left, texRect.bottom,
			texRect.right, texRect.bottom,
			texRect.right, texRect.bottom,
			texRect.right, texRect.top,
			texRect.left, texRect.top
		]
		
		instanceData = [color.x, color.y, color.z, color.w, tilingFactor.x, tilingFactor.y, texIdx] + list(transform[0]) + list(transform[1]) + list(transform[2]) + list(transform[3])

		self.__vertexData.extend(vertexData)
		self.__instanceData.extend(instanceData)
		
		RenderStats.quadsCount += 1
		self.__vertexCount += VERTICES_PER_QUAD