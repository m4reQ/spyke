import logging
import os
import time
import typing as t
from concurrent import futures

import glm
import numpy as np
from OpenGL import GL
from PIL import Image
from spyke import debug, events, exceptions, paths
from spyke.enums import (ClearMask, DebugSeverity, DebugSource, DebugType,
                         GLType, Key, MagFilter, MinFilter, ShaderType,
                         SizedInternalFormat, TextureFormat)
from spyke.graphics.buffers import AttachmentSpec, DynamicBuffer, Framebuffer
from spyke.graphics.shader import Shader
from spyke.graphics.textures import (Texture2D, TextureBase, TextureSpec,
                                     TextureUploadData)
from spyke.graphics.vertex_array import VertexArray
from spyke.resources import Model

# from OpenGL.GL.INTEL.framebuffer_CMAA import glApplyFramebufferAttachmentCMAAINTEL

# TODO: Restore particle rendering
# TODO: Remove unnecessary constants

# color_attachment_spec = AttachmentSpec(SizedInternalFormat.Rgba8)
# entity_id_attachment_spec = AttachmentSpec(
#     SizedInternalFormat.R8i,
#     MinFilter.Nearest,
#     MagFilter.Nearest)
# depth_attachment_spec = AttachmentSpec(
#     SizedInternalFormat.Depth24Stencil8,
#     MinFilter.Nearest,
#     MagFilter.Nearest)

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

_SIZEOF_FLOAT = np.dtype(np.float32).itemsize

_BASIC_SHADER_SPEC = {
    ShaderType.VertexShader: os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.vert'),
    ShaderType.FragmentShader: os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.frag')}

_MAX_MODEL_VERTICES = 2000
_MODEL_VERTEX_COUNT = 3 + 2
_MAX_INSTANCES = 500
_INSTANCE_VERTEX_COUNT = 4 + 1 + 1 + 16

_MODEL_DATA_BUFFER_BINDING = 0
_INSTANCE_DATA_BUFFER_BINDING = 1

_UNIFORM_BLOCK_COUNT = 16
_UNIFORM_BLOCK_BINDING = 0

_MAX_TEXTURES = 16

@t.final
class Renderer:
    @debug.profiled('graphics', 'initialization')
    def __init__(self, window_size: tuple[int, int]) -> None:
        self._debug_proc = GL.GLDEBUGPROC(_opengl_debug_callback)
        _enable_debug_output(self._debug_proc)
        _setup_opengl_state()

        self._basic_shader = Shader.create(_BASIC_SHADER_SPEC)
        self._model_data_buffer = DynamicBuffer(_MAX_MODEL_VERTICES * _MODEL_VERTEX_COUNT)
        self._instance_data_buffer = DynamicBuffer(_MAX_INSTANCES * _INSTANCE_VERTEX_COUNT)
        self._uniform_buffer = DynamicBuffer(_UNIFORM_BLOCK_COUNT)
        self._vertex_array = VertexArray()
        self._white_texture = Texture2D(
            TextureSpec(
                1,
                1,
                SizedInternalFormat.Rgba8,
                mipmaps = 1,
                min_filter = MinFilter.Nearest,
                mag_filter = MagFilter.Nearest))
        self._framebuffer = Framebuffer([AttachmentSpec(*window_size, SizedInternalFormat.Rgba8, MinFilter.Linear)])

        self._current_model: Model | None = None
        self._textures: list[TextureBase] = []
        self._instance_count = 0

        self._basic_shader.set_uniform_array('uTextures', list(range(_MAX_TEXTURES)))
        self._basic_shader.set_uniform_block_binding('uMatrices', _UNIFORM_BLOCK_BINDING)
        self._basic_shader.validate()

        self._setup_vertex_array()

        self._white_texture.upload(
            TextureUploadData(
                1,
                1,
                np.array([255, 255, 255, 255], dtype=np.ubyte),
                TextureFormat.Rgba))

        self._uniform_buffer.bind_to_uniform(_UNIFORM_BLOCK_BINDING)

        events.register(self._resize_callback, events.ResizeEvent, priority=-1)
        events.register(self._key_down_callback, events.KeyDownEvent, priority=-1)

        self._resize(*window_size)

        _logger.info('Renderer initialized.')

    @debug.profiled('graphics', 'rendering')
    def clear(self) -> None:
        '''
        Clears the screen.
        '''

        GL.glClear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)

    def set_clear_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        '''
        Sets background color of the window.

        @r: Red component of the color.
        @g: Green component of the color.
        @b: Blue component of the color.
        @a: Alpha component of the color.
        '''

        GL.glClearColor(r, g, b, a)

    @debug.profiled('graphics', 'rendering')
    def render(self, color: glm.vec4, transform: glm.mat4, entity_id: int = 0, texture: TextureBase | None = None) -> None:
        '''
        Renders instance of the currently set models with given parameters.
        NOTE: This function is not thread-safe.

        @color: Color of the rendered instance.
        @transform: Determines where in the scene should the instance be drawn.
        @entity_id: Used when running with imgui on, to determine entity given its position on the screen.
        @texture: Texture to apply on the rendered instance. If `None` instance will be rendered with flat color.
        '''

        if self._instance_count >= _MAX_INSTANCES or len(self._textures) >= _MAX_TEXTURES - 1:
            self._flush()

        self._instance_data_buffer.store(
            np.array(
                [*color,
                self._get_texture_index(texture),
                entity_id],
                dtype = np.float32))
        self._instance_data_buffer.store(transform)

        self._instance_count += 1

    def begin_batch(self, model: Model, view_projection: glm.mat4 = glm.mat4(1.0)) -> None:
        self._current_model = model

        self._uniform_buffer.store(view_projection)
        self._uniform_buffer.bind_ubo()

    def end_batch(self) -> None:
        if self._instance_count == 0:
            _logger.warning('end_batch called with an empty batch. No objects will be rendered.')
            return

        self._flush()

    @debug.profiled('graphics')
    def capture_frame(self) -> None:
        pixels = self._framebuffer.read_color_attachment(0, TextureFormat.Rgb)
        _screenshot_save_executor.submit(_save_screenshot, pixels, self._framebuffer.size)

    def _get_texture_index(self, texture):
        if texture is None:
            return 0

        if texture in self._textures:
            return self._textures.index(texture) + 1

        self._textures.append(texture)
        return len(self._textures)

    @debug.profiled('graphics', 'setup')
    def _setup_vertex_array(self) -> None:
        self._vertex_array.bind_vertex_buffer(_MODEL_DATA_BUFFER_BINDING, self._model_data_buffer, 0, _MODEL_VERTEX_COUNT * _SIZEOF_FLOAT)
        self._vertex_array.add_layout(self._basic_shader.get_attrib_location('aPosition'), _MODEL_DATA_BUFFER_BINDING, 3, GLType.Float)
        self._vertex_array.add_layout(self._basic_shader.get_attrib_location('aTexCoord'), _MODEL_DATA_BUFFER_BINDING, 2, GLType.Float)

        self._vertex_array.bind_vertex_buffer(_INSTANCE_DATA_BUFFER_BINDING, self._instance_data_buffer, 0, _INSTANCE_VERTEX_COUNT * _SIZEOF_FLOAT, 1)
        self._vertex_array.add_layout(self._basic_shader.get_attrib_location('aColor'), _INSTANCE_DATA_BUFFER_BINDING, 4, GLType.Float)
        self._vertex_array.add_layout(self._basic_shader.get_attrib_location('aTexIdx'), _INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Float)
        self._vertex_array.add_layout(self._basic_shader.get_attrib_location('aEntId'), _INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Float)
        self._vertex_array.add_matrix_layout(self._basic_shader.get_attrib_location('aTransform'), _INSTANCE_DATA_BUFFER_BINDING, 4, 4, GLType.Float)

    @debug.profiled('graphics', 'rendering')
    def _flush(self) -> None:
        assert self._current_model is not None, '_flush called but no model is set.'

        self._model_data_buffer.store(self._current_model.data)

        TextureBase.bind_textures(0, [self._white_texture] + self._textures) # type: ignore

        self._vertex_array.bind()
        self._basic_shader.use()

        GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, self._current_model.vertex_count * self._instance_count, self._instance_count)

        self._instance_data_buffer.reset()
        self._model_data_buffer.reset()
        self._uniform_buffer.reset()
        self._textures.clear()
        self._instance_count = 0

    @debug.profiled('graphics', 'events')
    def _resize_callback(self, e: events.ResizeEvent) -> None:
        self._resize(e.width, e.height)

    @debug.profiled('graphics', 'events')
    def _key_down_callback(self, e: events.KeyDownEvent) -> None:
        if e.repeat:
            return

        if e.key == Key.F1:
            _logger.warning('Taking screenshots is not available yet')
            return

            self.capture_frame()

    def _resize(self, width: int, height: int) -> None:
        GL.glScissor(0, 0, width, height)
        GL.glViewport(0, 0, width, height)

        _logger.info('Viewport size set to %d, %d.', width, height)

