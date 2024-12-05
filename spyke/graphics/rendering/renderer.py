import ctypes as ct
import logging
import os

import glm
import numpy as np

import pygl
from pygl import buffers, commands
from pygl import debug as gl_debug
from pygl import framebuffer, rendering, shaders, textures, vertex_array
from spyke import debug, paths
from spyke.graphics.texture_buffer import TextureBuffer
from spyke.resources import Font, Model
from spyke.utils import once

# from OpenGL.GL.INTEL.framebuffer_CMAA import glApplyFramebufferAttachmentCMAAINTEL

# TODO: Restore particle rendering

# framebuffer_spec.samples = 1 if context.has_extension('GL_INTEL_framebuffer_CMAA') else 2

# @debug.profiled('graphics', 'rendering')
# def render_scene(scene: Scene) -> None:
#     assert _is_initialized, 'Renderer not initialized.'
#     # self.info.reset_frame_stats()
#     # TODO: Decide if we really want to measure draw time even without performing glFlush
#     start = time.perf_counter()

#     primary_camera = None
#     for _, camera in scene.get_component(components.CameraComponent):
#         if camera.is_primary:
#             primary_camera = camera

#     if not primary_camera:
#         view_projection = glm.mat4(1.0)
#     else:
#         view_projection = primary_camera.view_projection

#     _uniform_buffer.store_direct(view_projection)

#     BufferBase.bind_ubo(_uniform_buffer)

#     # self.framebuffer.bind()

#     clear_screen()

#     GL.glPolygonMode(GL.GL_FRONT_AND_BACK, _polygon_mode_iterator.current)
#     GL.glEnable(GL.GL_DEPTH_TEST)

#     _render_objects(scene)
#     _flush()

#     GL.glDisable(GL.GL_DEPTH_TEST)

#     _render_text(scene)
#     _flush()

#     # TODO: Reimplement particle renderer
#     # for _, system in scene.GetComponent(components.ParticleSystemComponent):
#     # 	for particle in system.particlePool:
#     # 		if particle.isAlive:
#     # 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

#     # TODO: Implement rendering of multisampled framebuffer
#     # if self.info.extension_present('GL_INTEL_framebuffer_CMAA'):
#     # self.framebuffer.unbind()

#     # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
#     # GL.glViewport(0, 0, self.info.window_width, self.info.window_height)

#     # self.clear_screen()

#     # self._render_quad(glm.mat4(1.0), glm.vec4(1.0), glm.vec2(
#     #     1.0), self.framebuffer.get_color_attachment(0))
#     # self._flush()

#     # if self.info.vendor == Vendor.Nvidia:
#     #     self.info.video_memory_used = self.info.video_memory_available - \
#     #         GL.glGetInteger(NvidiaIntegerName.GpuMemInfoCurrentAvailable)

#     # self.info.drawtime = time.perf_counter() - start

# @debug.profiled('graphics', 'rendering')
# def _render_text(scene: esper.World) -> None:
#     text_transform = glm.mat4(1.0)

#     fb_width = _framebuffer.width
#     fb_height = _framebuffer.height

#     for ent, (text, transform) in scene.get_components(components.TextComponent, components.TransformComponent):
#         font: Font = resources.get(text.font_id, Font) # type: ignore
#         if not font.is_loaded:
#             continue

#         scale = text.size / font.base_size

#         x = transform.position.x
#         y = transform.position.y

#         for char in text.text:
#             glyph = font.get_glyph(char)

#             # TODO: Normalize all values here
#             pos_x = x + ((glyph.bearing.x / fb_height) * scale)
#             pos_y = y - (((glyph.size.y - glyph.bearing.y) / fb_height) * scale)

#             width = glyph.size.x / fb_width * scale
#             height = glyph.size.y / fb_height * scale

#             x += glyph.advance / fb_width * scale

#             text_transform[3, 0] = pos_x
#             text_transform[3, 1] = pos_y
#             text_transform[3, 2] = transform.position.z
#             text_transform[0, 0] = width
#             text_transform[1, 1] = height

