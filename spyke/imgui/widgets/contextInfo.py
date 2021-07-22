from ...enums import Vendor
from ...constants import DEFAULT_IMGUI_BG_COLOR, DEFAULT_IMGUI_FONT, DEFAULT_IMGUI_TITLE_BG_COLOR

import tkinter as tk

class ContextInfoWidget(tk.Frame):
	def __init__(self, master, renderer: str, version: str, glslVersion: str, vendor: Vendor, memoryAvailable: int):
		super().__init__(master)

		self.titleLabel = tk.Label(self, text="Renderer info", anchor="center", bg=DEFAULT_IMGUI_TITLE_BG_COLOR, font=(*DEFAULT_IMGUI_FONT, "bold"))

		self.rendererTitleLabel = self._CreateLabel("Renderer: ", "w")
		self.versionTitleLabel = self._CreateLabel("Version: ", "w")
		self.glslVersionTitleLabel = self._CreateLabel("GLSL version: ", "w")
		self.vendorTitleLabel = self._CreateLabel("Vendor: ", "w")
		self.memoryAvailableTitleLabel = self._CreateLabel("Total video memory: ", "w")

		self.rendererLabel = self._CreateLabel(renderer, "e")
		self.versionLabel = self._CreateLabel(version, "e")
		self.glslVersionLabel = self._CreateLabel(glslVersion, "e")
		self.vendorLabel = self._CreateLabel(vendor, "e")

		memString = f"{memoryAvailable / 1024.0 ** 3}GB" if memoryAvailable else "unavailable"
		self.memoryAvailableLabel = self._CreateLabel(memString, "e")

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)

		self.titleLabel.grid(row=0, column=0, sticky="we", columnspan=2)

		self._GridComponent(self.rendererTitleLabel, self.rendererLabel, 1)
		self._GridComponent(self.versionTitleLabel, self.versionLabel, 2)
		self._GridComponent(self.glslVersionTitleLabel, self.glslVersionLabel, 3)
		self._GridComponent(self.vendorTitleLabel, self.vendorLabel, 4)
		self._GridComponent(self.memoryAvailableTitleLabel, self.memoryAvailableLabel, 5)

	def _CreateLabel(self, text: str, anchor: str) -> tk.Label:
		return tk.Label(self, text = text, bg = DEFAULT_IMGUI_BG_COLOR, anchor = anchor)

	def _GridComponent(self, title: tk.Label, value: tk.Label, row: int) -> None:
		title.grid(row = row, column = 0, sticky = "we")
		value.grid(row = row, column = 1, sticky = "we")