def _opengl_debug_callback(source: int, msg_type: int, _, severity: int, __, raw: bytes, ___) -> None:
    _source = DebugSource(source).name.upper()
    _msg_type = DebugType(msg_type).name.upper()
    _severity = DebugSeverity(severity)

    message_formatted = f'OpenGL {_source} -> {_msg_type}: {raw.decode("ansi")}.'

    if _severity == DebugSeverity.High:
        raise exceptions.GraphicsException(message_formatted)
    elif _severity == DebugSeverity.Medium:
        _logger.warning(message_formatted)
    elif _severity in [DebugSeverity.Low, DebugSeverity.Notification]:
        _logger.info(message_formatted)

@debug.profiled('graphics', 'setup')
def _enable_debug_output(debug_proc: GL.GLDEBUGPROC):
    GL.glEnable(GL.GL_DEBUG_OUTPUT)
    GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
    GL.glDebugMessageCallback(debug_proc, None)

    msg = b'Testing OpenGL debug output...'
    GL.glDebugMessageInsert(DebugSource.Application, DebugType.Other, 2137, DebugSeverity.Notification, len(msg), msg)

@debug.profiled('graphics', 'setup')
def _setup_opengl_state() -> None:
    GL.glEnable(GL.GL_MULTISAMPLE)
    GL.glHint(GL.GL_TEXTURE_COMPRESSION_HINT, GL.GL_NICEST)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glDepthFunc(GL.GL_LEQUAL)
    GL.glCullFace(GL.GL_FRONT)
    GL.glFrontFace(GL.GL_CW)
    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
    GL.glPointSize(4.0)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glClearColor(0.0, 0.0, 0.0, 1.0)

@debug.profiled('graphics', 'io')
def _save_screenshot(pixels: np.ndarray, size: tuple[int, int]) -> None:
    img = Image.frombytes('RGB', size, pixels)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    filename = os.path.join(paths.SCREENSHOTS_DIRECTORY, f'screenshot_{int(time.time())}.jpg')
    img.save(filename, 'JPEG')

    _logger.info('Screenshot was saved as "%s".', filename)

_logger = logging.getLogger(__name__)
_screenshot_save_executor = futures.ThreadPoolExecutor(thread_name_prefix='ScreenshotSave')
