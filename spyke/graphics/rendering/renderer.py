from __future__ import annotations
import typing

from spyke.graphics.texturing.textureProxy import TextureProxy
if typing.TYPE_CHECKING:
    from glfw import _GLFWwindow
    from spyke.ecs import Scene
    from typing import Optional, Generator, List, Union

    PolygonModeGenerator = Generator[PolygonMode, None, None]

# TODO: Remove unused import statements
from spyke import debug
from spyke.ecs.components.camera import CameraComponent
from spyke.enums import GLType, ClearMask, Hint, TextureBufferSizedInternalFormat, MagFilter, MinFilter, NvidiaIntegerName, PolygonMode, ShaderType, Vendor, Keys, SizedInternalFormat
from spyke import events
from spyke.graphics import Rectangle
from ..texturing import Texture
from ..vertexArray import VertexArray
from ...utils import create_quad_indices
from .rendererInfo import RendererInfo
from ..shader import Shader
from ..buffers import *
from ...constants import _GL_FLOAT_SIZE
from ...ecs import components

from OpenGL import GL
from OpenGL.GL.INTEL.framebuffer_CMAA import glApplyFramebufferAttachmentCMAAINTEL
from PIL import Image
import glm
import time
import numpy as np
import os

# TODO: Restore particle rendering
# TODO: Fix textures not displaying properly
# TODO: Remove unnecessary constants

SCREENSHOT_DIRECTORY = "screenshots/"
SHADER_SOURCES_DIRECTORY = "spyke/graphics/shaderSources/"

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
MATRICES_UNIFORM_BLOCK_INDEX = 0

DEFAULT_RENDER_COLOR_ATTACHMENT = 0
ENTITY_ID_ATTACHMENT = 1

MAX_QUADS_COUNT = 400
VERTICES_PER_QUAD = 4
INDICES_PER_QUAD = 6

POS_VERTEX_VALUES_COUNT = 3

BASIC_INSTANCE_VERTEX_VALUES_COUNT = 4 + 2 + 1 + 1 + 16
BASIC_VERTEX_VERTEX_VALUES_COUNT = 2

POST_VERTEX_VERTEX_VALUES_COUNT = 3 + 2

POS_DATA_VERTEX_SIZE = POS_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

BASIC_INSTANCE_DATA_VERTEX_SIZE = BASIC_INSTANCE_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE
BASIC_VERTEX_DATA_VERTEX_SIZE = BASIC_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POST_VERTEX_DATA_VERTEX_SIZE = POST_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1
POST_DATA_BUFFER_BINDING = 0

MAX_TEXTURES_COUNT = 15

MULTISAMPLE_TEXTURE_SAMPLER = 0
NORMAL_TEXTURE_SAMPLER = 1

BUFFER_TEXTURE_SAMPLER = 15

# TODO: Eventually get this data while loading model for instanced rendering
_quadVertices = [
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 0.0, 0.0]


