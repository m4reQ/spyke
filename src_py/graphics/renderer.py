import ctypes as ct
import dataclasses
import logging
import typing as t

import numpy as np

from spyke import debug, math
from spyke.graphics import gl
from spyke.graphics.deferred_pipeline import DeferredPipeline
from spyke.graphics.frame_data import FrameData
from spyke.graphics.light_data import LightData
from spyke.graphics.pipeline import (GraphicsPipeline, PipelineInfo,
                                     PipelineSettings)
from spyke.graphics.render_batch import RenderBatch
from spyke.scheduler import Scheduler

if t.TYPE_CHECKING:
    from spyke.assets import Image, Model

DEFERRED_PIPELINE = DeferredPipeline()

MAX_MODEL_VERTICES = 8192
MAX_INSTANCES = 1024
MAX_INDICES = 16384
INDEX_SIZE = ct.sizeof(ct.c_ushort)

_FLOAT_SIZE = ct.sizeof(ct.c_float)
_UBYTE_SIZE = ct.sizeof(ct.c_ubyte)
_MAX_TEXTURES_COUNT = 16
_MAX_LIGHTS_COUNT = 32

# space for single 640x480 RGBA8 texture
_INITIAL_TEXTURE_UPLOAD_BUFFER_SIZE = 640 * 480 * 4 * _UBYTE_SIZE
_TEXTURE_UPLOAD_BUFFERS_COUNT = 3
# this is my guess about page size on Intel integrated GPUs, on Nvidia/AMD could be at least 64KB
_GPU_PAGE_SIZE = 4096

class _ModelVertex:
    LENGTH = 3 + 2 + 3
    SIZE = LENGTH * _FLOAT_SIZE

class _InstanceVertex:
    LENGTH = 4 + 1 + 1 + 16
    SIZE = LENGTH * _FLOAT_SIZE

class _UniformData:
    LENGTH = 4 * 4 * 2
    SIZE = LENGTH * _FLOAT_SIZE

class _LightData:
    LENGTH = 8
    SIZE = LENGTH * _FLOAT_SIZE

@dataclasses.dataclass(slots=True)
class TextureUpload:
    image: 'Image'
    data: np.ndarray
    infos: list[gl.TextureUploadInfo]

    @property
    def data_size(self) -> int:
        return self.data.nbytes

    @property
    def data_size_page_size(self) -> int:
        return _round_to_page_size(self.data_size)

    @debug.profiled
    def adjust_data_offsets(self, offset: int) -> None:
        for info in self.infos:
            info.data_offset += offset

class TextureUploadBuffer:
    def __init__(self, initial_size: int) -> None:
        self.buffer = self._create_buffer(initial_size)
        self.upload_finished_sync = gl.Sync()
        self.textures_to_notify = list['Image']()

    def is_available(self) -> bool:
        return self.upload_finished_sync.is_signaled()

    def wait_until_available(self) -> None:
        self.upload_finished_sync.wait()

    @debug.profiled
    def resize(self, new_size: int) -> None:
        if new_size > self.buffer.size:
            self.buffer.delete()
            self.buffer = self._create_buffer(new_size)

    @debug.profiled
    def notify_uploaded_textures(self) -> None:
        # if the buffer finished its transfer we have to signal all textures it uploaded
        for image in self.textures_to_notify:
            # TODO Handle case when user deletes the texture between upload and next process call
            image.is_loaded = True

        # clear textures notify list
        self.textures_to_notify.clear()

    def delete(self) -> None:
        self.buffer.delete()
        self.upload_finished_sync.delete()

    @debug.profiled
    def _create_buffer(self, size: int) -> gl.Buffer:
        buffer = gl.Buffer(size, gl.BufferFlag.MAP_WRITE_BIT | gl.BufferFlag.MAP_PERSISTENT_BIT)
        gl.set_object_name(buffer, 'TextureUploadBuffer')

        return buffer

class TextureBinding:
    def __init__(self, unit: int) -> None:
        self.unit = unit
        self.age = 0

