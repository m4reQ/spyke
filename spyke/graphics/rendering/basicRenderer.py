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
from ...transform import CreateQuadIndices, Matrix4, QuadVerticsFloat
from ...debug import Log, LogLevel, GetGLError
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
import glm
import numpy
#endregion

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * GL_FLOAT_SIZE
TRANSFORM_VERTEX_SIZE = 16 * GL_FLOAT_SIZE
POS_VERTEX_SIZE = 3 * GL_FLOAT_SIZE
DATA_VERTEX_SIZE = (4 + 2 + 1 + 2) * GL_FLOAT_SIZE

class BasicRenderer(RendererComponent):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstancedMulti.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstancedMulti.frag")
		self.shader.Compile()

		self.posVbo = VertexBuffer(POS_VERTEX_SIZE * 4, GL.GL_STATIC_DRAW)
		self.vertexDataVbo = VertexBuffer(DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * 4)
		self.transformVbo = VertexBuffer(TRANSFORM_VERTEX_SIZE * RendererSettings.MaxQuadsCount)

		self.vao = VertexArray()
		self.ibo = IndexBuffer(CreateQuadIndices(RendererSettings.MaxQuadsCount))

		self.vao.Bind()

		self.posVbo.Bind()
		self.vao.SetVertexSize(POS_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.posVbo.AddData(QuadVerticsFloat, len(QuadVerticsFloat) * GL_FLOAT_SIZE)
		self.vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False))

		self.vertexDataVbo.Bind()
		self.vao.SetVertexSize(DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 			4, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 		2, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 		1, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTilingFactor"), 	2, GL.GL_FLOAT, False)])

		self.transformVbo.Bind()
		self.vao.SetVertexSize(TRANSFORM_VERTEX_SIZE)
		self.vao.ClearVertexOffset()

		idx = self.shader.GetAttribLocation("aTransform")
		for i in range(4):
			self.vao.AddLayout(VertexArrayLayout(idx + i, 4, GL.GL_FLOAT, False))
			self.vao.AddDivisor(idx + i, 1)

		self.__batch = RenderBatch(VERTEX_SIZE * RendererSettings.MaxQuadsCount)

		self.__textures = [0] * RendererSettings.MaxTextures
		self.__lastTexture = 1 #0 reserved for white texture

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

		Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		if not RenderStats.QuadsCount:
			return
		
		self.__Flush()

	def __Flush(self) -> None:
		self.shader.Use()

		self.vao.Bind()
		self.ibo.Bind()

		GL.glBindTextureUnit(0, self.__whiteTexture.ID)

		for i in range(1, self.__lastTexture):
			GL.glBindTextureUnit(i, self.__textures[i])

		self.vertexDataVbo.Bind()
		self.vertexDataVbo.AddData(self.__batch.data, len(self.__batch.data) * GL_FLOAT_SIZE)

		self.transformVbo.Bind()
		self.transformVbo.AddData(self.__batch.transformData, len(self.__batch.transformData) * GL_FLOAT_SIZE)

		GL.glDrawElementsInstanced(GL.GL_TRIANGLES, self.__batch.indexCount, GL.GL_UNSIGNED_INT, None, RenderStats.QuadsCount)

		RenderStats.DrawsCount += 1

		self.__batch.Clear()
		self.__lastTexture = 1
		
	def RenderQuad(self, transform: Matrix4, color: glm.vec4, texture: Texture, tilingFactor: glm.vec2):
		if not self.__batch.WouldAccept(VERTEX_SIZE * 4):
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

		data = [
			color.x, color.y, color.z, color.w, 0.0, 1.0, texIdx, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, 0.0, 0.0, texIdx, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, 1.0, 0.0, texIdx, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, 1.0, 1.0, texIdx, tilingFactor.x, tilingFactor.y]

		self.__batch.AddData(data)

		transformData = list(transform[0]) + list(transform[1]) + list(transform[2]) + list(transform[3])
		self.__batch.AddTransformData(transformData)
		
		RenderStats.QuadsCount += 1
		self.__batch.indexCount += 6