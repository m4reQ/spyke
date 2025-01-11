import dataclasses
import typing as t

import numpy as np

from pygl.rendering import ElementsType
from spyke.assets.asset import Asset


@dataclasses.dataclass(eq=False)
class Model(Asset):
    _vertex_data: np.ndarray = dataclasses.field(repr=False, init=False)
    _index_data: np.ndarray = dataclasses.field(repr=False, init=False)
    _vertex_count: int = dataclasses.field(init=False)
    _index_count: int = dataclasses.field(init=False)
    _elements_type: ElementsType = dataclasses.field(init=False)

    @property
    def vertex_data(self) -> np.ndarray:
        return self._vertex_data

    @property
    def index_data(self) -> np.ndarray:
        return self._index_data

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    @property
    def index_count(self) -> int:
        return self._index_count

    @property
    def elements_type(self) -> ElementsType:
        return self._elements_type
