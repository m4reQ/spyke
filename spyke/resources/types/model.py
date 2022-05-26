import uuid
import typing as t

import numpy as np

from .resource import ResourceBase

class Model(ResourceBase):
    quad: uuid.UUID
    
    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.obj']
    
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
        
        return model
    
    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.index_data: t.Optional[np.ndarray] = None
        self.position_data: np.ndarray
        self.texture_coords: np.ndarray
        self.vertices_per_instance: int

    def _unload(self) -> None:
        pass
