import logging
import colorama

from spyke import paths

LOG_LEVEL: int = logging.DEBUG if __debug__ else logging.WARNING

class _ConsoleFormatter(logging.Formatter):
    _color_map = {
        logging.DEBUG: colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.FATAL: colorama.Back.WHITE + colorama.Fore.RED
    }

    def format(self, record: logging.LogRecord) -> str:
        return self._color_map.get(record.levelno, '') + super().format(record) + colorama.Style.RESET_ALL

class _SpykeLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith('spyke') and super().filter(record)

class SpykeLogger(logging.Logger):
    _log_format: str = '[%(levelname)s][%(asctime)s.%(msecs)03d] (%(threadName)s) %(name)s: %(message)s'
    _log_time_format: str = '%H:%M:%S'

    def __init__(self, name: str):
        super().__init__(name, LOG_LEVEL)

        _file_handler = logging.FileHandler(paths.LOG_FILE)
        _file_handler.setLevel(LOG_LEVEL)
        _file_handler.setFormatter(logging.Formatter(
            fmt=self._log_format,
            datefmt=self._log_time_format
            ))
        self.addHandler(_file_handler)

        _con_handler = logging.StreamHandler()
        _con_handler.setLevel(LOG_LEVEL)
        _con_handler.setFormatter(
            _ConsoleFormatter(
                fmt=self._log_format,
                datefmt=self._log_time_format))
        self.addHandler(_con_handler)

        self.addFilter(_SpykeLogFilter(name))

        self.propagate = False
