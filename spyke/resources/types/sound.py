import typing as t
import uuid

from spyke.audio import ALBuffer
from .resource import ResourceBase

class Sound(ResourceBase):
    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.mp3', '.ogg', '.wav']
    
    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.buffer = ALBuffer.empty()

    def _unload(self) -> None:
        self.buffer.delete()
