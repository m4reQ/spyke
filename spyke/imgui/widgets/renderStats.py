from ...constants import DEFAULT_IMGUI_BG_COLOR, DEFAULT_IMGUI_FONT, DEFAULT_IMGUI_HIGLIGHT_COLOR, DEFAULT_IMGUI_TITLE_BG_COLOR

import tkinter as tk
from tkinter import ttk

class RenderStatsWidget(tk.Frame):
	def __init__(self, master: tk.Frame):
		super().__init__(master)

		self.titleLabel = tk.Label(self, text = "Render stats", anchor = "center", bg = DEFAULT_IMGUI_TITLE_BG_COLOR, font = (*DEFAULT_IMGUI_FONT, "bold"))

		self.drawsTitleLabel = self._CreateLabel("Draws count: ", "w")
		self.vertexTitleLabel = self._CreateLabel("Vertex count: ", "w")
		self.timeTitleLabel = self._CreateLabel("Draw time: ", "w")
		self.memUsedTitleLabel = self._CreateLabel("Memory used: ", "w")
		self.vidMemUsedTitleLabel = self._CreateLabel("Video memory used: ", "w")
		self.winSizeTitleLabel = self._CreateLabel("Window size: ", "w")
		self.vsyncTitleLabel = self._CreateLabel("Vsync: ", "w")
		self.refreshRateTitleLabel = self._CreateLabel("Refresh rate: ", "w")

		self.separator1 = ttk.Separator(self, orient = "vertical")
		self.separator2 = ttk.Separator(self, orient = "vertical")

		self.drawsCountLabel = self._CreateLabel("", "e")
		self.vertexCountLabel = self._CreateLabel("", "e")
		self.drawTimeLabel = self._CreateLabel("", "e")
		self.memoryUsedLabel = self._CreateLabel("", "e")
		self.videoMemoryUsedLabel = self._CreateLabel("", "e")
		self.windowSizeLabel = self._CreateLabel("", "e")
		self.vsyncLabel = self._CreateLabel("", "e")
		self.refreshRateLabel = self._CreateLabel("", "e")

		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)

		self.titleLabel.grid(row = 0, column = 0, sticky = "we", columnspan = 2)

		self._GridComponent(self.drawsTitleLabel, self.drawsCountLabel, 1)
		self._GridComponent(self.vertexTitleLabel, self.vertexCountLabel, 2)
		self._GridComponent(self.timeTitleLabel, self.drawTimeLabel, 3)
		self.separator1.grid(row = 4, column = 0, sticky = "we", columnspan = 2)
		self._GridComponent(self.memUsedTitleLabel, self.memoryUsedLabel, 5)
		self._GridComponent(self.vidMemUsedTitleLabel, self.videoMemoryUsedLabel, 6)
		self.separator2.grid(row = 7, column = 0, sticky = "we", columnspan = 2)
		self._GridComponent(self.winSizeTitleLabel, self.windowSizeLabel, 8)
		self._GridComponent(self.vsyncTitleLabel, self.vsyncLabel, 9)
		self._GridComponent(self.refreshRateTitleLabel, self.refreshRateLabel, 10)
	
	def Update(self, drawsCount: int, vertexCount: int, drawTime: float, memUsed: int, vidMemUsed: float, winSize: tuple, vsync: bool, refreshRate: float) -> None:
		self.drawsCountLabel["text"] = str(drawsCount)
		self.vertexCountLabel["text"] = str(vertexCount)
		self.drawTimeLabel["text"] = f"{drawTime:.5f}"
		self.memoryUsedLabel["text"] = f"{(memUsed / 1024.0 ** 2):.2f}MB"
		self.videoMemoryUsedLabel["text"] = str(vidMemUsed) if vidMemUsed else "unavailable"
		self.windowSizeLabel["text"] = f"{winSize[0]}x{winSize[1]}"
		self.vsyncLabel["text"] = "enabled" if vsync else "disabled"
		self.refreshRateLabel["text"] = str(refreshRate)
	
	def _CreateLabel(self, text: str, anchor: str) -> tk.Label:
		return tk.Label(self, text = text, bg = DEFAULT_IMGUI_BG_COLOR, anchor = anchor)
	
	def _GridComponent(self, title: tk.Label, value: tk.Label, row: int) -> None:
		title.grid(row = row, column = 0, sticky = "we")
		value.grid(row = row, column = 1, sticky = "we")
