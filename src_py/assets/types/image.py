import dataclasses
import typing as t

from pygl import textures

from spyke import debug
from spyke.assets.asset import Asset
from spyke.assets.asset_config import AssetConfig
from spyke.assets.loaders.image_load_data import ImageLoadData
from spyke.graphics import renderer


@dataclasses.dataclass(eq=False)
class Image(Asset):
    _texture: textures.Texture | None = dataclasses.field(repr=False, init=False, default=None)

    def unload(self):
        if self.is_loaded:
            self._texture.delete()

    @debug.profiled('assets')
    def post_load(self, load_data: ImageLoadData):
        with debug.profiled_scope('create_texture'):
            texture = textures.Texture(load_data.specification)

        with debug.profiled_scope('upload_texture_data'):
            textures.set_pixel_unpack_alignment(load_data.unpack_alignment)

            for info in load_data.upload_infos:
                texture.upload(info, load_data.upload_data)

            textures.set_pixel_unpack_alignment(4)

        with self._loading_lock:
            self._texture = texture
            self.is_loaded = True

    @property
    def texture(self) -> textures.Texture:
        # FIXME
        # Realistically user should never try to access texture if the asset is not loaded
        # but if we stick assert here the debugger may crash, trying to display value of texture
        return self._texture # type: ignore[return-value]

@dataclasses.dataclass
class ImageConfig(AssetConfig):
    min_filter: textures.MinFilter
    mag_filter: textures.MagFilter
    mipmap_count: int

    @classmethod
    def default(cls) -> t.Self:
        return cls(textures.MinFilter.LINEAR_MIPMAP_LINEAR, textures.MagFilter.LINEAR, 4)
