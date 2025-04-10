import dataclasses
import datetime
import hashlib
import json
import logging
import os
import pathlib
import typing as t

from spyke import debug
from spyke.graphics import gl

_INFO_FILENAME = 'cache.json'

@dataclasses.dataclass(slots=True)
class CachedProgram:
    name: str
    hash: str
    created_at: datetime.datetime
    binary_type: int

    @classmethod
    def from_json(cls, data: dict[str, t.Any]) -> t.Self:
        return cls(
            data['name'],
            data['hash'],
            datetime.datetime.fromtimestamp(float(data['created_at'])),
            int(data['binary_type']))

    @property
    def data_filepath(self) -> pathlib.Path:
        return pathlib.Path(f'{self.name}_{self.binary_type}.bin')

class ShaderCache:
    def __init__(self, directory: pathlib.Path | str) -> None:
        self._directory: pathlib.Path
        self._info_filepath: pathlib.Path
        self._cached_programs = dict[str, CachedProgram]()

        self.is_enabled = True

        self.set_directory(directory)

    def is_program_cached(self, name: str) -> bool:
        return name in self._cached_programs

    def get_cached_program_filepath(self, name: str) -> pathlib.Path:
        return self._cached_programs[name].data_filepath

    def clear(self) -> None:
        _logger.info('Clearing shader cache "%s"', self._directory.as_posix())

        for cached_program in self._cached_programs.values():
            path = cached_program.data_filepath
            os.remove(path)
            _logger.debug('Removed cached program "%s" (filepath: %s).', cached_program.name, path.as_posix())

        self._cached_programs.clear()
        self._save_cache_info()

    @debug.profiled
    def load_cached_program_or_create(self, program_name: str, stages: list[gl.ShaderStageInfo], validate_hash: bool = True) -> gl.ShaderProgram:
        if self.is_enabled:
            if self.is_program_cached(program_name):
                _logger.info('Using cached shader program "%s".', program_name)
                return self.load_cached_program(program_name, validate_hash)

            _logger.info('Shader program "%s" not present in the cache. Creating...', program_name)

        program = gl.ShaderProgram(stages)

        if self.is_enabled:
            self.cache_program(program, program_name)

        return program

    @debug.profiled
    def load_cached_program(self, program_name: str, validate_hash: bool = True) -> gl.ShaderProgram:
        if not self.is_enabled:
            _raise_cache_disabled()

        cached_program = self._cached_programs.get(program_name)
        if cached_program is None:
            raise RuntimeError('Program not found in the cache: %s.', program_name)

        filepath = self._get_cached_program_filepath(cached_program)

        with debug.profiled_scope('read_program_binary'):
            binary = filepath.read_bytes()

        if validate_hash:
            self._validate_program_hash(cached_program.hash, binary)

        with debug.profiled_scope('load_program_from_binary'):
            return gl.ShaderProgram.from_binary(binary, cached_program.binary_type)

    @debug.profiled
    def cache_program(self, program: gl.ShaderProgram, name: str) -> pathlib.Path:
        if not self.is_enabled:
            _raise_cache_disabled()

        created_at = datetime.datetime.now()
        binary, binary_type = program.get_binary()
        binary_hash = hashlib.md5(binary).hexdigest()

        cached_program = self._cached_programs.get(name)
        if cached_program is not None:
            if binary_hash == cached_program.hash:
                _logger.info('Shader program "%s" is already present in cache.', name)
                return self._get_cached_program_filepath(cached_program)

            _logger.info('Shader program "%s" is present in cache but binary hash differs. Recreating cache entry...')
            cached_program.hash = binary_hash
            cached_program.created_at = created_at
            cached_program.binary_type = binary_type
        else:
            cached_program = CachedProgram(
                name,
                binary_hash,
                created_at,
                binary_type)
            self._cached_programs[name] = cached_program

        data_filepath = self._get_cached_program_filepath(cached_program)

        self._save_program_binary(data_filepath, binary)
        self._save_cache_info()

        return data_filepath

    def set_directory(self, directory: pathlib.Path | str) -> None:
        if isinstance(directory, str):
            value = pathlib.Path(directory)

        self._directory = value.absolute()

        if not self._directory.exists():
            directory_str = self._directory.as_posix()
            _logger.info('Shader cache directory "%s" does not exist. Creating...', directory_str)
            os.mkdir(directory_str)
        elif not self._directory.is_dir():
            raise RuntimeError(f'Path "{self._directory.as_posix()}" is not a directory.')

        self._info_filepath = self._directory / _INFO_FILENAME
        if not self._info_filepath.exists():
            _logger.info('Shader cache info file "%s" does not exist. Creating...', self._info_filepath.as_posix())
            self._save_cache_info()

        self._load_cache_info()

    @property
    def info_filepath(self) -> pathlib.Path:
        return self._info_filepath

    @property
    def directory(self) -> pathlib.Path:
        return self._directory

    @property
    def cached_programs(self) -> dict[str, CachedProgram]:
        return self._cached_programs

    @debug.profiled
    def _get_cached_program_filepath(self, cached_program: CachedProgram) -> pathlib.Path:
        return self._directory / cached_program.data_filepath

    @debug.profiled
    def _validate_program_hash(self, hash: str, binary: bytes) -> None:
        if hash != hashlib.md5(binary).hexdigest():
            raise RuntimeError('Cached shader program hash differs from expected hash.')

    @debug.profiled
    def _save_cache_info(self) -> None:
        _logger.debug('Saving shader cache info to "%s"...', self._info_filepath.as_posix())

        with self._info_filepath.open('w') as f:
            programs_payload = [
                {
                    'name': x.name,
                    'hash': x.hash,
                    'created_at': x.created_at.timestamp(),
                    'binary_type': x.binary_type,
                }
                for x in self._cached_programs.values()]
            json.dump({'programs': programs_payload}, f)
            f.truncate()

    @debug.profiled
    def _save_program_binary(self, path: pathlib.Path, binary: bytes) -> None:
        _logger.debug('Saving shader program binary to "%s"...', path.as_posix())

        with path.open('wb+') as f:
            f.write(binary)
            f.truncate()

    @debug.profiled
    def _load_cache_info(self) -> None:
        _logger.debug('Reading shader cache info from "%s"...', self._info_filepath.as_posix())

        self._cached_programs.clear()

        data = json.loads(self._info_filepath.read_text())
        for cached_program_data in data.get('programs', []):
            cached_program = CachedProgram.from_json(cached_program_data)
            self._cached_programs[cached_program.name] = cached_program

def get() -> ShaderCache:
    assert _cache is not None
    return _cache

def set(cache: ShaderCache) -> None:
    global _cache
    _cache = cache

def _raise_cache_disabled() -> t.NoReturn:
    raise RuntimeError('Shader cache is disabled.')

_logger = logging.getLogger(__name__)
_cache: ShaderCache | None = None
