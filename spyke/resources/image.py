from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from uuid import UUID

from PIL import Image as _Image
import time
from .resource import Resource
from spyke.graphics.texturing import TextureData
from spyke.utils import convert, loaders
from spyke import debug
from spyke.graphics.texturing import TextureSpec, Texture


class Image(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture

    def _load(self, **_) -> None:
        with _Image.open(self.filepath) as img:
            data = loaders.get_image_data(img)
            size = img.size

        texture_data = TextureData(*size)
        texture_data.format = convert.image_mode_to_texture_format(img.mode)
        texture_data.data = data

        # TODO: Add customization of texture specification (in future in form of popup window in editor)
        texture_spec = TextureSpec()

        self._loading_data['texture_spec'] = texture_spec
        self._loading_data['texture_data'] = texture_data

    def _finalize(self) -> None:
        self.texture = Texture(
            self._loading_data['texture_data'], self._loading_data['texture_spec'])

        debug.log_info(
            f'Image from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def _unload(self) -> None:
        self.texture.delete()
