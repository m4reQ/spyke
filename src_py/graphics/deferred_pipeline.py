import logging

import numpy as np

from spyke import _data, debug
from spyke.graphics import gl, shader_cache
from spyke.graphics.frame_data import FrameData
from spyke.graphics.pipeline import (GraphicsPipeline, PipelineInfo,
                                     PipelineSettings)


class DeferredPipeline(GraphicsPipeline):
    _CAMERA_MATRICES_BUFFER_BINDING = 0
    _LIGHTS_BUFFER_BINDING = 1

    def __init__(self) -> None:
        super().__init__()

        self._geometry_shader: gl.ShaderProgram
        self._light_shader: gl.ShaderProgram
        self._post_process_shader: gl.ShaderProgram
        self._geometry_vao: gl.VertexArray
        self._empty_vao: gl.VertexArray
        self._instance_buffer: gl.Buffer
        self._camera_uniform_buffer: gl.Buffer
        self._lights_uniform_buffer: gl.Buffer
        self._framebuffer: gl.Framebuffer

        self._model_vertex_size = 0
        self._info = self._create_pipeline_info()

    @debug.profiled
    def initialize(self, settings: PipelineSettings, fb_width: int, fb_height: int) -> None:
        self._model_vertex_size = settings.model_vertex_size
        self._create_buffers(settings)
        self._create_shaders(settings)
        self._create_vaos(settings)
        self._create_framebuffer(fb_width, fb_height)

        self._info = self._create_pipeline_info()

        _logger.info('Created deferred rendering pipeline.')

    def reset_buffers(self) -> None:
        self._instance_buffer.reset_data_offset()
        self._camera_uniform_buffer.reset_data_offset()
        self._lights_uniform_buffer.reset_data_offset()

    def get_framebuffer_attachment_id(self, index: int) -> int:
        return self._framebuffer.get_attachment_id(index)

    @debug.profiled
    def execute(self, frame_data: FrameData) -> None:
        self._framebuffer.resize(frame_data.frame_width, frame_data.frame_height)
        self._framebuffer.bind()

        self._execute_geometry_pass(frame_data)
        self._execute_light_pass(frame_data)
        self._execute_post_process(frame_data)

    def destroy(self) -> None:
        self._geometry_shader.delete()
        self._light_shader.delete()
        self._post_process_shader.delete()
        self._geometry_vao.delete()
        self._empty_vao.delete()
        self._instance_buffer.delete()
        self._camera_uniform_buffer.delete()
        self._lights_uniform_buffer.delete()
        self._framebuffer.delete()

    @debug.profiled
    def _create_framebuffer(self, width: int, height: int) -> None:
        # 0: final
        # 1: albedo + specular
        # 2: world pos
        # 3: normal
        attachments = [
            gl.FramebufferAttachment(0, 0, gl.FramebufferAttachmentFormat.RGBA8, 0, min_filter=gl.MinFilter.NEAREST, mag_filter=gl.MagFilter.NEAREST),
            gl.FramebufferAttachment(0, 0, gl.FramebufferAttachmentFormat.RGBA8, 1, min_filter=gl.MinFilter.NEAREST, mag_filter=gl.MagFilter.NEAREST),
            gl.FramebufferAttachment(0, 0, gl.FramebufferAttachmentFormat.RGB16F, 2, min_filter=gl.MinFilter.NEAREST, mag_filter=gl.MagFilter.NEAREST),
            gl.FramebufferAttachment(0, 0, gl.FramebufferAttachmentFormat.RGB16F, 3, min_filter=gl.MinFilter.NEAREST, mag_filter=gl.MagFilter.NEAREST),
            gl.FramebufferAttachment(0, 0, gl.FramebufferAttachmentFormat.DEPTH24_STENCIL8, gl.FramebufferAttachmentPoint.DEPTH_STENCIL_ATTACHMENT, use_renderbuffer=True)]
        self._framebuffer = gl.Framebuffer(attachments, width, height)
        self._framebuffer.set_debug_name('DeferredFramebuffer')

    @debug.profiled
    def _create_shaders(self, settings: PipelineSettings) -> None:
        cache = shader_cache.get()
        with debug.profiled_scope('create_geometry_shader'):
            self._geometry_shader = cache.load_cached_program_or_create(
                'deferred_geometry_shader',
                [gl.ShaderStageInfo.from_file(gl.ShaderType.VERTEX_SHADER, _data.get_package_data_file('data', 'shaders', 'deferred_geometry.vert')),
                 gl.ShaderStageInfo.from_file(gl.ShaderType.FRAGMENT_SHADER, _data.get_package_data_file('data', 'shaders', 'deferred_geometry.frag'))])
            self._geometry_shader.set_uniform_array('uTextures', np.arange(0, settings.max_textures_per_batch, dtype=np.int32), gl.UniformType.INT)
            self._geometry_shader.set_uniform_block_binding('uCameraMatrices', self._CAMERA_MATRICES_BUFFER_BINDING)
            self._geometry_shader.validate()
            self._geometry_shader.set_debug_name('DeferredGeometryShader')

        with debug.profiled_scope('create_light_shader'):
            self._light_shader = cache.load_cached_program_or_create(
                'deferred_light_shader',
                [gl.ShaderStageInfo.from_file(gl.ShaderType.VERTEX_SHADER, _data.get_package_data_file('data', 'shaders', 'deferred_lighting.vert')),
                 gl.ShaderStageInfo.from_file(gl.ShaderType.FRAGMENT_SHADER, _data.get_package_data_file('data', 'shaders', 'deferred_lighting.frag'))])
            self._light_shader.set_uniform_block_binding('uLights', self._LIGHTS_BUFFER_BINDING)
            self._light_shader.validate()
            self._light_shader.set_debug_name('DeferredLightingShader')

        with debug.profiled_scope('create_post_process_shader'):
            self._post_process_shader = cache.load_cached_program_or_create(
                'post_process_shader',
                [gl.ShaderStageInfo.from_file(gl.ShaderType.VERTEX_SHADER, _data.get_package_data_file('data', 'shaders', 'post.vert')),
                 gl.ShaderStageInfo.from_file(gl.ShaderType.FRAGMENT_SHADER, _data.get_package_data_file('data', 'shaders', 'post.frag'))])
            self._post_process_shader.set_uniform('uFramebufferTexture', 0, gl.UniformType.INT)
            self._post_process_shader.validate()
            self._post_process_shader.set_debug_name('PostProcessShader')

    @debug.profiled
    def _create_vaos(self, settings: PipelineSettings) -> None:
        self._geometry_vao = gl.VertexArray(
            layout=[
                gl.VertexInput(
                    buffer=None,
                    stride=settings.model_vertex_size,
                    descriptors=[
                        gl.VertexDescriptor(self._geometry_shader.attributes['aPosition'], gl.VertexAttribType.FLOAT, 3),
                        gl.VertexDescriptor(self._geometry_shader.attributes['aTexCoord'], gl.VertexAttribType.FLOAT, 2),
                        gl.VertexDescriptor(self._geometry_shader.attributes['aNormal'], gl.VertexAttribType.FLOAT, 3)]),
                gl.VertexInput(
                    buffer=self._instance_buffer,
                    stride=settings.instance_vertex_size,
                    descriptors=[
                        gl.VertexDescriptor(self._geometry_shader.attributes['aColor'], gl.VertexAttribType.FLOAT, 4),
                        gl.VertexDescriptor(self._geometry_shader.attributes['aAlbedoTextureIndex'], gl.VertexAttribType.FLOAT, 1),
                        gl.VertexDescriptor(self._geometry_shader.attributes['aSpecularTextureIndex'], gl.VertexAttribType.FLOAT, 1),
                        gl.VertexDescriptor(self._geometry_shader.attributes['aTransform'], gl.VertexAttribType.FLOAT, 4, 4)],
                    divisor=1)])
        self._geometry_vao.set_debug_name('DeferredGeometryVAO')

        self._empty_vao = gl.VertexArray([])
        self._empty_vao.set_debug_name('DeferredEmptyVAO')

    @debug.profiled
    def _create_buffers(self, settings: PipelineSettings) -> None:
        self._instance_buffer = gl.Buffer(settings.instance_buffer_size, gl.BufferFlag.MAP_WRITE_BIT | gl.BufferFlag.MAP_PERSISTENT_BIT)
        self._instance_buffer.set_debug_name('InstanceBuffer')

        self._camera_uniform_buffer = gl.Buffer(settings.uniform_buffer_size, gl.BufferFlag.MAP_WRITE_BIT | gl.BufferFlag.MAP_PERSISTENT_BIT)
        self._camera_uniform_buffer.bind_base(gl.BufferBaseTarget.UNIFORM_BUFFER, self._CAMERA_MATRICES_BUFFER_BINDING)
        self._camera_uniform_buffer.set_debug_name('CameraUniformBuffer')

        self._lights_uniform_buffer = gl.Buffer(settings.max_lights * settings.light_data_size, gl.BufferFlag.MAP_WRITE_BIT | gl.BufferFlag.MAP_PERSISTENT_BIT)
        self._lights_uniform_buffer.bind_base(gl.BufferBaseTarget.UNIFORM_BUFFER, self._LIGHTS_BUFFER_BINDING)
        self._lights_uniform_buffer.set_debug_name('LightsUniformBuffer')

    def _create_pipeline_info(self) -> PipelineInfo:
        framebuffer_attachments = {
            'default': 0,
            'albedo': 1,
            'world_pos': 2,
            'normal': 3}

        return PipelineInfo(0, 0, framebuffer_attachments)

    @debug.profiled
    def _execute_geometry_pass(self, frame_data: FrameData) -> None:
        with debug.profiled_scope('transfer_uniform_data'):
            self._camera_uniform_buffer.write(frame_data.camera_view)
            self._camera_uniform_buffer.write(frame_data.camera_projection)
            self._camera_uniform_buffer.transfer()

        gl.polygon_mode(gl.CullFace.FRONT_AND_BACK, frame_data.polygon_mode)
        gl.front_face(gl.FrontFace.CW)
        gl.disable(gl.EnableCap.BLEND)
        gl.enable(gl.EnableCap.CULL_FACE)
        gl.cull_face(gl.CullFace.FRONT)
        gl.enable(gl.EnableCap.DEPTH_TEST)
        gl.depth_mask(True)

        gl.scissor(0, 0, self._framebuffer.width, self._framebuffer.height)
        gl.viewport(0, 0, self._framebuffer.width, self._framebuffer.height)

        # TODO Allow passing Vector4 to commands.clear_color
        gl.clear_color(*frame_data.clear_color)
        gl.clear(gl.ClearMask.COLOR_BUFFER_BIT | gl.ClearMask.DEPTH_BUFFER_BIT)

        self._geometry_vao.bind()
        self._geometry_shader.use()
        self._camera_uniform_buffer.bind(gl.BufferTarget.UNIFORM_BUFFER)
        frame_data.white_texture.bind_to_unit(0)

        for model, batches in frame_data.batches.items():
            self._geometry_vao.bind_index_buffer(model.buffer)
            self._geometry_vao.bind_vertex_buffer(model.buffer, 0, self._model_vertex_size, model.vertex_offset)

            for batch in batches:
                with debug.profiled_scope('render_batch'):
                    with debug.profiled_scope('transfer_instance_data'):
                        self._instance_buffer.write(batch.instance_data[:batch.current_instance])
                        self._instance_buffer.transfer()

                    gl.bind_textures(batch.textures, first=1)
                    gl.draw_elements_instanced(
                        batch.draw_mode,
                        model.index_count,
                        model.index_type,
                        batch.current_instance)

    @debug.profiled
    def _execute_light_pass(self, frame_data: FrameData) -> None:
        gl.polygon_mode(gl.CullFace.FRONT_AND_BACK, gl.PolygonMode.FILL)
        gl.front_face(gl.FrontFace.CW)
        gl.disable(gl.EnableCap.CULL_FACE)
        gl.disable(gl.EnableCap.DEPTH_TEST)
        gl.depth_mask(False)

        for light in frame_data.lights:
            self._lights_uniform_buffer.write(light.color.x)
            self._lights_uniform_buffer.write(light.color.y)
            self._lights_uniform_buffer.write(light.color.z)
            self._lights_uniform_buffer.write(light.intensity)
            self._lights_uniform_buffer.write(light.position)
            self._lights_uniform_buffer.write(0) # padding

        self._lights_uniform_buffer.transfer()
        self._lights_uniform_buffer.bind(gl.BufferTarget.UNIFORM_BUFFER)

        self._light_shader.set_uniform('uLightsCount', len(frame_data.lights), gl.UniformType.UNSIGNED_INT)
        # TODO Allow passing vectors to set_uniform_vec* methods
        self._light_shader.set_uniform_vec3('uViewPos', gl.UniformType.FLOAT, frame_data.camera_pos.x, frame_data.camera_pos.y, frame_data.camera_pos.z)
        self._light_shader.use()

        self._empty_vao.bind()

        attachment_ids = [
            self._framebuffer.get_attachment_id(3),
            self._framebuffer.get_attachment_id(2),
            self._framebuffer.get_attachment_id(1)]
        gl.bind_texture_ids(attachment_ids, 1)
        gl.draw_arrays(gl.DrawMode.TRIANGLES, 0, 6)

    def _execute_post_process(self, frame_data: FrameData) -> None:
        self._framebuffer.unbind()
        self._empty_vao.bind()

        gl.bind_texture_id(self._framebuffer.get_attachment_id(0), 0)
        gl.draw_arrays(gl.DrawMode.TRIANGLES, 0, 6)

_logger = logging.getLogger(__name__)
