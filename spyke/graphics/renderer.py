import ctypes as ct
import logging
import os

import numpy as np

import pygl
import pygl.vertex_array
from pygl import buffers, commands
from pygl import debug as gl_debug
from pygl import framebuffer, rendering, shaders, sync, textures, vertex_array
from pygl.math import Matrix4, Vector4
from spyke import debug, paths
from spyke.assets.types.model import Model
from spyke.graphics.deferred_pipeline import DeferredPipeline
from spyke.graphics.frame_data import FrameData
from spyke.graphics.pipeline import GraphicsPipeline, PipelineSettings
from spyke.graphics.render_batch import RenderBatch
from spyke.graphics.ring_buffer import RingBuffer
from spyke.graphics.texture_buffer import TextureBuffer

DEFERRED_PIPELINE = DeferredPipeline()

MAX_MODEL_VERTICES = 8192
MAX_INSTANCES = 1024
MAX_INDICES = 16384
INDEX_SIZE = ct.sizeof(ct.c_ushort)

_FLOAT_SIZE = ct.sizeof(ct.c_float)
_UBYTE_SIZE = ct.sizeof(ct.c_ubyte)
_MAX_TEXTURES_COUNT = 16

_INITIAL_TEXTURE_UPLOAD_BUFFER_SIZE = 640 * 480 * 4 * _UBYTE_SIZE

class ModelVertex:
    LENGTH = 3 + 2 + 3
    SIZE = LENGTH * _FLOAT_SIZE

class InstanceVertex:
    LENGTH = 4 + 1 + 16
    SIZE = LENGTH * _FLOAT_SIZE

class UniformData:
    LENGTH = 4 * 4 * 2
    SIZE = LENGTH * _FLOAT_SIZE

@debug.profiled('renderer', 'initialization')
def initialize(width: int, height: int) -> None:
    global _frame_data

    pygl.init()

    if __debug__:
        _enable_debug_output()

    _create_white_texture()
    _create_texture_upload_buffer(_INITIAL_TEXTURE_UPLOAD_BUFFER_SIZE)

    pipeline_settings = PipelineSettings(
        MAX_MODEL_VERTICES * ModelVertex.SIZE,
        MAX_INSTANCES * InstanceVertex.SIZE,
        UniformData.SIZE,
        MAX_INDICES * INDEX_SIZE,
        ModelVertex.SIZE,
        InstanceVertex.SIZE,
        _MAX_TEXTURES_COUNT - 1)
    DEFERRED_PIPELINE.initialize(pipeline_settings, width, height)

    _frame_data = FrameData(_white_texture, width, height)

    _logger.info('Renderer initialized.')

def shutdown() -> None:
    DEFERRED_PIPELINE.destroy()

    _white_texture.delete()
    _texture_upload_buffer.delete()
    _texture_upload_sync.delete()

def get_framebuffer_color_texture_id() -> int:
    '''
    Returns ID of the texture used as main framebuffer's color attachment.
    '''
    Returns ID of the texture used as main framebuffer's color attachment.
    '''
    Returns ID of the texture used as main framebuffer's depth-stencil attachment.
    '''

    return _framebuffer.get_attachment_id(framebuffer.Attachment.DEPTH_STENCIL_ATTACHMENT)

    assert _current_pipeline is not None, 'Cannot retrieve current framebuffer: no pipeline bound'
    return _current_pipeline.get_output_texture_id()

def get_framebuffer_width() -> int:
    assert _frame_data is not None, 'Frame data not present: renderer not initialized properly'
    return _frame_data.frame_width

def get_framebuffer_height() -> int:
    assert _frame_data is not None, 'Frame data not present: renderer not initialized properly'
    return _frame_data.frame_height

def get_white_texture() -> textures.Texture:
    return _white_texture

@debug.profiled('graphics', 'rendering')
def begin_frame(pipeline: GraphicsPipeline) -> None:
    global _current_pipeline

    _current_pipeline = pipeline

@debug.profiled('graphics', 'rendering')
def end_frame() -> None:
    assert _current_pipeline is not None, 'Cannot render frame: no pipeline bound'
    assert _frame_data is not None, 'Cannot render frame: no frame data, renderer not initialized properly'

    _current_pipeline.render(_frame_data)
    _frame_data.reset()

