from __future__ import annotations
from spyke.audio import ALBuffer
from ..resource import Resource
from uuid import UUID

class Sound(Resource):
    def __init__(self, _id: UUID, filepath: str=''):
        super().__init__(_id, filepath)

        self.buffer: ALBuffer

    def _unload(self) -> None:
        self.buffer.delete()
