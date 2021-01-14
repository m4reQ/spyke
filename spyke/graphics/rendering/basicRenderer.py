#region Import
from .renderBatch import RenderBatch
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray
from ..buffers import VertexBuffer, IndexBuffer
from ..texturing.textureUtils import GetWhiteTexture
from ..texturing.texture import Texture
from ...managers import TextureManager
from ...transform import CreateQuadIndices, Matrix4
from ...debug import Log, LogLevel, GetGLError
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
import glm
import numpy
#endregion

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * GL_FLOAT_SIZE
POS_VERTEX_SIZE = 3 * GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = (4 + 2 + 1 + 16) * GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = 2 * GL_FLOAT_SIZE

class BasicRenderer(RendererComponent):
	__QuadVertices = [
		0.0, 0.0, 0.0,
		0.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 0.0, 0.0]

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstanced.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstanced.frag")
		self.shader.Compile()

		self.posVbo = VertexBuffer(POS_VERTEX_SIZE * 4, GL.GL_STATIC_DRAW)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount)
		self.vertexDataVbo = VertexBuffer(VERTEX_DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * 4)

		self.ibo = IndexBuffer(CreateQuadIndices(RendererSettings.MaxQuadsCount))

		self.vao = VertexArray()
		self.vao.Bind()

		self.posVbo.Bind()
		self.vao.SetVertexSize(POS_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False)
		self.posVbo.AddDataDirect(BasicRenderer.__QuadVertices, len(BasicRenderer.__QuadVertices) * GL_FLOAT_SIZE)

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
		self.__indexCount = 0

		self.__textures = [0] * (RendererSettings.MaxTextures - 1)
		self.__lastTexture = 1

		self.__whiteTexture = Texture(GetWhiteTexture())

		samplers = [x for x in range(RendererSettings.MaxTextures)]

		self.shader.Use()
		self.shader.SetUniformIntArray("uTextures", samplers)

		Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		if self.__indexCount != 0:
			self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		GL.glBindTextureUnit(0, self.__whiteTexture.ID)

		for i in range(self.__lastTexture):
			GL.glBindTextureUnit(i, self.__textures[i])

		self.vao.Bind()
		self.ibo.Bind()

		self.instanceDataVbo.AddDataDirect(self.__instanceData, len(self.__instanceData) * GL_FLOAT_SIZE)
		self.vertexDataVbo.AddDataDirect(self.__vertexData, len(self.__vertexData) * GL_FLOAT_SIZE)

		GL.glDrawElementsInstanced(GL.GL_TRIANGLES, self.__indexCount, GL.GL_UNSIGNED_INT, None, self.__indexCount // 6)

		RenderStats.DrawsCount += 1

		self.__vertexData.clear()
		self.__instanceData.clear()
		self.__indexCount = 0
		self.__lastTexture = 1
		
	def RenderQuad(self, transform: Matrix4, color: glm.vec4, texture: Texture, tilingFactor: glm.vec2):
		if self.__indexCount // 6 >= RendererSettings.MaxQuadsCount:
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

		vertexData = [
			0.0, 1.0,
			0.0, 0.0,
			1.0, 0.0,
			1.0, 1.0
		]
		
		instanceData = [color.x, color.y, color.z, color.w, tilingFactor.x, tilingFactor.y, texIdx] + list(transform[0]) + list(transform[1]) + list(transform[2]) + list(transform[3])

		self.__vertexData.extend(vertexData)
		self.__instanceData.extend(instanceData)
		
		RenderStats.QuadsCount += 1
		self.__indexCount += 6