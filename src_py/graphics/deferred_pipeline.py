import logging

import numpy as np
from pygl import commands
from pygl import debug as gl_debug
from pygl import rendering, textures
from pygl.buffers import BindTarget, Buffer, BufferBaseTarget, BufferFlags
from pygl.commands import BlendEquation, BlendFactor, DepthFunc, EnableCap
from pygl.framebuffer import (Attachment, AttachmentFormat, Framebuffer,
                              RenderbufferAttachment, TextureAttachment)
from pygl.shaders import Shader, ShaderStage, ShaderType, UniformType
from pygl.vertex_array import (AttribType, VertexArray, VertexDescriptor,
                               VertexInput)

from spyke import _data, debug
from spyke.graphics.frame_data import FrameData
from spyke.graphics.pipeline import (GraphicsPipeline, PipelineInfo,
                                     PipelineSettings)


class DeferredPipeline(GraphicsPipeline):
    _CAMERA_MATRICES_BUFFER_BINDING = 0

    def __init__(self) -> None:
        self._geometry_shader: Shader
        self._geometry_vao: VertexArray
        self._instance_buffer: Buffer
        self._uniform_buffer: Buffer
        self._framebuffer: Framebuffer

        self._model_vertex_size = 0

    @debug.profiled('rendering', 'init')
    def initialize(self, settings: PipelineSettings, fb_width: int, fb_height: int) -> None:
        self._model_vertex_size = settings.model_vertex_size

        with debug.profiled_scope('create_buffers'):
            self._instance_buffer = Buffer(settings.instance_buffer_size, BufferFlags.DYNAMIC_STORAGE_BIT)
            gl_debug.set_object_name(self._instance_buffer, 'InstanceBuffer')

            self._uniform_buffer = Buffer(settings.uniform_buffer_size, BufferFlags.DYNAMIC_STORAGE_BIT)
            self._uniform_buffer.bind_base(BufferBaseTarget.UNIFORM_BUFFER, self._CAMERA_MATRICES_BUFFER_BINDING)
            gl_debug.set_object_name(self._uniform_buffer, 'UniformBuffer')

        with debug.profiled_scope('create_shaders'):
            self._geometry_shader = Shader([
                ShaderStage(ShaderType.VERTEX_SHADER, _data.get_package_data_file('shader_sources', 'deferred_geometry.vert')),
                ShaderStage(ShaderType.FRAGMENT_SHADER, _data.get_package_data_file('shader_sources', 'deferred_geometry.frag'))])
            self._geometry_shader.set_uniform_array('uTextures', np.arange(0, settings.max_textures_per_batch, dtype=np.int32), UniformType.INT)
            self._geometry_shader.set_uniform_block_binding('uCameraMatrices', self._CAMERA_MATRICES_BUFFER_BINDING)
            self._geometry_shader.validate()
            gl_debug.set_object_name(self._geometry_shader, 'DeferredGeometryShader')

        with debug.profiled_scope('create_vertex_arrays'):
            self._geometry_vao = VertexArray(
                layout=[
                    VertexInput(
                        buffer=None,
                        stride=settings.model_vertex_size,
                        descriptors=[
                            VertexDescriptor(self._geometry_shader.resources['aPosition'], AttribType.FLOAT, 3),
                            VertexDescriptor(self._geometry_shader.resources['aTexCoord'], AttribType.FLOAT, 2),
                            VertexDescriptor(self._geometry_shader.resources['aNormal'], AttribType.FLOAT, 3)]),
                    VertexInput(
                        buffer=self._instance_buffer,
                        stride=settings.instance_vertex_size,
                        descriptors=[
                            VertexDescriptor(self._geometry_shader.resources['aColor'], AttribType.FLOAT, 4),
                            VertexDescriptor(self._geometry_shader.resources['aTextureIndex'], AttribType.FLOAT, 1),
                            VertexDescriptor(self._geometry_shader.resources['aTransform'], AttribType.FLOAT, 4, 4)],
                        divisor=1)])
            gl_debug.set_object_name(self._geometry_vao, 'DeferredVAO')

        with debug.profiled_scope('create_framebuffer'):
            attachments: list[TextureAttachment | RenderbufferAttachment] = [
                TextureAttachment(0, 0, AttachmentFormat.RGBA8, 0), # diffuse
                TextureAttachment(0, 0, AttachmentFormat.RGB32F, 1, min_filter=textures.MinFilter.NEAREST, mag_filter=textures.MagFilter.NEAREST), # world pos
                TextureAttachment(0, 0, AttachmentFormat.RGB16F, 2, min_filter=textures.MinFilter.NEAREST, mag_filter=textures.MagFilter.NEAREST), # normal
                TextureAttachment(0, 0, AttachmentFormat.RG16F, 3, min_filter=textures.MinFilter.NEAREST, mag_filter=textures.MagFilter.NEAREST), # texture coords
                RenderbufferAttachment(0, 0, AttachmentFormat.DEPTH24_STENCIL8, Attachment.DEPTH_STENCIL_ATTACHMENT)]
            self._framebuffer = Framebuffer(attachments, fb_width, fb_height)
            gl_debug.set_object_name(self._framebuffer, 'DeferredFramebuffer')

        self._info = self._create_pipeline_info()

        _logger.info('Created deferred rendering pipeline.')

    def reset_buffers(self) -> None:
        self._instance_buffer.reset_offset()
        self._uniform_buffer.reset_offset()

    def get_output_texture_id(self) -> int:
        return self._framebuffer.get_attachment_id(0)

    @debug.profiled('rendering')
    def render(self, frame_data: FrameData) -> None:
        self._framebuffer.resize(frame_data.frame_width, frame_data.frame_height)

        commands.polygon_mode(commands.CullFace.FRONT_AND_BACK, frame_data.polygon_mode)
        commands.viewport(0, 0, self._framebuffer.width, self._framebuffer.height)

        with debug.profiled_scope('transfer_uniform_data'):
            self._uniform_buffer.store(frame_data.camera_view)
            self._uniform_buffer.store(frame_data.camera_projection)
            self._uniform_buffer.transfer()

        self._uniform_buffer.bind(BindTarget.UNIFORM_BUFFER)
        self._framebuffer.bind()

        self._execute_geometry_pass(frame_data)
        self._execute_light_pass()

        self._framebuffer.unbind()

    def destroy(self):
        self._geometry_shader.delete()
        self._geometry_vao.delete()
        self._instance_buffer.delete()
        self._framebuffer.delete()

    def _create_pipeline_info(self) -> PipelineInfo:
        buffers_size = self._instance_buffer.size + self._uniform_buffer.size

        diffuse_pixel_size = 4
        world_pos_pixel_size = 3 * 4
        normal_pixel_size = 3 * 2
        tex_coord_pixel_size = 3 * 2
        depth_stencil_pixel_size = 4
        attachments_size = self._framebuffer.width * self._framebuffer.height * (diffuse_pixel_size + world_pos_pixel_size + normal_pixel_size + tex_coord_pixel_size + depth_stencil_pixel_size)

        return PipelineInfo(buffers_size, attachments_size)

    @debug.profiled('rendering')
    def _execute_geometry_pass(self, frame_data: FrameData) -> None:
        commands.disable(EnableCap.BLEND)
        commands.enable(EnableCap.CULL_FACE)
        commands.cull_face(commands.CullFace.BACK)
        commands.enable(commands.EnableCap.DEPTH_TEST)
        commands.front_face(commands.FrontFace.CW)
        commands.depth_mask(True)

        commands.clear_color(
            frame_data.clear_color.r,
            frame_data.clear_color.g,
            frame_data.clear_color.b,
            frame_data.clear_color.a)
        rendering.clear(rendering.ClearMask.COLOR_BUFFER_BIT | rendering.ClearMask.DEPTH_BUFFER_BIT)

        self._geometry_vao.bind()
        self._geometry_shader.use()

        frame_data.white_texture.bind_to_unit(0)

        for model, batches in frame_data.batches.items():
            self._geometry_vao.bind_index_buffer(model.buffer)
            self._geometry_vao.bind_vertex_buffer(model.buffer, 0, self._model_vertex_size, model.vertex_offset)

            for batch in batches:
                with debug.profiled_scope('render_batch'):
                    with debug.profiled_scope('transfer_instance_data'):
                        self._instance_buffer.store(batch.instance_data[:batch.current_instance])
                        self._instance_buffer.transfer()

                    textures.bind_textures(batch.textures, first=1)
                    rendering.draw_elements_instanced(
                        batch.draw_mode,
                        model.index_count,
                        model.index_type,
                        batch.current_instance)

        commands.depth_mask(False)
        commands.disable(EnableCap.DEPTH_TEST)

    @debug.profiled('rendering')
    def _execute_light_pass(self) -> None:
        commands.enable(EnableCap.BLEND)
        commands.blend_equation(BlendEquation.FUNC_ADD)
        commands.blend_func(BlendFactor.SRC_ALPHA, BlendFactor.ONE_MINUS_SRC_ALPHA)

_logger = logging.getLogger(__name__)