@debug.profiled('graphics', 'rendering')
def resize(width: int, height: int) -> None:
    assert _frame_data is not None, 'Frame data not present: renderer not initialized properly'

    _frame_data.frame_width = width
    _frame_data.frame_height = height

@debug.profiled('graphics', 'rendering')
def render(model: Model,
           transform: Matrix4,
           color: Vector4,
           texture: textures.Texture | None = None) -> None:
    assert _frame_data is not None, 'Frame data not present: renderer not initialized properly'

    batch_list = _frame_data.batches[model]
    for batch in batch_list:
        if batch.try_add_instance(transform, color, texture):
            return

    new_batch = _create_new_batch()
    add_succeeded = new_batch.try_add_instance(transform, color, texture)
    assert add_succeeded, 'Failed to add instance to a newly created batch'

    batch_list.append(new_batch)

@debug.profiled('rendering')
def acquire_texture_upload_buffer(texture_width: int, texture_height: int, texture_format: textures.InternalFormat) -> buffers.Buffer:
    texture_size = _calculate_texture_byte_size(texture_width, texture_height, texture_format)

    if _texture_upload_buffer.size < texture_size:
        _texture_upload_buffer.delete()
        _texture_upload_sync.delete()
        _create_texture_upload_buffer(texture_size)

    _texture_upload_buffer.bind(buffers.BindTarget.PIXEL_UNPACK_BUFFER)
    return _texture_upload_buffer

def set_camera_transform(view: Matrix4, projection: Matrix4) -> None:
    assert _frame_data is not None, 'Renderer not initialized: frame data is None'

    _frame_data.camera_view = view
    _frame_data.camera_projection = projection

def set_polygon_mode(mode: commands.PolygonMode) -> None:
    assert _frame_data is not None, 'Renderer not initialized: frame data is None'

    _frame_data.polygon_mode = mode

def set_clear_color(color: Vector4) -> None:
    assert _frame_data is not None, 'Renderer not initialized: frame data is None'

    _frame_data.clear_color = color

def get_clear_color() -> Vector4:
    assert _frame_data is not None, 'Renderer not initialized: frame data is None'
    return _frame_data.clear_color

