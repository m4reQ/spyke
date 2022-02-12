from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from uuid import UUID
    from spyke.graphics import Texture

from .resource import Resource
from PIL import Image as _Image


class Image(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture

    def _load(self, **_) -> None:
        with _Image.open(self.filepath) as img:
            self._loading_data = self._loader.load(img)

        # TODO: Add customization of texture specification (in future in form of popup window in editor)
        # Ideally to achive this use texture views

    def _finalize(self) -> None:
        self.texture = self._loader.finalize(self._loading_data)

    def _unload(self) -> None:
        self.texture.delete()