@debug.profiled
def initialize(width: int, height: int) -> None:
    global _frame_data

    gl.initialize()
    gl.disable(gl.EnableCap.MULTISAMPLE)
    gl.disable(gl.EnableCap.FRAMEBUFFER_SRGB)

    # TODO Handle different texture data alignment
    # For now we hardcode alignment to 1 byte which might heavily decrease performance.
    gl.set_pixel_unpack_alignment(1)

    if __debug__:
        _enable_debug_output()

    _create_white_texture()
    _create_texture_upload_buffers(_TEXTURE_UPLOAD_BUFFERS_COUNT, _INITIAL_TEXTURE_UPLOAD_BUFFER_SIZE)

    pipeline_settings = PipelineSettings(
        MAX_MODEL_VERTICES * _ModelVertex.SIZE,
        MAX_INSTANCES * _InstanceVertex.SIZE,
        _UniformData.SIZE,
        MAX_INDICES * INDEX_SIZE,
        _ModelVertex.SIZE,
        _InstanceVertex.SIZE,
        _LightData.SIZE,
        _MAX_TEXTURES_COUNT - 1,
        _MAX_LIGHTS_COUNT)
    DEFERRED_PIPELINE.initialize(pipeline_settings, width, height)

    _frame_data = FrameData(_white_texture, width, height)

    _logger.info('Renderer initialized.')

def shutdown() -> None:
    DEFERRED_PIPELINE.destroy()

    _white_texture.delete()
    for buffer in _texture_upload_buffers:
        buffer.delete()

def get_framebuffer_attachment_id(index: int) -> int:
    '''
    Returns ID of the texture used as main framebuffer's color attachment.
    '''

    assert _current_pipeline is not None, 'Cannot retrieve current framebuffer: no pipeline bound'
    return _current_pipeline.get_framebuffer_attachment_id(index)

def get_framebuffer_width() -> int:
    return _frame_data.frame_width

def get_framebuffer_height() -> int:
    return _frame_data.frame_height

def get_white_texture() -> gl.Texture:
    return _white_texture

@debug.profiled
def _process_texture_uploads_for_buffer(buffer: TextureUploadBuffer) -> None:
    if not buffer.is_available():
        return

    buffer.notify_uploaded_textures()

    _max_texture_size = _round_to_page_size(_texture_uploads[-1].data_size)
    if _max_texture_size > buffer.buffer.size:
        buffer.resize(_max_texture_size)

        # we use persistent, non-coherent buffers and we map it immediately
        # This *might* block because GPU might still be in the process of allocating memory.
        # It's not a problem during renderer initialization but might cause noticable frame drop.
        # If this becomes a problem we can always temporarily skip mapping buffer and remap it in the next call
        # (1 frame should be plenty of time for GPU to allocate memory).

    # gather incoming upload requests
    uploads_to_commit = list[TextureUpload]()
    for upload in _texture_uploads:
        # trying to upload the texture would overflow buffer, stop here
        if not buffer.buffer.can_store_data(upload.data_size):
            break

        upload.adjust_data_offsets(buffer.buffer.current_offset)
        uploads_to_commit.append(upload)

        # TODO HANDLE ALIGNMENT!!!

        # copy texture data to buffer
        # buffer is persistent and non coherent to ensure best performance
        #
        # Another way would be to allow user to 'borrow' a part of buffer and then allow to
        # read data directly into it. While this is more memory efficient because we remove additional user-side
        # allocation, it decreases possibility to pack multiple transfers into one buffer update.
        with debug.profiled_scope('store_texture_data'):
            buffer.buffer.write(
                upload.data,
                alignment=_get_format_required_alignment(upload.infos[0].format))

            # format_size = _get_required_format_alignment(upload.image.texture.internal_format, upload.image.texture.target)
            # buffer.buffer.current_offset = (buffer.buffer.current_offset + format_size - 1) & (-format_size)

        # TODO Add upload data free callback to release CPU side memory immediately after it is no longer needed

        buffer.textures_to_notify.append(upload.image)

    # flush buffer
    with debug.profiled_scope('transfer_texture_data'):
        buffer.buffer.transfer()

    # issue upload calls
    # binding buffer immediately after data transfer might or might not block
    # maybe it's better to bind somewhere else?
    buffer.buffer.bind(gl.BufferTarget.PIXEL_UNPACK_BUFFER)

    _commit_texture_uploads(uploads_to_commit)

    # issue sync to be signaled after all textures have been uploaded
    # unfortunately there is no way of synchronizing just on the data transfer, even if
    # the GPU has separate transfer queue
    buffer.upload_finished_sync.set()

