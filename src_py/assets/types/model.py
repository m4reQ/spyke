import dataclasses

from pygl.buffers import Buffer, BufferFlags
from pygl.rendering import ElementsType

from spyke import debug
from spyke.assets.asset import Asset
from spyke.assets.asset_config import AssetConfig
from spyke.assets.loaders.model_load_data import ModelLoadData


@dataclasses.dataclass(eq=False)
class Model(Asset):
    _vertex_count: int = 0
    _vertex_offset: int = 0
    _index_count: int = 0
    _index_type: ElementsType = ElementsType.UNSIGNED_BYTE

    _buffer: Buffer | None = dataclasses.field(repr=False, init=False, default=None)

    def unload(self):
        if self.is_loaded:
            self._buffer.delete()

    def load_from_data(self, data: ModelLoadData, config: AssetConfig):
        self.post_load(data)

    @debug.profiled('assets')
    def post_load(self, load_data: ModelLoadData) -> None:
        # TODO Allow for immutable pygl buffers
        buffer = Buffer(load_data.vertex_data_size + load_data.index_data_size, BufferFlags.DYNAMIC_STORAGE_BIT)
        buffer.store(load_data.index_data)
        buffer.store(load_data.vertex_data)
        buffer.transfer()

        with self._loading_lock:
            self._vertex_count = load_data.vertex_count
            self._index_count = load_data.index_count
            self._index_type = load_data.index_type
            self._vertex_offset = load_data.index_data_size
            self._buffer = buffer

            self.is_loaded = True

    @property
    def buffer(self) -> Buffer:
        return self._buffer # type: ignore[return-value]

    @property
    def index_type(self) -> ElementsType:
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
