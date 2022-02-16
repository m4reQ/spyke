from __future__ import annotations
from .textureData import TextureData, CompressedTextureData
from .fontData import FontData
from .loader import Loader
from . import classes
from typing import Dict, Type
from spyke import debug
import inspect

__all__ = [
    'Loader',
    'TextureData',
    'FontData',
    'CompressedTextureData',
    'get'
]


def _is_loader(obj: Type) -> bool:
    return inspect.isclass(obj) and \
        obj.__name__.endswith('Loader') and \
        not inspect.isabstract(obj) and \
        issubclass(obj, Loader)


def _has_restypes(_type) -> bool:
    return '__restypes__' in dir(_type)


def _register_loaders() -> None:
    modules = inspect.getmembers(classes, lambda x: inspect.ismodule(x))
    for name, module in modules:
        _loaders = inspect.getmembers(module, _is_loader)
        for name, _loader in _loaders:
            assert _has_restypes(
                _loader), f'Loader class {_loader.__name__} has to contain "__restypes__" member'

            if isinstance(_loader.__restypes__, list):
                restypes = _loader.__restypes__
            elif isinstance(_loader.__restypes__, str):
                restypes = [_loader.__restypes__, ]

            for restype in restypes:
                _registered_loaders[restype] = _loader

                debug.log_info(f'Loader {name} for resource type: {restype} registered.')


_registered_loaders: Dict[str, Type[Loader]] = {}
_register_loaders()


def get(restype: str) -> Loader:
    assert restype in _registered_loaders, f'Could not find loader for resource type: {restype}'
    return _registered_loaders[restype]()


def has_loader(restype: str) -> bool:
    return restype in _registered_loaders