def _calculate_texture_byte_size(width: int, height: int, format: textures.InternalFormat) -> int:
    bpp: int
    match format:
        case textures.InternalFormat.R8:
            bpp = 1
        case textures.InternalFormat.R8_SNORM:
            bpp = 1
        case textures.InternalFormat.R16:
            bpp = 2
        case textures.InternalFormat.R16_SNORM:
            bpp = 2
        case textures.InternalFormat.RG8:
            bpp = 2
        case textures.InternalFormat.RG8_SNORM:
            bpp = 2
        case textures.InternalFormat.RG16:
            bpp = 4
        case textures.InternalFormat.RG16_SNORM:
            bpp = 4
        case textures.InternalFormat.R3_G3_B2:
            bpp = 1
        case textures.InternalFormat.RGB4:
            bpp = 2
        case textures.InternalFormat.RGB5:
            bpp = 2
        case textures.InternalFormat.RGB8:
            bpp = 3
        case textures.InternalFormat.RGB8_SNORM:
            bpp = 3
        case textures.InternalFormat.RGB10:
            bpp = 4
        case textures.InternalFormat.RGB12:
            bpp = 5
        case textures.InternalFormat.RGB16_SNORM:
            bpp = 6
        case textures.InternalFormat.RGBA2:
            bpp = 1
        case textures.InternalFormat.RGBA4:
            bpp = 2
        case textures.InternalFormat.RGB5_A1:
            bpp = 2
        case textures.InternalFormat.RGBA8:
            bpp = 4
        case textures.InternalFormat.RGBA8_SNORM:
            bpp = 4
        case textures.InternalFormat.RGB10_A2:
            bpp = 4
        case textures.InternalFormat.RGB10_A2UI:
            bpp = 4
        case textures.InternalFormat.RGBA12:
            bpp = 5
        case textures.InternalFormat.RGBA16:
            bpp = 8
        case textures.InternalFormat.SRGB8:
            bpp = 3
        case textures.InternalFormat.SRGB8_ALPHA8:
            bpp = 4
        case textures.InternalFormat.R16F:
            bpp = 2
        case textures.InternalFormat.RG16F:
            bpp = 4
        case textures.InternalFormat.RGB16F:
            bpp = 6
        case textures.InternalFormat.RGBA16F:
            bpp = 8
        case textures.InternalFormat.R32F:
            bpp = 4
        case textures.InternalFormat.RG32F:
            bpp = 8
        case textures.InternalFormat.RGB32F:
            bpp = 12
        case textures.InternalFormat.RGBA32F:
            bpp = 16
        case textures.InternalFormat.R11F_G11F_B10F:
            bpp = 4
        case textures.InternalFormat.RGB9_E5:
            bpp = 4
        case textures.InternalFormat.R8I:
            bpp = 1
        case textures.InternalFormat.R8UI:
            bpp = 1
        case textures.InternalFormat.R16I:
            bpp = 2
        case textures.InternalFormat.R16UI:
            bpp = 2
        case textures.InternalFormat.R32I:
            bpp = 4
        case textures.InternalFormat.R32UI:
            bpp = 4
        case textures.InternalFormat.RG8I:
            bpp = 2
        case textures.InternalFormat.RG8UI:
            bpp = 2
        case textures.InternalFormat.RG16I:
            bpp = 4
        case textures.InternalFormat.RG16UI:
            bpp = 4
        case textures.InternalFormat.RG32I:
            bpp = 8
        case textures.InternalFormat.RG32UI:
            bpp = 8
        case textures.InternalFormat.RGB8I:
            bpp = 3
        case textures.InternalFormat.RGB8UI:
            bpp = 3
        case textures.InternalFormat.RGB16I:
            bpp = 6
        case textures.InternalFormat.RGB16UI:
            bpp = 6
        case textures.InternalFormat.RGB32I:
            bpp = 12
        case textures.InternalFormat.RGB32UI:
            bpp = 12
        case textures.InternalFormat.RGBA8I:
            bpp = 4
        case textures.InternalFormat.RGBA8UI:
            bpp = 4
        case textures.InternalFormat.RGBA16I:
            bpp = 8
        case textures.InternalFormat.RGBA16UI:
            bpp = 8
        case textures.InternalFormat.RGBA32I:
            bpp = 16
        case textures.InternalFormat.RGBA32UI:
            bpp = 16

    return width * height * bpp

def _create_new_batch() -> RenderBatch:
    return RenderBatch(
        MAX_INSTANCES,
        _MAX_TEXTURES_COUNT - 1)

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

def _pygl_log_callback(log_level: int, msg: str) -> None:
    match log_level:
        case gl_debug.LogLevel.INFO:
            _logger.debug(msg)
        case gl_debug.LogLevel.WARNING:
            _logger.warning(msg)
        case gl_debug.LogLevel.ERROR:
            _logger.error(msg)

@debug.profiled('graphics', 'setup')
def _enable_debug_output():
    gl_debug.set_log_callback(_pygl_log_callback)
    gl_debug.enable(_opengl_debug_callback)
    gl_debug.insert_message(
        gl_debug.DebugSource.DEBUG_SOURCE_APPLICATION,
        gl_debug.DebugType.DEBUG_TYPE_OTHER,
        2137,
        gl_debug.DebugSeverity.DEBUG_SEVERITY_NOTIFICATION,
        'Testing OpenGL debug output..')

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

    if __debug__:
        gl_debug.set_object_name(_white_texture, 'WhiteTexture')

@debug.profiled('graphics', 'rendering')
def _create_texture_upload_buffer(initial_size: int) -> None:
    global _texture_upload_buffer, _texture_upload_sync

    _texture_upload_buffer = buffers.Buffer(initial_size, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)
    gl_debug.set_object_name(_texture_upload_buffer, 'TextureUploadBuffer')

    _texture_upload_sync = sync.Sync()
    gl_debug.set_object_name(_texture_upload_buffer, 'TextureUploadSync')

_logger = logging.getLogger(__name__)
_white_texture: textures.Texture
_texture_upload_buffer: buffers.Buffer
_texture_upload_sync: sync.Sync
_current_pipeline: GraphicsPipeline | None = None
_frame_data: FrameData | None = None
