#region Import
from .renderBatch import RenderBatch
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import VertexBuffer, IndexBuffer
from ..texturing.textureUtils import TextureHandle
from ..texturing.texture import Texture, TextureData
from ...managers import TextureManager
from ...transform import CreateQuadIndices, Matrix4, QuadVerticesFloat
from ...debug import Log, LogLevel, GetGLError
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
import glm
import numpy
#endregion

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * GL_FLOAT_SIZE
TRANSFORM_VERTEX_SIZE = 16 * GL_FLOAT_SIZE
POS_VERTEX_SIZE = 3 * GL_FLOAT_SIZE
__DATA_VERTEX_SIZE = (4 + 2 + 1 + 2) * GL_FLOAT_SIZE

INSTANCE_DATA_VERTEX_SIZE = (4 + 2 + 1 + 16) * GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = 2 * GL_FLOAT_SIZE

class BasicRenderer(RendererComponent):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstancedMulti.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstancedMulti.frag")
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
		self.vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False))
		self.posVbo.AddDataDirect(QuadVerticesFloat, len(QuadVerticesFloat) * GL_FLOAT_SIZE)

		self.vertexDataVbo.Bind()
		self.vao.SetVertexSize(VERTEX_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, GL.GL_FLOAT, False))

		self.instanceDataVbo.Bind()
		self.vao.SetVertexSize(INSTANCE_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()

		colLoc = self.shader.GetAttribLocation("aColor")
		tfLoc = self.shader.GetAttribLocation("aTilingFactor")
		tiLoc = self.shader.GetAttribLocation("aTexIdx")

		self.vao.AddLayout(VertexArrayLayout(colLoc, 4, GL.GL_FLOAT, False))
		self.vao.AddLayout(VertexArrayLayout(tfLoc, 2, GL.GL_FLOAT, False))
		self.vao.AddLayout(VertexArrayLayout(tiLoc, 1, GL.GL_FLOAT, False))

		self.vao.AddDivisor(colLoc, 1)
		self.vao.AddDivisor(tfLoc, 1)
		self.vao.AddDivisor(tiLoc, 1)

		matLoc = self.shader.GetAttribLocation("aTransform")
		for i in range(4):
			self.vao.AddLayout(VertexArrayLayout(matLoc + i, 4, GL.GL_FLOAT, False))
			self.vao.AddDivisor(matLoc + i, 1)

		#self.__batch = RenderBatch(VERTEX_SIZE * RendererSettings.MaxQuadsCount)
		self.__vertexData = []
		self.__instanceData = []
		self.__indexCount = 0

		self.__textures = [0] * (RendererSettings.MaxTextures - 1)
		self.__lastTexture = 1

		wtData = TextureData(1, 1)
		wtData.data = numpy.asarray([255, 255, 255], dtype = numpy.uint8)
		wtData.minFilter = GL.GL_NEAREST
		wtData.magFilter = GL.GL_NEAREST
		wtData.mipLevels = 1
		wtData.format = GL.GL_RGB

		self.__whiteTexture = Texture(wtData)

		samplers = [x for x in range(RendererSettings.MaxTextures)]

		self.shader.Use()
		self.shader.SetUniformIntArray("uTextures", samplers)

		######################### TEMPORARY #################################
		GL.glPointSize(5.0)

		Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		if not self.__indexCount:
			return
		
		self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		GL.glBindTextureUnit(0, self.__whiteTexture.ID)
		GL.glBindTextures(1, self.__lastTexture, self.__textures[:self.__lastTexture + 1])

		self.vao.Bind()
		self.ibo.Bind()

		self.instanceDataVbo.AddDataDirect(self.__instanceData, len(self.__instanceData) * GL_FLOAT_SIZE)
		self.vertexDataVbo.AddDataDirect(self.__vertexData, len(self.__vertexData) * GL_FLOAT_SIZE)

		GL.glDrawElementsInstanced(GL.GL_TRIANGLES, self.__indexCount, GL.GL_UNSIGNED_INT, None, self.__indexCount // 6)

		RenderStats.DrawsCount += 1

		#self.__batch.Clear()
		self.__indexCount = 0
		self.__vertexData.clear()
		self.__instanceData.clear()
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