from __future__ import annotations
# TODO: Remove unused import statements
from spyke import events, resources, paths
from spyke.ecs import Scene, components
from spyke.enums import GLType, ClearMask, Hint, TextureBufferSizedInternalFormat, MagFilter, MinFilter, NvidiaIntegerName, PolygonMode, ShaderType, Vendor, Key, SizedInternalFormat
from spyke.utils import convert, Iterator
from spyke.resources.types import Image, Model, Font
from ..texturing import Texture
from ..vertex_array import VertexArray
from ..shader import Shader, ShaderSpec
from ..buffers import *
from .renderCommand import RenderCommand
from .rendererInfo import RendererInfo
from typing import Generator, List, Dict
from glfw import _GLFWwindow
from uuid import UUID
from OpenGL import GL
from OpenGL.GL.INTEL.framebuffer_CMAA import glApplyFramebufferAttachmentCMAAINTEL
from PIL import Image as PILImage
import esper
import threading
import glm
import time
import numpy as np
import os
import logging
from spyke import debug

PolygonModeGenerator = Generator[PolygonMode, None, None]
# TODO: Restore particle rendering
# TODO: Fix textures not displaying properly
# TODO: Remove unnecessary constants

_LOGGER = logging.getLogger(__name__)

# TODO: Corelate below constant with buffer sizes
MAX_RENDER_COMMANDS_COUNT = 200

UNIFORM_BLOCK_SIZE = 16 * convert.gl_type_to_size(GLType.Float)
MATRICES_UNIFORM_BLOCK_INDEX = 0

MAX_QUADS_COUNT = 400
VERTICES_PER_QUAD = 4

POS_VERTEX_VALUES_COUNT = 3

BASIC_INSTANCE_VERTEX_VALUES_COUNT = 4 + 2 + 1 + 1 + 16
BASIC_VERTEX_VERTEX_VALUES_COUNT = 2

POST_VERTEX_VERTEX_VALUES_COUNT = 3 + 2

POS_DATA_VERTEX_SIZE = POS_VERTEX_VALUES_COUNT * convert.gl_type_to_size(GLType.Float)

BASIC_INSTANCE_DATA_VERTEX_SIZE = BASIC_INSTANCE_VERTEX_VALUES_COUNT * convert.gl_type_to_size(GLType.Float)
BASIC_VERTEX_DATA_VERTEX_SIZE = BASIC_VERTEX_VERTEX_VALUES_COUNT * convert.gl_type_to_size(GLType.Float)

POST_VERTEX_DATA_VERTEX_SIZE = POST_VERTEX_VERTEX_VALUES_COUNT * convert.gl_type_to_size(GLType.Float)

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1

MAX_TEXTURES_COUNT = 15
BUFFER_TEXTURE_SAMPLER = 15

# TODO: Eventually get this data while loading model for instanced rendering
_quadVertices = [
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 0.0, 0.0]