class Renderer:
    # TODO: Break renderer apart into smaller pieces for easier menagement

    def __init__(self):
        self.is_initialized: bool = False

        self.info: RendererInfo = RendererInfo()

        self.polygon_mode_generator: PolygonModeGenerator = self._polygon_mode_generator_impl()
        self.polygon_mode: PolygonMode = next(self.polygon_mode_generator)

        self.ubo: UniformBuffer = None
        self.ibo: StaticBuffer = None
        self.instance_data_buffer: DynamicBuffer = None
        self.pos_data_buffer: StaticBuffer = None
        self.vertex_data_buffer: TextureBuffer = None
        self.basic_shader: Shader = None
        self.vao: VertexArray = None
        self.framebuffer: Framebuffer = None

        self.last_texture: int = 1
        self.instance_count: int = 0
        self.textures: List[int] = [0] * MAX_TEXTURES_COUNT

    def initialize(self, window_handle: _GLFWwindow) -> None:
        if self.is_initialized:
            debug.log_warning('Renderer already initialized.')
            return

        debug.check_context()

        self.info._get(window_handle)

        # register callbacks
        events.register_method(self._key_down_callback,
                               events.KeyDownEvent, priority=-1)
        events.register_method(self._resize_callback,
                               events.ResizeEvent, priority=-1)
        events.register_method(self._window_move_callback,
                               events.WindowMoveEvent, priority=-1)

        # TODO: Possibly move this to resource manager
        if not os.path.exists(SCREENSHOT_DIRECTORY):
            os.mkdir(SCREENSHOT_DIRECTORY)

        # set vendor-specific properties of the renderer
        # TODO: Add support for nv_commands_lists here
        # TODO: Restore texture compression
        # if self.info.extension_present('gl_arb_texture_compression'):
        #     Texture.set_compression_flag()

        if self.info.vendor == Vendor.Nvidia:
            GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_NICEST)

        # enable all required OpenGL settings
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

        # create all components (buffers, vaos, etc.)
        self.pos_data_buffer = StaticBuffer(_quadVertices, GLType.Float)
        self.instance_data_buffer = DynamicBuffer(
            BASIC_INSTANCE_DATA_VERTEX_SIZE * MAX_QUADS_COUNT, GLType.Float)
        self.vertex_data_buffer = TextureBuffer(BASIC_VERTEX_DATA_VERTEX_SIZE *
                                                MAX_QUADS_COUNT * VERTICES_PER_QUAD, GLType.Float, TextureBufferSizedInternalFormat.Rg32f)
        self.ibo = StaticBuffer(create_quad_indices(
            MAX_QUADS_COUNT), GLType.UnsignedInt)
        self.basic_shader = Shader()
        self.ubo = UniformBuffer(UNIFORM_BLOCK_SIZE, GLType.Float)
        self.vao = VertexArray()
        self.textures[0] = Texture.create_white_texture().id

        color_attachment_spec = AttachmentSpec(SizedInternalFormat.Rgba8)

        entity_id_attachment_spec = AttachmentSpec(SizedInternalFormat.R8i)
        entity_id_attachment_spec.min_filter = MinFilter.Nearest
        entity_id_attachment_spec.mag_filter = MagFilter.Nearest

        depth_attachment_spec = AttachmentSpec(
            SizedInternalFormat.Depth24Stencil8)
        depth_attachment_spec.min_filter = MinFilter.Nearest
        depth_attachment_spec.mag_filter = MagFilter.Nearest

        attachments_specs = [
            color_attachment_spec,
            entity_id_attachment_spec,
            depth_attachment_spec
        ]

        # TODO: Handle usage of framebuffer with different size than the window
        framebuffer_spec = FramebufferSpec(
            self.info.window_width,
            self.info.window_height)
        framebuffer_spec.is_resizable = True
        framebuffer_spec.attachments_specs = attachments_specs
        # TODO: Get samples count from some kind of settings file
        framebuffer_spec.samples = 1 if self.info.extension_present(
            'GL_INTEL_framebuffer_CMAA') else 2

        self.framebuffer = Framebuffer(framebuffer_spec)
        self.info.framebuffer_width = self.framebuffer.width
        self.info.framebuffer_height = self.framebuffer.height

        # set up all renderer's components
        self.basic_shader.add_stage(ShaderType.VertexShader,
                                    SHADER_SOURCES_DIRECTORY + 'basic.vert')
        self.basic_shader.add_stage(ShaderType.FragmentShader,
                                    SHADER_SOURCES_DIRECTORY + 'basic.frag')
        self.basic_shader.compile()

        samplers = list(range(MAX_TEXTURES_COUNT))
        self.basic_shader.set_uniform_int(
            'uTextures', samplers)
        self.basic_shader.set_uniform_int(
            'uTextureCoordsBuffer', BUFFER_TEXTURE_SAMPLER)
        self.basic_shader.set_uniform_block_binding(
            'uMatrices', MATRICES_UNIFORM_BLOCK_INDEX)
        self.basic_shader.validate()

        # // per-instance data:
        # layout(location=1) in vec4 aColor;
        # layout(location=2) in vec2 aTiling;
        # layout(location=3) in float aTexIndex;
        # layout(location=4) in float aEntityId;
        # layout(location=5) in mat4 aTransform;

        self.vao.bind_element_buffer(self.ibo)

        self.vao.bind_vertex_buffer(
            POS_DATA_BUFFER_BINDING, self.pos_data_buffer, 0, POS_DATA_VERTEX_SIZE)
        self.vao.add_layout(self.basic_shader.get_attrib_location(
            'aPosition'), POS_DATA_BUFFER_BINDING, 3, GLType.Float, False)

        self.vao.bind_vertex_buffer(
            INSTANCE_DATA_BUFFER_BINDING, self.instance_data_buffer, 0, BASIC_INSTANCE_DATA_VERTEX_SIZE)
        self.vao.add_layout(self.basic_shader.get_attrib_location(
            'aColor'), INSTANCE_DATA_BUFFER_BINDING, 4, GLType.Float, False, 1)
        self.vao.add_layout(self.basic_shader.get_attrib_location(
            'aTiling'), INSTANCE_DATA_BUFFER_BINDING, 2, GLType.Float, False, 1)
        self.vao.add_layout(self.basic_shader.get_attrib_location(
            'aTexIndex'), INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Float, False, 1)
        self.vao.add_layout(self.basic_shader.get_attrib_location(
            'aEntityId'), INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Float, False, 1)
        self.vao.add_matrix_layout(self.basic_shader.get_attrib_location(
            'aTransform'), INSTANCE_DATA_BUFFER_BINDING, 4, 4, GLType.Float, False, 1)

        self.ubo.bind_to_uniform(MATRICES_UNIFORM_BLOCK_INDEX)

        debug.get_gl_error()
        debug.log_info('Master renderer fully initialized.')

        self.is_initialized = True

    def clear_screen(self) -> None:
        GL.glClear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)

    def set_clear_color(self, r: float, g: float, b: float, a: float) -> None:
        GL.glClearColor(r, g, b, a)

    def capture_frame(self) -> None:
        # TODO: Decide whether we want to capture frame with the size
        # of framebuffer or if we want to scale it to the window size

        width, height = self.info.framebuffer_size
        pixels = GL.glReadPixels(0, 0, width, height,
                                 GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)

        img = Image.frombytes(
            'RGB', (width, height), pixels)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        filename = os.path.join(SCREENSHOT_DIRECTORY,
                                f'screenshot_{time.time()}.jpg')
        img.save(filename, 'JPEG')
        debug.log_info(f'Screenshot was saved as "{filename}".')

    def render_scene(self, scene: Scene) -> None:
        self.info.reset_frame_stats()

        # TODO: Decide if we really want to measure draw time even without performing glFlush
        start = time.perf_counter()

        primary_camera = None
        for _, camera in scene.get_component(CameraComponent):
            if camera.is_primary:
                primary_camera = camera

        if not primary_camera:
            view_projection = glm.mat4(1.0)
        else:
            view_projection = primary_camera.view_projection

        self.ubo.add_data(np.asarray(
            view_projection, dtype=np.float32).T.flatten())
        self.ubo.flip()

        self.ubo.bind()

        # per-vertex data (in vbo): position // only ONE model
        # per-vertex data (in tbo): all of texture coordinates for every instance -> [], [], [] ...
        # per-instance data (in vbo): color, TRANSFORM, tiling, texture index, ... // BIGGER

        # offsetting tbo with indices

        # self.framebuffer.bind()

        self.clear_screen()

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, self.polygon_mode)
        GL.glEnable(GL.GL_DEPTH_TEST)

        # drawables = [x for x in scene.GetComponents(components.SpriteComponent, components.TransformComponent)]
        # opaque = [x for x in drawables if x[1][0].color.w == 1.0]
        # alpha = [x for x in drawables if x not in opaque]

        # alpha.sort(key = lambda x: x[1][0].color.w, reverse = True)
        # for ent, (sprite, transform) in opaque:
        # 	_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tiling_factor, entId=int(ent))

        # _Flush()

        # GL.glDisable(GL.GL_DEPTH_TEST)
        # for ent, (sprite, transform) in alpha:
        # 	_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tiling_factor, entId=int(ent))

        # _Flush()

        for ent, (sprite, transform) in scene.get_components(components.SpriteComponent, components.TransformComponent):
            self._render_quad(transform.matrix, sprite.color, sprite.tiling_factor,
                              texture=sprite.image.texture, ent_id=int(ent))

        self._flush()

        GL.glDisable(GL.GL_DEPTH_TEST)

        text_transform = glm.mat4(1.0)
        fb_width = self.info.framebuffer_width
        fb_height = self.info.framebuffer_height

        for ent, (text, transform) in scene.get_components(components.TextComponent, components.TransformComponent):
            font = text.font
            scale = text.size / font.base_size

            x = transform.position.x
            y = transform.position.y

            for char in text.text:
                glyph = font.get_glyph(char)

                # TODO: Normalize all values here
                pos_x = (x + glyph.bearing.x) / fb_height * scale
                pos_y = (y - (glyph.size.y - glyph.bearing.y)) / \
                    fb_height * scale

                width = glyph.size.x / fb_width * scale
                height = glyph.size.y / fb_height * scale

                x += glyph.advance / fb_width * scale

                text_transform[3, 0] = pos_x
                text_transform[3, 1] = pos_y
                text_transform[3, 2] = transform.position.z
                text_transform[0, 0] = width
                text_transform[1, 1] = height

                self._render_quad(text_transform, text.color,
                                  glm.vec2(1.0, 1.0), texture=font.texture, tex_rect=glyph.tex_rect, ent_id=int(ent))

        self._flush()

        # for _, system in scene.GetComponent(components.ParticleSystemComponent):
        # 	for particle in system.particlePool:
        # 		if particle.isAlive:
        # 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

        # TODO: Implement rendering of multisampled framebuffer
        # if self.info.extension_present('GL_INTEL_framebuffer_CMAA'):
        # self.framebuffer.unbind()

        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        # GL.glViewport(0, 0, self.info.window_width, self.info.window_height)

        # self.clear_screen()

        # self._render_quad(glm.mat4(1.0), glm.vec4(1.0), glm.vec2(
        #     1.0), self.framebuffer.get_color_attachment(0))
        # self._flush()

        if self.info.vendor == Vendor.Nvidia:
            self.info.video_memory_used = self.info.video_memory_available - \
                GL.glGetInteger(NvidiaIntegerName.GpuMemInfoCurrentAvailable)

        self.info.drawtime = time.perf_counter() - start

    def _flush(self) -> None:
        if not self.instance_count:
            return

        self.vertex_data_buffer.flip()
        self.instance_data_buffer.flip()

        for i in range(self.last_texture):
            GL.glBindTextureUnit(i, self.textures[i])

        GL.glBindTextureUnit(15, self.vertex_data_buffer.texture_id)

        self.vao.bind()
        self.basic_shader.use()

        # TODO: Unhardcode this later
        self.basic_shader.set_uniform_int('uVerticesPerInstance', 4)

        # TODO: Later unhardcode `INDICES_PER_QUAD` to match actual count of
        # vertices per rendered object instance
        GL.glDrawElementsInstanced(
            GL.GL_TRIANGLES, self.instance_count * INDICES_PER_QUAD, self.ibo.data_type, None, self.instance_count)

        self.info.draw_calls += 1
        self.info.accumulated_vertex_count += self.instance_count * VERTICES_PER_QUAD

        self.instance_count = 0
        self.last_texture = 1

    # TODO: Create some kind of precompiled quad data object that stores below informations
    def _render_quad(self, transform: glm.mat4, color: glm.vec4, tilingFactor: glm.vec2, texture: Union[Optional[Texture], TextureProxy], tex_rect: Rectangle = Rectangle.one(), ent_id: int = -1) -> None:
        # TODO: Unhardcode this to match maximum capacity of the vertex buffer
        # with value given by `instance_count * current_model_vertices_per_instance`
        if self.instance_count > MAX_QUADS_COUNT:
            self._flush()

        tex_idx = 0

        if texture:
            for i in range(1, self.last_texture):
                if self.textures[i] == texture.id:
                    tex_idx = i
                    break

            if tex_idx == 0:
                if self.last_texture >= MAX_TEXTURES_COUNT:
                    self._flush()

                tex_idx = self.last_texture
                self.textures[self.last_texture] = texture.id
                self.last_texture += 1

        vertex_data = [
            tex_rect.left, tex_rect.top,
            tex_rect.right, tex_rect.top,
            tex_rect.right, tex_rect.bottom,
            tex_rect.left, tex_rect.bottom,
        ]

        self.vertex_data_buffer.add_data(
            np.asarray(vertex_data, dtype=np.float32))

        instance_data = np.concatenate((
            [
                color.x,
                color.y,
                color.z,
                color.w,
                tilingFactor.x,
                tilingFactor.y,
                tex_idx,
                ent_id
            ],
            np.asarray(glm.transpose(transform), dtype=np.float32).flatten()
        ))

        self.instance_data_buffer.add_data(instance_data)

        self.instance_count += 1

    def _window_change_focus_callback(self, e: events.WindowChangeFocusEvent) -> None:
        self.info.window_active = e.value

    def _window_move_callback(self, e: events.WindowMoveEvent) -> None:
        self.info.window_position_x = e.x
        self.info.window_position_y = e.y

    def _key_down_callback(self, e: events.KeyDownEvent) -> None:
        if e.repeat:
            return

        if e.key == Keys.KeyGrave:
            self.polygon_mode = next(self.polygon_mode_generator)
            debug.log_info(
                f'Renderer drawing mode set to: {self.polygon_mode.name}')
        elif e.key == Keys.KeyF1:
            self.capture_frame()
        elif e.key == Keys.KeyF2:
            events.invoke(events.ToggleVsyncEvent(not self.info.vsync))

    def _resize_callback(self, e: events.ResizeEvent) -> None:
        GL.glScissor(0, 0, e.width, e.height)
        GL.glViewport(0, 0, e.width, e.height)

        self.info.window_width = e.width
        self.info.window_height = e.height

        self.info.framebuffer_width = self.framebuffer.width
        self.info.framebuffer_height = self.framebuffer.height

    def _polygon_mode_generator_impl(self) -> PolygonModeGenerator:
        while True:
            yield PolygonMode.Fill
            yield PolygonMode.Line
            yield PolygonMode.Point
