# region Import
from .rendererInfo import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer
from ..vertex_array import VertexArray
from .rendererSettings import RendererSettings
from ...constants import _GL_FLOAT_SIZE
from ...debugging import Debug, LogLevel

from OpenGL import GL
import glm
# endregion

VERTEX_SIZE = (2 + 2 + 1 + 4 + 2 + 1) * _GL_FLOAT_SIZE

###########################################
# Change shader and everything other to accept rotation as 3 floats in all directions
# CHANGE THE TEXTURES SIDE OF RENDERING


class ParticleRenderer(object):
    def __init__(self):
        self.shader = Shader()
        self.shader.AddStage(GL.GL_VERTEX_SHADER,
                             "spyke/graphics/shaderSources/particle.vert")
        self.shader.AddStage(GL.GL_GEOMETRY_SHADER,
                             "spyke/graphics/shaderSources/particle.geom")
        self.shader.AddStage(GL.GL_FRAGMENT_SHADER,
                             "spyke/graphics/shaderSources/particle.frag")
        self.shader.Compile()

        self.vao = VertexArray()
        self.vbo = VertexBuffer(RendererSettings.MaxQuadsCount * VERTEX_SIZE)

        self.vao.bind()
        self.vbo.bind()
        self.vao.ClearVertexOffset()
        self.vao.SetVertexSize(VERTEX_SIZE)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aPosition"), 2, GL.GL_FLOAT, False)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aSize"), 2, GL.GL_FLOAT, False)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aRotation"), 1, GL.GL_FLOAT, False)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aColor"), 4, GL.GL_FLOAT, False)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aTexCoord"), 2, GL.GL_FLOAT, False)
        self.vao.add_layout(self.shader.get_attrib_location(
            "aTexIdx"), 1, GL.GL_FLOAT, False)

        self.__vertexData = []
        self.__vertexCount = 0

        Debug.Log("Particle renderer initialized.", LogLevel.Info)

    def RenderParticle(self, pos: glm.vec3, size: glm.vec3, rot: glm.vec3, color: glm.vec4, texHandle):
        raise NotImplementedError()
        if RenderStats.quadsCount >= RendererSettings.MaxQuadsCount:
            self.__Flush()

        data = [
            pos.x, pos.y, pos.z,
            size.x, size.y, size.z,
            rot.x, rot.y, rot.z,
            color.x, color.y, color.z, color.w,
            texHandle.U, texHandle.V,
            texHandle.Index]

        self.__vertexData.extend(data)

        RenderStats.quadsCount += 1
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
        self.vao.bind()

        self.vbo.AddData(self.__vertexData, len(
            self.__vertexData) * _GL_FLOAT_SIZE)
        GL.glDrawArrays(GL.GL_POINTS, 0, self.__vertexCount)

        RenderStats.drawsCount += 1
        self.__vertexData.clear()
        self.__vertexCount = 0
