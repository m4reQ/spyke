import dataclasses
import typing as t

import numpy as np

from spyke import debug
from spyke.assets.asset import Asset
from spyke.assets.asset_config import AssetConfig
from spyke.graphics import gl, renderer


@dataclasses.dataclass
class ImageLoadData:
    specification: gl.TextureSpec
    upload_infos: list[gl.TextureUploadInfo]
    upload_data: np.ndarray
    unpack_alignment: t.Literal[1, 2, 4, 8] = 4

@dataclasses.dataclass
class ImageConfig(AssetConfig):
    min_filter: gl.MinFilter
    mag_filter: gl.MagFilter
    mipmap_count: int

    @classmethod
    def default(cls) -> t.Self:
        return cls(gl.MinFilter.LINEAR_MIPMAP_LINEAR, gl.MagFilter.LINEAR, 4)

@dataclasses.dataclass(eq=False)
class Image(Asset):
    _texture: gl.Texture | None = dataclasses.field(repr=False, init=False, default=None)

    def load_from_data(self, data: ImageLoadData, config: AssetConfig):
        self.post_load(data)

    def unload(self):
        if self.is_loaded:
            self._texture.delete()

    @debug.profiled
    def post_load(self, load_data: ImageLoadData):
        with debug.profiled_scope('create_texture'):
            texture = gl.Texture(load_data.specification)

        renderer.upload_texture(self, load_data.upload_data, load_data.upload_infos)

        self._texture = texture

    @property
    def texture(self) -> gl.Texture:
        # FIXME
        # Realistically user should never try to access texture if the asset is not loaded
        # but if we stick assert here the debugger may crash, trying to display value of texture
        return self._texture # type: ignore[return-value]

    def __hash__(self) -> int:
        return hash(self.id)