@debug.profiled
def _commit_texture_uploads(uploads: t.Iterable[TextureUpload]) -> None:
    for upload in uploads:
        for upload_info in upload.infos:
            upload.image.texture.upload(upload_info, None)

    for upload in uploads:
        _texture_uploads.remove(upload)

@debug.profiled
def schedule_texture_uploads(scheduler: Scheduler, priority: int) -> None:
    # with debug.profiled_scope('sort_texture_uploads'):
    #     _texture_uploads.sort(key=lambda x: x.data_size)

    for upload in _texture_uploads:
        scheduler.schedule_main_thread_job(_upload_texture, priority, upload)

    _texture_uploads.clear()

@debug.profiled
def _upload_texture(upload: TextureUpload) -> None:
    for info in upload.infos:
        upload.image.texture.upload(info, upload.data)

    upload.image.is_loaded = True
    # _texture_uploads.remove(upload)

@debug.profiled
def process_texture_uploads() -> None:
    with debug.profiled_scope('sort_texture_uploads'):
        _texture_uploads.sort(key=lambda x: x.data_size)

    for buffer in _texture_upload_buffers:
        if len(_texture_uploads) == 0:
            break

        _process_texture_uploads_for_buffer(buffer)

@debug.profiled
def upload_texture(image: 'Image', data: np.ndarray, upload_infos: list[gl.TextureUploadInfo]) -> None:
    _texture_uploads.append(TextureUpload(image, data, upload_infos))

def _round_to_page_size(size: int) -> int:
    return (size + _GPU_PAGE_SIZE - 1) & ~(_GPU_PAGE_SIZE - 1)

@debug.profiled
def begin_frame(pipeline: GraphicsPipeline) -> None:
    global _current_pipeline

    _current_pipeline = pipeline
    _frame_data.reset()

@debug.profiled
def end_frame() -> None:
    assert _current_pipeline is not None, 'Cannot render frame: no pipeline bound'

    _current_pipeline.execute(_frame_data)

@debug.profiled
def resize(width: int, height: int) -> None:
    _frame_data.frame_width = width
    _frame_data.frame_height = height

@debug.profiled
def render(model: 'Model',
           transform: math.Matrix4,
           color: math.Vector4,
           textures_used: t.Sequence[gl.Texture]) -> None:
    with debug.profiled_scope('find_existing_batch'):
        batch_list = _frame_data.batches[model]
        for batch in batch_list:
            if batch.try_add_instance(transform, color, textures_used):
                return

    new_batch = _create_new_batch()
    add_succeeded = new_batch.try_add_instance(transform, color, textures_used)
    assert add_succeeded, 'Failed to add instance to a newly created batch'

    batch_list.append(new_batch)

# TODO Reorder light data so that color is first and A component is the intensity
@debug.profiled
def add_light(position: math.Vector3,
              color: math.Vector3,
              intensity: float = 1.0) -> None:
    if len(_frame_data.lights) >= _MAX_LIGHTS_COUNT:
        return

    _frame_data.lights.append(LightData(position, color, intensity))

def bind_texture(texture_id: int) -> int:
    slot = _textures.get(texture_id, None)
    if slot is not None:
        return slot.unit

    if len(_textures) < _max_bound_textures:
        unit = len(_textures)
        _textures[texture_id] = TextureBinding(unit)
        gl.bind_texture_id(texture_id, unit)

        return unit

    old_texture_id, slot = sorted(_textures.items(), key=lambda x: x[1].age, reverse=True)[0]
    del _textures[old_texture_id]

    slot.age = 0
    _textures[texture_id] = slot
    gl.bind_texture_id(texture_id, unit)

    return slot.unit

def update_textures() -> None:
    for slot in _textures.values():
        slot.age += 1

