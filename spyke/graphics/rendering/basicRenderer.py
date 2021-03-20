#region Import
from .renderStats import RenderStats
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray
from ..buffers import VertexBuffer
from ..texturing.texture import Texture
from ..rectangle import RectangleF
from ...debugging import Debug, LogLevel
from ...constants import _GL_FLOAT_SIZE

from OpenGL import GL
import glm
import numpy as np
#endregion

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * _GL_FLOAT_SIZE
POS_VERTEX_SIZE = 3 * _GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = (4 + 2 + 1 + 16) * _GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = 2 * _GL_FLOAT_SIZE

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

		self.posVbo = VertexBuffer(POS_VERTEX_SIZE * 6, GL.GL_STATIC_DRAW)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount)
		self.vertexDataVbo = VertexBuffer(VERTEX_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * 6)

		self.vao = VertexArray()
		self.vao.Bind()

		self.posVbo.Bind()
		self.vao.SetVertexSize(POS_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False)
		self.posVbo.AddDataDirect(BasicRenderer.__QuadVertices, len(BasicRenderer.__QuadVertices) * _GL_FLOAT_SIZE)

		self.vertexDataVbo.Bind()
		self.vao.SetVertexSize(VERTEX_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), 2, GL.GL_FLOAT, False)

		self.instanceDataVbo.Bind()
		self.vao.SetVertexSize(INSTANCE_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), 4, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTilingFactor"), 2, GL.GL_FLOAT, False, 1)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexIdx"), 1, GL.GL_FLOAT, False, 1)

		matLoc = self.shader.GetAttribLocation("aTransform")
		for i in range(4):
			self.vao.AddLayout(matLoc + i, 4, GL.GL_FLOAT, False, 1)

		self.__vertexData = []
		self.__instanceData = []
		self.__vertexCount = 0

		self.__textures = [0] * (RendererSettings.MaxTextures - 1)
		self.__lastTexture = 1

		self.__whiteTexture = Texture.CreateWhiteTexture()

		samplers = [x for x in range(RendererSettings.MaxTextures)]

		self.shader.Use()
		self.shader.SetUniformIntArray("uTextures", samplers)

		Debug.GetGLError()
		Debug.Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		if self.__vertexCount != 0:
			self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		GL.glBindTextureUnit(0, self.__whiteTexture.ID)

		for i in range(1, self.__lastTexture):
			GL.glBindTextureUnit(i, self.__textures[i])

		self.vao.Bind()

		self.instanceDataVbo.AddDataDirect(self.__instanceData, len(self.__instanceData) * _GL_FLOAT_SIZE)
		self.vertexDataVbo.AddDataDirect(self.__vertexData, len(self.__vertexData) * _GL_FLOAT_SIZE)

		GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, self.__vertexCount, self.__vertexCount // 6)

		RenderStats.DrawsCount += 1
		RenderStats.VertexCount += self.__vertexCount

		self.__vertexData.clear()
		self.__instanceData.clear()
		self.__vertexCount = 0
		self.__lastTexture = 1
		
	def RenderQuad(self, transform: glm.mat4 or np.array, color: glm.vec4, texture: Texture, tilingFactor: glm.vec2, texRect: RectangleF = None):
		if RenderStats.QuadsCount >= RendererSettings.MaxQuadsCount:
			self.__Flush()

		texIdx = 0.0

		if texture:
			for i in range(self.__lastTexture):
				if self.__textures[i] == texture.ID:
					texIdx = float(i)
					break
			
			if texIdx == 0.0:
				if self.__lastTexture >= RendererSettings.MaxTextures - 1:
					self.__Flush()
				
				texIdx = float(self.__lastTexture)
				self.__textures[self.__lastTexture] = texture.ID
				self.__lastTexture += 1

		if not texRect:
			vertexData = [
				0.0, 1.0,
				0.0, 0.0,
				1.0, 0.0,
				1.0, 0.0,
				1.0, 1.0,
				0.0, 1.0
			]
		else:
			vertexData = [
				texRect.left, texRect.top,
				texRect.left, texRect.bottom,
				texRect.right, texRect.bottom,
				texRect.right, texRect.bottom,
				texRect.right, texRect.top,
				texRect.left, texRect.top
			]
		
		instanceData = [color.x, color.y, color.z, color.w, tilingFactor.x, tilingFactor.y, texIdx]
		
		if isinstance(transform, glm.mat4):
			instanceData.extend(list(transform[0]) + list(transform[1]) + list(transform[2]) + list(transform[3]))
		elif isinstance(transform, np.ndarray):
			instanceData.extend(transform.flat)

		self.__vertexData.extend(vertexData)
		self.__instanceData.extend(instanceData)
		
		RenderStats.QuadsCount += 1
		self.__vertexCount += 6