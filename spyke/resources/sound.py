from __future__ import annotations
from uuid import UUID
from spyke.audio import SoundBuffer
from .resource import Resource


class Sound(Resource):
    def __init__(self, _id: UUID, filepath: str):
        super().__init__(_id, filepath)

        self.buffer: SoundBuffer

    def _load(self) -> None:
        self._loading_data = self._loader.load(
            self.filepath, self._resource_type)

    def _finalize(self) -> None:
        self.buffer = self._loader.finalize(self._loading_data)

    def _unload(self) -> None:
        pass