def set_camera_transform(view: math.Matrix4, projection: math.Matrix4, position: math.Vector3) -> None:
    _frame_data.camera_view = view
    _frame_data.camera_projection = projection
    _frame_data.camera_pos = position

def set_polygon_mode(mode: gl.PolygonMode) -> None:
    _frame_data.polygon_mode = mode

def set_clear_color(color: math.Vector4) -> None:
    _frame_data.clear_color = color

def get_clear_color() -> math.Vector4:
    return _frame_data.clear_color

def get_pipeline_info() -> PipelineInfo:
    assert _current_pipeline is not None, 'No pipeline bound'
    return _current_pipeline.info

def _get_format_required_alignment(format: gl.PixelFormat) -> int:
    match format:
        case gl.PixelFormat.RED:
            return 1
        case gl.PixelFormat.RG:
            return 2
        case gl.PixelFormat.RGB:
            return 1
        case gl.PixelFormat.BGR:
            return 1
        case gl.PixelFormat.RGBA:
            return 4
        case gl.PixelFormat.BGRA:
            return 4
        case gl.PixelFormat.DEPTH_COMPONENT:
            return 1
        case gl.PixelFormat.STENCIL_INDEX:
            return 1

    # raise ValueError('Invalid pixel format')
    return 1

def _create_new_batch() -> RenderBatch:
    return RenderBatch(
        MAX_INSTANCES,
        _MAX_TEXTURES_COUNT - 1)

def _opengl_debug_callback(source: int, msg_type: int, severity: int, _: int, msg: str) -> None:
    _source = gl.DebugSource(source).name.upper()
    _msg_type = gl.DebugType(msg_type).name.upper()

    message_formatted = f'OpenGL[{_source}] -> {_msg_type}: {msg}.'

    if severity == gl.DebugSeverity.HIGH:
        _logger.error(message_formatted)
    elif severity == gl.DebugSeverity.MEDIUM:
        _logger.warning(message_formatted)
    elif severity in (gl.DebugSeverity.LOW, gl.DebugSeverity.NOTIFICATION):
        _logger.info(message_formatted)

@debug.profiled
def _enable_debug_output():
    gl.enable(gl.EnableCap.DEBUG_OUTPUT)
    gl.enable(gl.EnableCap.DEBUG_OUTPUT_SYNCHRONOUS)
    gl.debug_message_callback(_opengl_debug_callback)
    gl.debug_message_insert(
        gl.DebugSource.APPLICATION,
        gl.DebugType.OTHER,
        gl.DebugSeverity.NOTIFICATION,
        2137,
        'Testing OpenGL debug output..')

@debug.profiled
def _create_white_texture() -> None:
    global _white_texture

    _white_texture = gl.Texture(
        gl.TextureSpec(
            gl.TextureTarget.TEXTURE_2D,
            1,
            1,
            gl.InternalFormat.RGBA8,
            min_filter=gl.MinFilter.NEAREST,
            mag_filter=gl.MagFilter.NEAREST))
    _white_texture.upload(
        gl.TextureUploadInfo(gl.PixelFormat.RGBA, 1, 1),
        np.array([255, 255, 255, 255], np.uint8))

    if __debug__:
        gl.set_object_name(_white_texture, 'WhiteTexture')

@debug.profiled
def _create_texture_upload_buffers(count: int, initial_size: int) -> None:
    for i in range(count):
        buffer = TextureUploadBuffer(initial_size)
        gl.set_object_name(buffer.buffer, f'TextureUploadBuffer_{i}')

        _texture_upload_buffers.append(buffer)

    global _upload_buffer_max_size
    _upload_buffer_max_size = initial_size

_logger = logging.getLogger(__name__)
_white_texture: gl.Texture
_frame_data: FrameData
_current_pipeline: GraphicsPipeline | None = None

_texture_upload_buffers = list[TextureUploadBuffer]()
_texture_uploads = list[TextureUpload]()
_max_bound_textures = 16
_textures = dict[int, TextureBinding]()
_upload_buffer_resize_request: int | None = None
_upload_buffer_max_size = 0
