import uuid

import numpy as np

from .resource import ResourceBase


class Model(ResourceBase):
    __supported_extensions__ = ['.obj']

    @classmethod
    def from_data(cls, uuid: uuid.UUID, data: np.ndarray, vertex_count: int):
        inst = cls(uuid, '')
        inst.data = data
        inst.vertex_count = vertex_count
        inst.is_loaded = True

        return inst

    quad: uuid.UUID

    @classmethod
    def create_quad_model(cls):
        model = cls(uuid.uuid4(), '')
        model.is_internal = True
        model.position_data = np.array([
            0.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            0.0, 1.0, 0.0], dtype=np.float32)
        model.vertices_per_instance = 6
        model.texture_coords = np.array([
            0.0, 1.0,
            1.0, 1.0,
            1.0, 0.0,
            1.0, 0.0,
            0.0, 0.0,
            0.0, 1.0], dtype=np.float32)
        model.is_loaded = True

        return model

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.data = np.empty((0,), dtype=np.float32)
        self.vertex_count = 0
