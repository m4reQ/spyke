#region Import
from .rendererComponent import RendererComponent
from .renderStats import RenderStats
from .renderBatch import RenderBatch
from ..shader import Shader
from ..buffers import IndexBuffer, VertexBuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ..texturing.textureUtils import TextureHandle
from ...managers import TextureManager
from ...transform import Matrix4, CreateQuadIndices, Vector2
from ...enums import VertexAttribType, GLType, ShaderType
from ...utils import GL_FLOAT_SIZE, Timer
from ...debug import Log, LogLevel

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (2 + 2 + 1 + 4 + 2 + 1) * GL_FLOAT_SIZE

###########################################
#Change shader and everything other to accept rotation as 3 floats in all directions

class ParticleRenderer(RendererComponent):
	MaxParticleCount = 150
	MaxVertexCount = MaxParticleCount * 1

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/particle.vert")
		self.shader.AddStage(ShaderType.GeometryShader, "spyke/graphics/shaderSources/particle.geom")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/particle.frag")
		self.shader.Compile()
		
		self.vao = VertexArray()
		self.vbo = VertexBuffer(ParticleRenderer.MaxVertexCount * VERTEX_SIZE)

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aSize"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aRotation"), 1, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 1, VertexAttribType.Float, False)])
		
		self.__batches = []
		self.__vertexCount = 0

		Log("Particle renderer initialized.", LogLevel.Info)
	
	def RenderParticle(self, pos: glm.vec3, size: glm.vec3, rot: glm.vec3, color: glm.vec4, texHandle: TextureHandle):
		data = [
			pos.x, pos.y, pos.z,
			size.x, size.y, size.z,
			rot.x, rot.y, rot.z,
			color.x, color.y, color.z, color.w,
			texHandle.U, texHandle.V,
			texHandle.Index]

		try:
			batch = next(x for x in self.__batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(ParticleRenderer.MaxVertexCount * VERTEX_SIZE)
			batch.texarrayID = texHandle.TexarrayID
			self.__batches.append(batch)
		
		batch.AddData(data)
		batch.vertexCount += 1

		RenderStats.QuadsCount += 1

	def EndScene(self) -> None:
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush()
				break
	
	def __Flush(self):
		GL.glDepthMask(False)

		self.shader.Use()
		
		self.vbo.Bind()
		self.vao.Bind()

		for batch in self.__batches:
			TextureManager.GetArray(batch.texarrayID).Bind()

			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawArrays(GL.GL_POINTS, 0, batch.vertexCount)
			RenderStats.DrawsCount += 1

			batch.Clear()
		
		GL.glDepthMask(True)