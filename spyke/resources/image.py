from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from uuid import UUID
    from typing import Union

from .resource import Resource
from spyke import loaders
from spyke.loaders import TextureData, CompressedTextureData
from spyke.enums import PixelType
from spyke import debug
from spyke.utils import convert
from spyke.graphics.texturing import TextureSpec, Texture
import time
from PIL import Image as _Image


class Image(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture

    def _load(self, **_) -> None:
        with _Image.open(self.filepath) as img:
            loader = loaders.get(img.format)
            texture_data = loader.load(img)

        self._loading_data['texture_data'] = texture_data
        # TODO: Add customization of texture specification (in future in form of popup window in editor)
        # Ideally to achive this use texture views

    def _finalize(self) -> None:
        texture_data: Union[TextureData,
                            CompressedTextureData] = self._loading_data['texture_data']

        loader = loaders.get(texture_data.image_format)
        self.texture = loader.finalize(texture_data)

        debug.log_info(
            f'Image from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def _unload(self) -> None:
        self.texture.delete()
