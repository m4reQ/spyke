from ...constants import DEFAULT_IMGUI_BG_COLOR, DEFAULT_IMGUI_FONT, DEFAULT_IMGUI_HIGLIGHT_COLOR

import tkinter as tk
from tkinter import ttk

TITLE_LABEL_BG_COLOR = "lightgray"

class RenderStatsWidget(tk.Frame):
	def __init__(self, master: tk.Frame):
		super().__init__(master, bg = DEFAULT_IMGUI_BG_COLOR, bd = 2, highlightthickness = 2, highlightcolor = DEFAULT_IMGUI_HIGLIGHT_COLOR)

		self.label = tk.Label(self, text = "Render stats", anchor = "center", bg = TITLE_LABEL_BG_COLOR, font = (*DEFAULT_IMGUI_FONT, "bold"))

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

		self.drawsLabel = self._CreateLabel("", "e")
		self.vertexLabel = self._CreateLabel("", "e")
		self.timeLabel = self._CreateLabel("", "e")
		self.memUsedLabel = self._CreateLabel("", "e")
		self.vidMemUsedLabel = self._CreateLabel("", "e")
		self.winSizeLabel = self._CreateLabel("", "e")
		self.vsyncLabel = self._CreateLabel("", "e")
		self.refreshRateLabel = self._CreateLabel("", "e")

		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)

		self.label.grid(row = 0, column = 0, sticky = "we", columnspan = 2)

		self._GridComponent(self.drawsTitleLabel, self.drawsLabel, 1)
		self._GridComponent(self.vertexTitleLabel, self.vertexLabel, 2)
		self._GridComponent(self.timeTitleLabel, self.timeLabel, 3)
		self.separator1.grid(row = 4, column = 0, sticky = "we", columnspan = 2)
		self._GridComponent(self.memUsedTitleLabel, self.memUsedLabel, 5)
		self._GridComponent(self.vidMemUsedTitleLabel, self.vidMemUsedLabel, 6)
		self.separator2.grid(row = 7, column = 0, sticky = "we", columnspan = 2)
		self._GridComponent(self.winSizeTitleLabel, self.winSizeLabel, 8)
		self._GridComponent(self.vsyncTitleLabel, self.vsyncLabel, 9)
		self._GridComponent(self.refreshRateTitleLabel, self.refreshRateLabel, 10)
	
	def Update(self, drawsCount: int, vertexCount: int, drawTime: float, memUsed: int, vidMemUsed: float, winSize: tuple, vsync: bool, refreshRate: float) -> None:
		self.drawsLabel["text"] = str(drawsCount) if vsync else "disable vsync"
		self.vertexLabel["text"] = str(vertexCount)  if vsync else "disable vsync"
		self.timeLabel["text"] = f"{drawTime:.5f}" if vsync else "disable vsync"
		self.memUsedLabel["text"] = f"{(float(memUsed) / 1024.0):.2f}kB"
		self.vidMemUsedLabel["text"] = str(vidMemUsed) if vidMemUsed else "unavailable"
		self.winSizeLabel["text"] = f"{winSize[0]}x{winSize[1]}"
		self.vsyncLabel["text"] = str(vsync)
		self.refreshRateLabel["text"] = str(refreshRate)
	
	def _CreateLabel(self, text: str, anchor: str) -> tk.Label:
		return tk.Label(self, text = text, bg = DEFAULT_IMGUI_BG_COLOR, anchor = anchor)
	
	def _GridComponent(self, title: tk.Label, value: tk.Label, row: int) -> None:
		title.grid(row = row, column = 0, sticky = "we")
		value.grid(row = row, column = 1, sticky = "we")
