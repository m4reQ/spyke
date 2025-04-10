import dataclasses

import numpy as np

from spyke import debug
from spyke.assets.asset import Asset
from spyke.assets.asset_config import AssetConfig
from spyke.graphics import gl


@dataclasses.dataclass(slots=True)
class ModelLoadData:
    index_data: np.ndarray
    index_count: int
    vertex_data: np.ndarray
    vertex_count: int
    index_type: gl.ElementsType

    @property
    def vertex_data_size(self) -> int:
        return self.vertex_data.nbytes

    @property
    def index_data_size(self) -> int:
        return self.index_data.nbytes

@dataclasses.dataclass(eq=False)
class Model(Asset):
    _vertex_count: int = 0
    _vertex_offset: int = 0
    _index_count: int = 0
    _index_type: gl.ElementsType = gl.ElementsType.UNSIGNED_BYTE

    _buffer: gl.Buffer | None = dataclasses.field(repr=False, init=False, default=None)

    def unload(self):
        if self.is_loaded:
            self._buffer.delete()

    def load_from_data(self, data: ModelLoadData, config: AssetConfig):
        self.post_load(data)

    @debug.profiled
    def post_load(self, load_data: ModelLoadData) -> None:
        # due to the limitation of how buffers are designed we have to first concatenate index data and vertex data
        # on the CPU and then upload it to OpenGL
        # Because of this when loading data we should use one buffer in the first place

        # TODO Change this ugly hack for empty models to something reasonable
        if len(load_data.index_data) == 0 or len(load_data.vertex_data) == 0:
            buffer = gl.Buffer(0, gl.BufferFlag.NONE)
        else:
            # TODO Converting index and vertex data to separate bytes objects and then concatenating them wastes resources and is slow
            data = load_data.index_data.tobytes() + load_data.vertex_data.tobytes()
            buffer = gl.Buffer(len(data), gl.BufferFlag.NONE, data)

        with self._loading_lock:
            self._vertex_count = load_data.vertex_count
            self._index_count = load_data.index_count
            self._index_type = load_data.index_type
            self._vertex_offset = load_data.index_data_size
            self._buffer = buffer

            self.is_loaded = True

    @property
    def buffer(self) -> gl.Buffer:
        return self._buffer # type: ignore[return-value]

    @property
    def index_type(self) -> gl.ElementsType:
        return self._index_type

    @property
    def vertex_offset(self) -> int:
        return self._vertex_offset

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    @property
    def index_count(self) -> int:
        return self._index_count

    def __hash__(self) -> int:
        return hash(self.id)
