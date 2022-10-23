import types
import inspect
import typing as t

from stdlib_list import stdlib_list

from spyke.debug.profiling import profiled

_KT = t.TypeVar('_KT')

def _is_std_module(module: types.ModuleType) -> bool:
    # TODO: When stdlib_list gets updated to support py 3.10 change this to default
    return module.__name__ in stdlib_list(version='3.9')

def _get_submodules(module: types.ModuleType, scan_stdlib: bool) -> list[types.ModuleType]:
    def _predicate(x: object):
        if inspect.ismodule(x) and not scan_stdlib:
            return not _is_std_module(x) # type: ignore
    
    return [x[1] for x in inspect.getmembers(module, _predicate)]

@profiled('initialization')
def build_class_dict(module: types.ModuleType,
                     predicate: t.Callable[[type], bool],
                     key_builder: t.Callable[[type], list[_KT]],
                     scan_submodules: bool=True,
                     scan_stdlib: bool=False) -> dict[_KT, type]:
    '''
    Creates a dictionary that contains classes retrieved from given module,
    that match given predicate; associated with key created using provided
    key builder function. It can scan submodules and retrieve types from there
    as well. This function will not scan standard library modules by default.
    
    @module: Module from which the types will be queried.
    @predicate: Callable that checks if given type should be added to resulting dictionary.
    @key_builder: Callable that creates key list using retrieved type.
    @scan_submodules: Tells if function should also lookup modules imported in target module.
    @scan_stdlib: Tells if function should query standard library modules while looking for desired types.
    '''
    
    if _is_std_module(module) and not scan_stdlib:
        return {}
    
    to_scan: list[types.ModuleType]
    if scan_submodules:
        to_scan = _get_submodules(module, scan_stdlib)
    else:
        to_scan = [module]
    
    _dict: dict[_KT, type] = {}
    for module in to_scan:
        classes = [x[1] for x in inspect.getmembers(module, predicate)]
        for _class in classes:
            _dict.update({key: _class for key in key_builder(_class)})
    
    return _dict
