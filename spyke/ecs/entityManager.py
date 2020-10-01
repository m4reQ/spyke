from .esper import World as Scene

from functools import lru_cache

class EntityManager:
    __EntityNames = {}
    __Scenes = {}

    @staticmethod
    def CreateEntity(scene: Scene, name: str):
        ent = scene.create_entity()
        EntityManager.__EntityNames[ent] = name
        return ent

    @staticmethod
    def CreateScene(name: str, timed: bool):
        scene = Scene(timed)
        EntityManager.__Scenes[name] = scene
        return scene
    
    @lru_cache
    def GetScene(name: str):
        try:
            return EntityManager.__Scenes[name]
        except KeyError:
            raise RuntimeError(f"Cannot find scene named '{name}'.")
    
    @lru_cache
    def GetEntityName(ent: int):
        try:
            return EntityManager.__EntityNames[ent]
        except KeyError:
            raise RuntimeError(f"Cannot find entity with id: {ent}.")