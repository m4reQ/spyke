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
    _texture: textures.Texture = dataclasses.field(repr=False, init=False)

    def unload(self):
        self._texture.delete()

    @debug.profiled('assets')
    def post_load(self, load_data: ImageLoadData):
        with debug.profiled_scope('create_texture'):
            texture = textures.Texture(load_data.specification)

        with debug.profiled_scope('upload_texture_data'):
            buffer = renderer.acquire_texture_upload_buffer(
                load_data.specification.width,
                load_data.specification.height,
                load_data.specification.internal_format)

            for info in load_data.upload_infos:
                buffer.store(load_data.upload_data)
                buffer.transfer()
                texture.upload(info, None)

        with self._loading_lock:
            self._texture = texture
            self.is_loaded = True

    @property
    def texture(self) -> textures.Texture:
        return self._texture

@dataclasses.dataclass
class ImageConfig(AssetConfig):
    min_filter: textures.MinFilter
    mag_filter: textures.MagFilter
    mipmap_count: int

    @classmethod
    def default(cls) -> t.Self:
        return cls(textures.MinFilter.LINEAR_MIPMAP_LINEAR, textures.MagFilter.LINEAR, 4)
