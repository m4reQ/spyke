from spyke.exceptions import SpykeException
from win32com.shell import shell #type: ignore

def get_known_folder_path(folder_id: str) -> str:
    try:
        return shell.SHGetKnownFolderPath(folder_id, 0, 0)
    except Exception as e:
        raise SpykeException(f'Cannot get path to known folder: {e}.')

