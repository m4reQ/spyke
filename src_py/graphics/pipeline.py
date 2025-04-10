import abc
import dataclasses

from spyke.graphics.frame_data import FrameData


@dataclasses.dataclass(slots=True)
class PipelineInfo:
    buffers_memory_size: int = 0
    attachments_memory_size: int = 0
    framebuffer_attachments: dict[str, int] = dataclasses.field(default_factory=lambda: {'default': 0})

@dataclasses.dataclass(slots=True)
class PipelineSettings:
    model_buffer_size: int
    instance_buffer_size: int
    uniform_buffer_size: int
    index_buffer_size: int

    model_vertex_size: int
    instance_vertex_size: int
    light_data_size: int

    max_textures_per_batch: int
    max_lights: int

class GraphicsPipeline(abc.ABC):
    def __init__(self) -> None:
        self._info = PipelineInfo()

    @property
    def info(self) -> PipelineInfo:
        return self._info

    @abc.abstractmethod
    def get_framebuffer_attachment_id(self, index: int) -> int:
        pass

    @abc.abstractmethod
    def initialize(self, settings: PipelineSettings, fb_width: int, fb_height: int) -> None:
        pass

    @abc.abstractmethod
    def execute(self, frame_data: FrameData) -> None:
        pass

    @abc.abstractmethod
    def reset_buffers(self) -> None:
        pass

    @abc.abstractmethod
    def destroy(self) -> None:
        pass
