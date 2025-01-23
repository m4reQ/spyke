import dataclasses

import numpy as np
from pygl.rendering import ElementsType


@dataclasses.dataclass(slots=True)
class ModelLoadData:
    index_data: np.ndarray
    index_count: int
    vertex_data: np.ndarray
    vertex_count: int
    index_type: ElementsType

    @property
    def vertex_data_size(self) -> int:
        return self.vertex_data.nbytes

    @property
    def index_data_size(self) -> int:
        return self.index_data.nbytes