#             _render(RenderCommand(
#                 font.texture.id,
#                 Model.quad,
#                 text_transform,
#                 text.color,
#                 glm.vec2(1.0),
#                 ent,
#                 glyph.tex_rect.to_coordinates()))

_DEFAULT_FB_SIZE = (1080, 720)

_MAX_MODEL_VERTICES = 2000
_MODEL_VERTEX_COUNT = 3 + 2
_MAX_INSTANCES = 500
_INSTANCE_VERTEX_COUNT = 4 + 1 + 1 + 16

_UNIFORM_BLOCK_COUNT = 16
_UNIFORM_BLOCK_BINDING = 0

_MAX_TEXTURES = 16

_TEXT_TEX_COORDS_BINDING = 15

_QUAD_VERTICES = np.array(
    [0.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 0.0],
    dtype=np.float32)

@debug.profiled('graphics', 'rendering')
def _create_shaders() -> None:
    global _basic_shader, _text_shader

    basic_shader_stages = [
        shaders.ShaderStage(shaders.ShaderType.VERTEX_SHADER, os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.vert')),
        shaders.ShaderStage(shaders.ShaderType.FRAGMENT_SHADER, os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.frag'))]
    _basic_shader = shaders.Shader(basic_shader_stages)
    _basic_shader.set_uniform_array('uTextures', np.arange(_MAX_TEXTURES, dtype=np.int32), shaders.UniformType.INT)
    _basic_shader.set_uniform_block_binding('uMatrices', _UNIFORM_BLOCK_BINDING)
    _basic_shader.validate()

    text_shader_stages = [
        shaders.ShaderStage(shaders.ShaderType.VERTEX_SHADER, os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'text.vert')),
        shaders.ShaderStage(shaders.ShaderType.FRAGMENT_SHADER, os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'text.frag'))]
    _text_shader = shaders.Shader(text_shader_stages)
    _text_shader.set_uniform_array('uTextures', np.arange(_MAX_TEXTURES - 1, dtype=np.int32), shaders.UniformType.INT)
    _text_shader.set_uniform_block_binding('uMatrices', _UNIFORM_BLOCK_BINDING)
    _text_shader.set_uniform('uTexCoordsBuffer', _TEXT_TEX_COORDS_BINDING, shaders.UniformType.INT)
    _text_shader.validate()

@debug.profiled('graphics', 'rendering')
def _create_buffers() -> None:
    global _model_data_buffer, _instance_data_buffer, _uniform_buffer, _text_tex_coords_buffer

    _model_data_buffer = buffers.Buffer(_MAX_MODEL_VERTICES * _MODEL_VERTEX_COUNT * ct.sizeof(ct.c_float), buffers.BufferFlags.DYNAMIC_STORAGE_BIT)
    _instance_data_buffer = buffers.Buffer(_MAX_INSTANCES * _INSTANCE_VERTEX_COUNT * ct.sizeof(ct.c_float), buffers.BufferFlags.DYNAMIC_STORAGE_BIT)

    _uniform_buffer = buffers.Buffer(_UNIFORM_BLOCK_COUNT * ct.sizeof(ct.c_float), buffers.BufferFlags.DYNAMIC_STORAGE_BIT)
    _uniform_buffer.bind_base(buffers.BufferBaseTarget.UNIFORM_BUFFER, _UNIFORM_BLOCK_BINDING)

    _text_tex_coords_buffer = TextureBuffer(_MAX_INSTANCES * 6, textures.InternalFormat.RG32F, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)

@debug.profiled('graphics', 'rendering')
def _create_vertex_arrays() -> None:
    global _basic_vertex_array, _text_vertex_array

    basic_layout = [
        vertex_array.VertexInput(
            buffer=_model_data_buffer,
            stride=_MODEL_VERTEX_COUNT * ct.sizeof(ct.c_float),
            descriptors=[
                vertex_array.VertexDescriptor(_basic_shader.resources['aPosition'], vertex_array.AttribType.FLOAT, 3),
                vertex_array.VertexDescriptor(_basic_shader.resources['aTexCoord'], vertex_array.AttribType.FLOAT, 2)]),
        vertex_array.VertexInput(
            buffer=_instance_data_buffer,
            stride=_INSTANCE_VERTEX_COUNT * ct.sizeof(ct.c_float),
            descriptors=[
                vertex_array.VertexDescriptor(_basic_shader.resources['aColor'], vertex_array.AttribType.FLOAT, 4),
                vertex_array.VertexDescriptor(_basic_shader.resources['aTexIdx'], vertex_array.AttribType.FLOAT, 1),
                vertex_array.VertexDescriptor(_basic_shader.resources['aEntId'], vertex_array.AttribType.FLOAT, 1),
                vertex_array.VertexDescriptor(_basic_shader.resources['aTransform'], vertex_array.AttribType.FLOAT, 4, 4)],
            divisor=1)]
    _basic_vertex_array = vertex_array.VertexArray(basic_layout)

    text_layout = [
        vertex_array.VertexInput(
            buffer=_model_data_buffer,
            stride=3 * ct.sizeof(ct.c_float),
            descriptors=[
                vertex_array.VertexDescriptor(_text_shader.resources['aPosition'], vertex_array.AttribType.FLOAT, 3)]),
        vertex_array.VertexInput(
            buffer=_instance_data_buffer,
            stride=_INSTANCE_VERTEX_COUNT * ct.sizeof(ct.c_float),
            descriptors=[
                vertex_array.VertexDescriptor(_text_shader.resources['aColor'], vertex_array.AttribType.FLOAT, 4),
                vertex_array.VertexDescriptor(_text_shader.resources['aTexIdx'], vertex_array.AttribType.FLOAT, 1),
                vertex_array.VertexDescriptor(_text_shader.resources['aEntId'], vertex_array.AttribType.FLOAT, 1),
                vertex_array.VertexDescriptor(_text_shader.resources['aTransform'], vertex_array.AttribType.FLOAT, 4, 4)],
            divisor=1)]
    _text_vertex_array = vertex_array.VertexArray(text_layout)

@debug.profiled('graphics', 'rendering')
def _create_white_texture() -> None:
    global _white_texture

    _white_texture = textures.Texture(
        textures.TextureSpec(
            textures.TextureTarget.TEXTURE_2D,
            1,
            1,
            textures.InternalFormat.RGBA8,
            min_filter=textures.MinFilter.NEAREST,
            mag_filter=textures.MagFilter.NEAREST))
    _white_texture.upload(
        textures.UploadInfo(textures.PixelFormat.RGBA, 1, 1),
        np.array([255, 255, 255, 255], np.uint8))

@debug.profiled('graphics', 'rendering')
def _create_framebuffer(width: int, height: int) -> None:
    global _framebuffer

    attachments = [
        framebuffer.RenderbufferAttachment(width, height, framebuffer.AttachmentFormat.RGBA8, 0),
        framebuffer.RenderbufferAttachment(width, height, framebuffer.AttachmentFormat.DEPTH24_STENCIL8, framebuffer.Attachment.DEPTH_STENCIL_ATTACHMENT)]
    _framebuffer = framebuffer.Framebuffer(attachments, width, height)

@once
def initialize(window_size: tuple[int, int]) -> None:
    pygl.init()

    if __debug__:
        _enable_debug_output()

    _setup_opengl_state(*window_size)
    _create_shaders()
    _create_buffers()
    _create_vertex_arrays()
    _create_white_texture()
    _create_framebuffer(*window_size)

    _logger.info('Renderer initialized.')

@debug.profiled('graphics', 'rendering')
def shutdown() -> None:
    _basic_shader.delete()
    _text_shader.delete()
    _basic_vertex_array.delete()
    _text_vertex_array.delete()
    _model_data_buffer.delete()
    _instance_data_buffer.delete()
    _uniform_buffer.delete()
    _white_texture.delete()
    _text_tex_coords_buffer.delete()
    _framebuffer.delete()

def set_clear_color(r: float, g: float, b: float, a: float = 1.0) -> None:
    '''
    Sets background color of the window.

    @r: Red component of the color.
    @g: Green component of the color.
    @b: Blue component of the color.
    @a: Alpha component of the color.
    '''

    commands.clear_color(r, g, b, a)

@debug.profiled('graphics', 'rendering')
def resize(width: int, height: int) -> None:
    commands.viewport(0, 0, width, height)
    commands.scissor(0, 0, width, height)

    _framebuffer.resize(width, height)

    _logger.info('Viewport size set to %d, %d.', width, height)

@debug.profiled('graphics', 'rendering')
def clear() -> None:
    '''
    Clears the screen.
    '''

    rendering.clear(rendering.ClearMask.COLOR_BUFFER_BIT | rendering.ClearMask.DEPTH_BUFFER_BIT)

@debug.profiled('graphics', 'rendering')
def render(color: glm.vec4, transform: glm.mat4, entity_id: int = 0, texture: textures.Texture | None = None) -> None:
    '''
    Renders instance of the currently set models with given parameters.
    NOTE: This function is not thread-safe.

    @color: Color of the rendered instance.
    @transform: Determines where in the scene should the instance be drawn.
    @entity_id: Used when running with imgui on, to determine entity given its position on the screen.
    @texture: Texture to apply on the rendered instance. If `None` instance will be rendered with flat color.
    '''

    global _instance_count

    if _should_flush(1):
        _flush()

    _instance_data_buffer.store(color)
    _instance_data_buffer.store(float(_get_texture_index(texture)))
    _instance_data_buffer.store(entity_id)
    _instance_data_buffer.store(transform)

    _instance_count += 1

@debug.profiled('graphics', 'rendering')
def render_text(text: str, pos: glm.vec3, color: glm.vec4, size: int, font: Font, entity_id: int = 0) -> None:
    global _instance_count

    v_width, v_height = _framebuffer.size
    x = pos.x
    y = pos.y
    # TODO: use points to pixels translation
    scale = size / v_height

    tex_idx = _get_texture_index(font.texture)
    transform = glm.mat4(1.0)

    for char in text:
        if _should_flush(2):
            _flush_text()

        glyph = font.get_glyph(char)

        # TODO: Normalize all values here
        pos_x = x + ((glyph.bearing.x / v_width) * scale)
        pos_y = y - (((glyph.size.y - glyph.bearing.y) / v_height) * scale)

        width = glyph.size.x / v_width * scale
        height = glyph.size.y / v_height * scale

        x += glyph.advance / v_width * scale

        transform[3, 0] = pos_x
        transform[3, 1] = pos_y
        transform[3, 2] = pos.z
        transform[0, 0] = width
        transform[1, 1] = height

        _instance_data_buffer.store(color)
        _instance_data_buffer.store(float(tex_idx))
        _instance_data_buffer.store(float(entity_id))
        _instance_data_buffer.store(transform)

        _text_tex_coords_buffer.store(glyph.tex_coords)

        _instance_count += 1

@debug.profiled('graphics', 'rendering')
def begin_batch(model: Model, view_projection: glm.mat4 = glm.mat4(1.0)) -> None:
    global _current_vertex_count

    _model_data_buffer.store(model.data)
    _model_data_buffer.transfer()

    _uniform_buffer.store(view_projection)
    _uniform_buffer.transfer()
    _uniform_buffer.bind(buffers.BindTarget.UNIFORM_BUFFER)

    _basic_shader.use()
    _basic_vertex_array.bind()

    _current_vertex_count = model.vertex_count

@debug.profiled('graphics', 'rendering')
def begin_text(view_projection: glm.mat4 = glm.mat4(1.0)) -> None:
    global _current_vertex_count

    _model_data_buffer.store(_QUAD_VERTICES)
    _model_data_buffer.transfer()

    _uniform_buffer.store(view_projection)
    _uniform_buffer.transfer()
    _uniform_buffer.bind(buffers.BindTarget.UNIFORM_BUFFER)

    _text_shader.use()
    _text_vertex_array.bind()

    _current_vertex_count = 6

def end_text() -> None:
    _flush_text()

def end_batch() -> None:
    _flush()

def _get_texture_index(texture: textures.Texture | None) -> int:
    if texture is None:
        return 0

    if texture in _textures:
        return _textures.index(texture) + 1

    _textures.append(texture)
    return len(_textures)

@debug.profiled('graphics', 'rendering')
def _flush() -> None:
    global _instance_count

    _white_texture.bind_to_unit(0)
    textures.bind_textures(_textures, 1)

    _instance_data_buffer.transfer()

    rendering.draw_arrays_instanced(
        rendering.DrawMode.TRIANGLES,
        0,
        _current_vertex_count * _instance_count,
        _instance_count)

    _textures.clear()
    _instance_count = 0

@debug.profiled('graphics', 'rendering')
def _flush_text() -> None:
    _text_tex_coords_buffer.transfer()
    _text_tex_coords_buffer.bind(_TEXT_TEX_COORDS_BINDING)

    _flush()

def _opengl_debug_callback(source: int, msg_type: int, id: int, severity: int, msg: str, _) -> None:
    _source = gl_debug.DebugSource(source).name.upper()
    _msg_type = gl_debug.DebugType(msg_type).name.upper()

    message_formatted = f'OpenGL {_source} -> {_msg_type}: {msg}.'

    if severity == gl_debug.DebugSeverity.DEBUG_SEVERITY_HIGH:
        _logger.error(message_formatted)
    elif severity == gl_debug.DebugSeverity.DEBUG_SEVERITY_MEDIUM:
        _logger.warning(message_formatted)
    elif severity in (gl_debug.DebugSeverity.DEBUG_SEVERITY_LOW, gl_debug.DebugSeverity.DEBUG_SEVERITY_NOTIFICATION):
        _logger.info(message_formatted)

@debug.profiled('graphics', 'setup')
def _enable_debug_output():
    gl_debug.enable(_opengl_debug_callback)
    gl_debug.insert_message(
        gl_debug.DebugSource.DEBUG_SOURCE_APPLICATION,
        gl_debug.DebugType.DEBUG_TYPE_OTHER,
        2137,
        gl_debug.DebugSeverity.DEBUG_SEVERITY_NOTIFICATION,
        'Testing OpenGL debug output..')

@debug.profiled('graphics', 'setup')
def _setup_opengl_state(width: int, height: int) -> None:
    commands.enable(commands.EnableCap.MULTISAMPLE)
    commands.enable(commands.EnableCap.DEPTH_TEST)
    commands.enable(commands.EnableCap.BLEND)
    commands.enable(commands.EnableCap.LINE_SMOOTH)

    commands.viewport(0, 0, width, height)
    commands.scissor(0, 0, width, height)

    commands.clear_color(0.0, 0.0, 0.0, 1.0)
    commands.hint(commands.HintTarget.TEXTURE_COMPRESSION_HINT, commands.HintValue.NICEST)
    commands.blend_func(commands.BlendFactor.SRC_ALPHA, commands.BlendFactor.ONE_MINUS_SRC_ALPHA)
    commands.depth_func(commands.DepthFunc.LEQUAL)
    commands.cull_face(commands.CullFace.FRONT)
    commands.front_face(commands.FrontFace.CW)
    commands.polygon_mode(commands.CullFace.FRONT_AND_BACK, commands.PolygonMode.FILL)
    commands.point_size(4.0)

def _should_flush(textures_reserved: int) -> bool:
    return _instance_count >= _MAX_INSTANCES or len(_textures) >= _MAX_TEXTURES - textures_reserved

_logger = logging.getLogger(__name__)

_textures = list[textures.Texture]()
_instance_count = 0
_current_vertex_count = 0

_basic_shader: shaders.Shader
_text_shader: shaders.Shader
_model_data_buffer: buffers.Buffer
_instance_data_buffer: buffers.Buffer
_uniform_buffer: buffers.Buffer
_basic_vertex_array: vertex_array.VertexArray
_text_vertex_array: vertex_array.VertexArray
_white_texture: textures.Texture
_text_tex_coords_buffer: TextureBuffer
_framebuffer: framebuffer.Framebuffer
