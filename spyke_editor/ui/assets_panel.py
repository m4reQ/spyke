import os
import pathlib
import uuid

import imgui
from pygl.textures import MagFilter, MinFilter, Texture

from spyke import assets, debug
from spyke_editor.ui.editor_panel import EditorPanel

DEFAULT_THUMBNAIL_SIZE = 80.0
DEFAULT_PADDING = 8.0

class AssetsPanel(EditorPanel):
    def __init__(self, path: str) -> None:
        self.thumbnail_size = DEFAULT_THUMBNAIL_SIZE
        self.padding = DEFAULT_PADDING
        self._current_path = _convert_path(path)

        py_icon = _load_file_icon(os.path.join('.', 'spyke_editor', 'assets', 'icons', 'file_py_source_icon.png'))
        sound_icon = _load_file_icon(os.path.join('.', 'spyke_editor', 'assets', 'icons', 'file_sound_icon.png'))
        self._generic_file_icon = _load_file_icon(os.path.join('.', 'spyke_editor', 'assets', 'icons', 'file_generic_icon.png'))
        self._directory_icon = _load_file_icon(os.path.join('.', 'spyke_editor', 'assets', 'icons', 'directory_icon.png'))
        self._file_icons = {
            '.py': py_icon,
            '.wav': sound_icon,
            '.mp3': sound_icon,
            '.ogg': sound_icon,
            '.flc': sound_icon}
        self._cached_thumbnails = dict[str, assets.Image]()

    @property
    def current_path(self) -> str:
        return self._current_path

    @current_path.setter
    def current_path(self, value: str) -> None:
        self._current_path = _convert_path(value)

    def go_to_parent_dir(self) -> None:
        self.current_path = os.path.dirname(self.current_path)

    @debug.profiled
    def render(self) -> None:
        with imgui.begin('Assets'):
            if imgui.arrow_button('Go to parent directory', imgui.DIRECTION_LEFT):
                self.go_to_parent_dir()

            imgui.same_line()
            imgui.text_unformatted(self._current_path)

            panel_width, _ = imgui.get_content_region_available()
            column_count = max(1, int(panel_width / (self.thumbnail_size + self.padding)))

            imgui.columns(column_count, None, False)

            for file in sorted(pathlib.Path(self.current_path).iterdir(), key=lambda x: x.is_dir(), reverse=True):
                image = self._get_icon_image(file)

                imgui.push_id(file.name)
                imgui.image_button(image.texture.id, self.thumbnail_size, self.thumbnail_size, (0, 0), (1, 1))
                if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(imgui.MOUSE_BUTTON_LEFT) and file.is_dir():
                    self.current_path = os.path.join(self.current_path, file.name)
                    imgui.pop_id()

                    break

                imgui.text_wrapped(file.name)
                imgui.next_column()
                imgui.pop_id()

            imgui.columns(1)

    def _get_icon_image(self, path: pathlib.Path) -> assets.Image:
        if path.is_dir():
            return self._directory_icon

        extension = path.suffix.lower()
        if extension in ('.png', '.jpg', '.dds'):
            asset = self._get_thumbnail(str(path))
            if not asset.is_loaded:
                asset = self._generic_file_icon
        else:
            asset = self._file_icons.get(extension, self._generic_file_icon)

        return asset

    def _get_thumbnail(self, filepath: str) -> assets.Image:
        if filepath in self._cached_thumbnails:
            return self._cached_thumbnails[filepath]

        asset_id = assets.load_from_file(assets.Image, filepath, assets.ImageConfig(MinFilter.LINEAR, MagFilter.LINEAR, 1))
        asset = assets.get(assets.Image, asset_id)
        self._cached_thumbnails[filepath] = asset

        return asset

def _convert_path(path: str) -> str:
    return os.path.abspath(path).replace('\\', '/')

def _load_file_icon(path: str) -> assets.Image:
    return assets.load_from_file_immediate(assets.Image, path, assets.ImageConfig(MinFilter.LINEAR, MagFilter.LINEAR, 1))
