from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from uuid import UUID

from .resource import Resource
from spyke.enums import PixelType
from spyke import debug
from spyke.utils import convert, loaders
from spyke.graphics.texturing import TextureSpec, Texture
import time
from PIL import Image as _Image


class Image(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture

    def _load_normal(self) -> None:
        pass

    def _load_dds(self) -> None:
        pass

    def _load(self, **_) -> None:
        with _Image.open(self.filepath) as img:
            width = img.width
            height = img.height
            data = loaders.get_image_data(img)

        _format = convert.image_mode_to_texture_format(img.mode)

        # TODO: Add customization of texture specification (in future in form of popup window in editor)
        # Ideally to achive this use texture views
        texture_spec = TextureSpec()
        # TODO: Make this more customizable
        texture_spec.internal_format = convert.texture_format_to_internal_format(
            _format)
        texture_spec.width = width
        texture_spec.height = height

        self._loading_data['spec'] = texture_spec
        self._loading_data['data'] = data
        self._loading_data['format'] = _format

    def _finalize(self) -> None:
        self.texture = Texture(self._loading_data['spec'])
        self.texture.upload(
            None, 0, self._loading_data['format'], PixelType.UnsignedByte, self._loading_data['data'])
        self.texture.generate_mipmap()
        self.texture._check_immutable()

        debug.log_info(
            f'Image from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def _unload(self) -> None:
        self.texture.delete()
