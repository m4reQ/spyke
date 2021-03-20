#region Import
from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer
from ..vertexArray import VertexArray
from ..texturing.textureHandle import TextureHandle
from .rendererSettings import RendererSettings
from ...constants import _GL_FLOAT_SIZE
from ...debugging import Debug, LogLevel

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (2 + 2 + 1 + 4 + 2 + 1) * _GL_FLOAT_SIZE

###########################################
#Change shader and everything other to accept rotation as 3 floats in all directions
#CHANGE THE TEXTURES SIDE OF RENDERING

class ParticleRenderer(object):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/particle.vert")
		self.shader.AddStage(GL.GL_GEOMETRY_SHADER, "spyke/graphics/shaderSources/particle.geom")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/particle.frag")
		self.shader.Compile()
		
		self.vao = VertexArray()
		self.vbo = VertexBuffer(RendererSettings.MaxQuadsCount * VERTEX_SIZE)

		self.vao.Bind()
		self.vbo.Bind()
		self.vao.ClearVertexOffset()
		self.vao.SetVertexSize(VERTEX_SIZE)
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 2, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aSize"), 2, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aRotation"), 1, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), 4, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), 2, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexIdx"), 1, GL.GL_FLOAT, False)

		self.__vertexData = []
		self.__vertexCount = 0

		Debug.Log("Particle renderer initialized.", LogLevel.Info)
	
	def RenderParticle(self, pos: glm.vec3, size: glm.vec3, rot: glm.vec3, color: glm.vec4, texHandle: TextureHandle):
		if RenderStats.QuadsCount >= RendererSettings.MaxQuadsCount:
			self.__Flush()

		data = [
			pos.x, pos.y, pos.z,
			size.x, size.y, size.z,
			rot.x, rot.y, rot.z,
			color.x, color.y, color.z, color.w,
			texHandle.U, texHandle.V,
			texHandle.Index]
		
		self.__vertexData.extend(data)

		RenderStats.QuadsCount += 1
		self.__vertexCount += 1

		# try:
		# 	batch = next(x for x in self.__batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * _GL_FLOAT_SIZE))
		# except StopIteration:
		# 	batch = RenderBatch(ParticleRenderer.MaxVertexCount * VERTEX_SIZE)
		# 	batch.texarrayID = texHandle.TexarrayID
		# 	self.__batches.append(batch)
		
	def EndScene(self) -> None:
		if self.__vertexCount != 0:
			self.__Flush()
	
	def __Flush(self):
		GL.glDepthMask(False)

		self.shader.Use()
		self.vao.Bind()

		self.vbo.AddDataDirect(self.__vertexData, len(self.__vertexData) * _GL_FLOAT_SIZE)
		GL.glDrawArrays(GL.GL_POINTS, 0, self.__vertexCount)

		RenderStats.DrawsCount += 1
		self.__vertexData.clear()
		self.__vertexCount = 0