class Renderer:
    # TODO: Break renderer apart into smaller pieces for easier management

    def __init__(self):
        self.is_initialized: bool = False

        self.info: RendererInfo = RendererInfo()
        self.polygon_mode_iterator: Iterator[PolygonMode] = Iterator([PolygonMode.Fill, PolygonMode.Line, PolygonMode.Point], looping=True)

        self.ubo: DynamicBuffer = None
        self.ibo: DynamicBuffer = None
        self.instance_data_buffer: DynamicBuffer = None
        self.pos_data_buffer: DynamicBuffer = None
        self.vertex_data_buffer: TextureBuffer = None
        self.basic_shader: Shader = None
        self.vao: VertexArray = None
        self.framebuffer: Framebuffer = None

        self.render_commands: Dict[UUID, List[RenderCommand]] = dict()
        self.render_lock: threading.RLock = threading.RLock()
    
    @property
    def render_commands_count(self) -> int:
        return sum(len(x) for x in self.render_commands.values())
    
    @debug.profiled('graphics', 'rendering')
    def shutdown(self) -> None:
        if not self.is_initialized:
            return

        self.ubo.delete()
        self.ibo.delete()
        self.instance_data_buffer.delete()
        self.pos_data_buffer.delete()
        self.vertex_data_buffer.delete()
        self.basic_shader.delete()
        self.vao.delete()
        self.framebuffer.delete()
        
        if Texture._white_texture:
            Texture._white_texture.delete()
        if Texture._invalid_texture:
            Texture._invalid_texture.delete()

        self.is_initialized = False
        _LOGGER.debug('Renderer shutdown completed.')

    @debug.profiled('graphics', 'rendering')
    def initialize(self, window_handle: _GLFWwindow) -> None:
        if self.is_initialized:
            _LOGGER.warning('Renderer already initialized.')
            return

        self.info._get(window_handle)

        # register callbacks
        events.register(self._key_down_callback, events.KeyDownEvent, priority=-1)
        events.register(self._resize_callback, events.ResizeEvent, priority=-1)
        events.register(self._window_move_callback, events.WindowMoveEvent, priority=-1)

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
        shader_spec = ShaderSpec(
            os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.vert'),
            os.path.join(paths.SHADER_SOURCES_DIRECTORY, 'basic.frag'))
        self.basic_shader = Shader(shader_spec)
        self.pos_data_buffer = DynamicBuffer(MAX_RENDER_COMMANDS_COUNT * 1024, GLType.Float)
        self.instance_data_buffer = DynamicBuffer(
            BASIC_INSTANCE_DATA_VERTEX_SIZE * MAX_QUADS_COUNT,
            GLType.Float)
        self.vertex_data_buffer = TextureBuffer(
            BASIC_VERTEX_DATA_VERTEX_SIZE * MAX_QUADS_COUNT * VERTICES_PER_QUAD,
            GLType.Float,
            TextureBufferSizedInternalFormat.Rg32f)
        self.ibo = DynamicBuffer(MAX_RENDER_COMMANDS_COUNT * 128, GLType.UnsignedInt)
        self.ubo = DynamicBuffer(UNIFORM_BLOCK_SIZE, GLType.Float)
        self.vao = VertexArray()

        color_attachment_spec = AttachmentSpec(SizedInternalFormat.Rgba8)

        entity_id_attachment_spec = AttachmentSpec(SizedInternalFormat.R8i)
        entity_id_attachment_spec.min_filter = MinFilter.Nearest
        entity_id_attachment_spec.mag_filter = MagFilter.Nearest

        depth_attachment_spec = AttachmentSpec(SizedInternalFormat.Depth24Stencil8)
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
        framebuffer_spec.samples = 1 if self.info.extension_present('GL_INTEL_framebuffer_CMAA') else 2

        self.framebuffer = Framebuffer(framebuffer_spec)
        self.info.framebuffer_width = self.framebuffer.width
        self.info.framebuffer_height = self.framebuffer.height

        samplers = list(range(MAX_TEXTURES_COUNT))
        self.basic_shader.set_uniform_array('uTextures', samplers)
        self.basic_shader.set_uniform('uTextureCoordsBuffer', BUFFER_TEXTURE_SAMPLER)
        self.basic_shader.set_uniform_block_binding('uMatrices', MATRICES_UNIFORM_BLOCK_INDEX)
        self.basic_shader.validate()

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

        BufferBase.bind_to_uniform(self.ubo, MATRICES_UNIFORM_BLOCK_INDEX)

        _LOGGER.info('Master renderer fully initialized.')

        self.is_initialized = True

    @debug.profiled('graphics', 'rendering')
    def clear_screen(self) -> None:
        GL.glClear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)

    def set_clear_color(self, r: float, g: float, b: float, a: float=1.0) -> None:
        GL.glClearColor(r, g, b, a)

    @debug.profiled('graphics', 'rendering')
    def capture_frame(self) -> None:
        width, height = self.info.framebuffer_size
        pixels = GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)

        img = PILImage.frombytes(
            'RGB', (width, height), pixels)
        img = img.transpose(PILImage.FLIP_TOP_BOTTOM)

        filename = os.path.join(paths.SCREENSHOTS_DIRECTORY, f'screenshot_{time.time()}.jpg')
        img.save(filename, 'JPEG')
        _LOGGER.info('Screenshot was saved as "%s".', filename)

    @debug.profiled('graphics', 'rendering')
    def render_scene(self, scene: Scene) -> None:
        self.info.reset_frame_stats()

        # TODO: Decide if we really want to measure draw time even without performing glFlush
        start = time.perf_counter()

        primary_camera = None
        for _, camera in scene.get_component(components.CameraComponent):
            if camera.is_primary:
                primary_camera = camera

        if not primary_camera:
            view_projection = glm.mat4(1.0)
        else:
            view_projection = primary_camera.view_projection

        self.ubo.store_direct(view_projection)

        BufferBase.bind_ubo(self.ubo)

        # self.framebuffer.bind()

        self.clear_screen()

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, self.polygon_mode_iterator.current)
        GL.glEnable(GL.GL_DEPTH_TEST)

        self._render_objects(scene)
        self._flush()

        GL.glDisable(GL.GL_DEPTH_TEST)

        self._render_text(scene)
        self._flush()

        # TODO: Reimplement particle renderer
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

    @debug.profiled('graphics', 'rendering')
    def _render_text(self, scene: esper.World) -> None:
        text_transform = glm.mat4(1.0)
        fb_width = self.info.framebuffer_width
        fb_height = self.info.framebuffer_height

        for ent, (text, transform) in scene.get_components(components.TextComponent, components.TransformComponent):
            font: Font = resources.get(text.font_id, Font) # type: ignore
            if not font.is_loaded:
                continue
            
            scale = text.size / font.base_size

            x = transform.position.x
            y = transform.position.y

            for char in text.text:
                glyph = font.get_glyph(char)

                # TODO: Normalize all values here
                pos_x = x + ((glyph.bearing.x / fb_height) * scale)
                pos_y = y - (((glyph.size.y - glyph.bearing.y) / fb_height) * scale)

                width = glyph.size.x / fb_width * scale
                height = glyph.size.y / fb_height * scale

                x += glyph.advance / fb_width * scale

                text_transform[3, 0] = pos_x
                text_transform[3, 1] = pos_y
                text_transform[3, 2] = transform.position.z
                text_transform[0, 0] = width
                text_transform[1, 1] = height

                self._render(RenderCommand(
                    font.texture.id,
                    Model.quad,
                    text_transform,
                    text.color,
                    glm.vec2(1.0),
                    ent,
                    glyph.tex_rect.to_coordinates()))

    @debug.profiled('graphics', 'rendering')
    def _render_objects(self, scene: esper.World) -> None:
        for ent, (sprite, transform) in scene.get_components(components.SpriteComponent, components.TransformComponent):
            image: Image = resources.get(sprite.image_id, Image) # type: ignore
            if not image.is_loaded:
                continue
            
            self._render(
                RenderCommand(
                    image.texture.id,
                    transform.model_id,
                    transform.matrix,
                    sprite.color,
                    sprite.tiling_factor,
                    ent))
    
    @debug.profiled('graphics', 'rendering')
    def _flush(self) -> None:
        self.render_lock.acquire()

        textures: List[int] = [0] * MAX_TEXTURES_COUNT

        for model_id, commands in self.render_commands.items():
            instance_count = len(commands)
            last_texture_idx = 0

            # disabling type checks here as mypy doesn't work well with lru_cache
            model: Model = resources.get(model_id, Model) #type: ignore

            self.pos_data_buffer.store_direct(model.position_data)

            for command in commands:
                t_id = command.texture_id
                # TODO: Handle case of not enough texture slots
                if t_id not in textures:
                    textures[last_texture_idx] = t_id
                    last_texture_idx += 1 
                
                texture_idx = textures.index(t_id)

                tex_coords: np.ndarray
                if command.texture_coords_override is not None:
                    tex_coords = command.texture_coords_override
                else:
                    tex_coords = model.texture_coords
                    
                self.vertex_data_buffer.store(tex_coords)
                
                color = command.color
                # TODO: Decide if we really want to have ability
                # to change tiling factor, as it will not work well
                # with complex models anyway
                tiling_factor = command.tiling_factor

                instance_data = np.array([
                    *color,
                    *tiling_factor,
                    texture_idx,
                    command.entity_id], dtype=np.float32)
                
                self.instance_data_buffer.store(instance_data)
                self.instance_data_buffer.store(command.transform)
            
            self._draw(model, instance_count, textures[:last_texture_idx])
        
        self.render_commands.clear()
        self.render_lock.release()
    
    @debug.profiled('graphics', 'rendering')
    def _bind_textures(self, textures: list[int]) -> None:
        GL.glBindTextureUnit(15, self.vertex_data_buffer.texture_id)
        
        for i, texture in enumerate(textures):
            GL.glBindTextureUnit(i, texture)
    
    @debug.profiled('graphics', 'rendering')
    def _draw(self, model: Model, instance_count: int, textures: list[int]) -> None:
        # TODO: Add docs
        self.vertex_data_buffer.flip()
        self.instance_data_buffer.flip()
        
        self._bind_textures(textures)

        self.vao.bind()
        self.basic_shader.use()

        self.basic_shader.set_uniform('uVerticesPerInstance', model.vertices_per_instance)

        accumulated_vertex_count = instance_count * model.vertices_per_instance
        GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, accumulated_vertex_count, instance_count)

        self.info.draw_calls += 1
        self.info.accumulated_vertex_count += accumulated_vertex_count
    
    def _render(self, render_command: RenderCommand) -> None:
        self.render_lock.acquire()

        if self.render_commands_count >= MAX_RENDER_COMMANDS_COUNT:
            self._flush()
        
        model_id = render_command.model_id
        if model_id not in self.render_commands:
            self.render_commands[model_id] = []

        self.render_commands[model_id].append(render_command)

        self.render_lock.release()

    def _window_change_focus_callback(self, e: events.WindowChangeFocusEvent) -> None:
        self.info.window_active = e.value

    def _window_move_callback(self, e: events.WindowMoveEvent) -> None:
        self.info.window_position_x = e.x
        self.info.window_position_y = e.y

    def _key_down_callback(self, e: events.KeyDownEvent) -> None:
        if e.repeat:
            return

        if e.key == Key.Grave:
            next(self.polygon_mode_iterator)
            _LOGGER.info('Renderer drawing mode set to %s', self.polygon_mode_iterator.current)
        elif e.key == Key.F1:
            self.capture_frame()
        elif e.key == Key.F2:
            events.invoke(events.ToggleVsyncEvent(not self.info.vsync))

    def _resize_callback(self, e: events.ResizeEvent) -> None:
        GL.glScissor(0, 0, e.width, e.height)
        GL.glViewport(0, 0, e.width, e.height)

        self.info.window_width = e.width
        self.info.window_height = e.height

        self.info.framebuffer_width = self.framebuffer.width
        self.info.framebuffer_height = self.framebuffer.height