from ..graphics.rendering.renderStats import RenderStats

import tkinter as tk

FONT = ("Helvetica", 9)

class StatsWidget(tk.Frame):
	def __init__(self, master: tk.Frame):
		super().__init__(master)

		self.drawsTitleLabel = tk.Label(self, text = "Draws count: ", bg = "white", anchor = "w")
		self.quadsTitleLabel = tk.Label(self, text = "Quads count: ", bg = "white", anchor = "w")
		self.timeTitleLabel = tk.Label(self, text = "Draw time: ", bg = "white", anchor = "w")
		self.fpsTitleLabel = tk.Label(self, text = "FPS: ", bg = "white", anchor = "w")

		self.drawsLabel = tk.Label(self, text = "0", bg = "white", anchor = "e")
		self.quadsLabel = tk.Label(self, text = "0", bg = "white", anchor = "e")
		self.timeLabel = tk.Label(self, text = "0.0", bg = "white", anchor = "e")
		self.fpsLabel = tk.Label(self, text = "0.0", bg = "white", anchor = "e")

		self.drawsTitleLabel.grid(row = 0, column = 0, sticky = "we")
		self.quadsTitleLabel.grid(row = 1, column = 0, sticky = "we")
		self.timeTitleLabel.grid(row = 2, column = 0, sticky = "we")
		self.fpsTitleLabel.grid(row = 3, column = 0, sticky = "we")

		self.drawsLabel.grid(row = 0, column = 1, sticky = "we")
		self.quadsLabel.grid(row = 1, column = 1, sticky = "we")
		self.timeLabel.grid(row = 2, column = 1, sticky = "we")
		self.fpsLabel.grid(row = 3, column = 1, sticky = "we")
	
	def Update(self):
		if not RenderStats.FrameEnded:
			return

		self.drawsLabel["text"] = str(RenderStats.DrawsCount)
		self.quadsLabel["text"] = str(RenderStats.QuadsCount)
		self.timeLabel["text"] = "{0:.5f}".format(RenderStats.DrawTime)
		if RenderStats.DrawTime:
			self.fpsLabel["text"] = "{0:.2f}".format(1.0 / RenderStats.DrawTime)

class ExpandableFrame(tk.Frame):
	def __init__(self, master: tk.Frame, title: str, widgetType: type, **widgetConfig):
		super().__init__(master)

		self.titleLabel = tk.Label(self, text = title, bg = "white", anchor = "w")
		self.expandButton = tk.Button(self, text = "+", bg = "white", bd = 0, command = self.__ButtonCallback)
		self.widget = widgetType(self, **widgetConfig)

		self.titleLabel.grid(row = 0, column = 0, sticky = "we")
		self.expandButton.grid(row = 0, column = 1)

		self.expanded = False
	
	def __ButtonCallback(self):
		if self.expanded:
			self.widget.grid_forget()
			self.expandButton.configure(text = "+")
			self.expanded = False
		else:
			self.widget.grid(row = 1, column = 0, sticky = "news", columnspan = 2)
			self.expandButton.configure(text = "-")
			self.expanded = True

class RenderStatsView(tk.Frame):
	def __init__(self, master: tk.Frame):
		super().__init__(master)

		self.drawsCountNameLabel = tk.Label(self, text = "Draws count: ", font = (*FONT, "bold"), bg = "white", anchor = "w")
		self.verticesCountNameLabel = tk.Label(self, text = "Vertices count: ", font = (*FONT, "bold"), bg = "white", anchor = "w")
		self.memUsedNameLabel = tk.Label(self, text = "Memory used: ", font = (*FONT, "bold"), bg = "white", anchor = "w")
		self.vidMemUsedNameLabel = tk.Label(self, text = "Video memory used: ", font = (*FONT, "bold"), bg = "white", anchor = "w")
		self.winSizeNameLabel = tk.Label(self, text = "Window size: ", font = (*FONT, "bold"), bg = "white", anchor = "w")
		
		self.drawsCountLabel = tk.Label(self, text = "", bg = "white")
		self.verticesCountLabel = tk.Label(self, text = "", bg = "white")
		self.memUsedLabel = tk.Label(self, text = "", bg = "white")
		self.vidMemUsedLabel = tk.Label(self, text = "", bg = "white")
		self.winSizeLabel = tk.Label(self, text = "", bg = "white")

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)

		self.drawsCountNameLabel.grid(row = 0, column = 0)
		self.drawsCountLabel.grid(row = 0, column = 1, sticky = "we")
		self.verticesCountNameLabel.grid(row = 1, column = 0)
		self.verticesCountLabel.grid(row = 1, column = 1, sticky = "we")
		self.memUsedNameLabel.grid(row = 2, column = 0)
		self.memUsedLabel.grid(row = 2, column = 1, sticky = "we")
		self.vidMemUsedNameLabel.grid(row = 3, column = 0)
		self.vidMemUsedLabel.grid(row = 3, column = 1, sticky = "we")
		self.winSizeNameLabel.grid(row = 4, column = 0)
		self.winSizeLabel.grid(row = 4, column = 1, sticky = "we")

	def Update(self, drawsN: int, vertN: int, memUsed: float, vidMemUsed: float, winSize: tuple) -> None:
		self.drawsCountLabel.configure(text = str(drawsN))
		self.verticesCountLabel.configure(text = str(vertN))
		self.memUsedLabel.configure(text = str(memUsed))
		self.vidMemUsedLabel.configure(text = str(vidMemUsed))
		self.winSizeLabel.configure(text = f"{winSize[0]}x{winSize[1]}")

		self.update()

class LineEditor(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.__posMin = -999.0
		self.__posMax = 999.0

		#region Variables
		self.xPosVar1 = tk.StringVar(name = "xPos1")
		self.yPosVar1 = tk.StringVar(name = "yPos1")
		self.xPosVar2 = tk.StringVar(name = "xPos2")
		self.yPosVar2 = tk.StringVar(name = "yPos2")
		#endregion

		#region Labels
		self.beginLabel = tk.Label(self, text = "Begin", bg = "white", anchor = "w", font = (*FONT, "bold"))
		self.endLabel = tk.Label(self, text = "End", bg = "white", anchor = "w", font = (*FONT, "bold"))
		self.xLabel1 = tk.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel1 = tk.Label(self, text = "Y: ", bg = "white", anchor = "w")
		self.xLabel2 = tk.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel2 = tk.Label(self, text = "Y: ", bg = "white", anchor = "w")
		#endregion

		#region Entries
		self.xPosEntry1 = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.xPosVar1)
		self.yPosEntry1 = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.yPosVar1)
		self.xPosEntry2 = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.xPosVar2)
		self.yPosEntry2 = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.yPosVar2)
		#endregion

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)

		self.beginLabel.grid(row = 0, column = 0, sticky = "we", columnspan = 2)
		self.xLabel1.grid(row = 1, column = 0, sticky = "we")
		self.xPosEntry1.grid(row = 1, column = 1, sticky = "news")
		self.yLabel1.grid(row = 2, column = 0, sticky = "we")
		self.yPosEntry1.grid(row = 2, column = 1, sticky = "news")

		self.endLabel.grid(row = 3, column = 0, sticky = "we", columnspan = 2)
		self.xLabel2.grid(row = 4, column = 0, sticky = "we")
		self.xPosEntry2.grid(row = 4, column = 1, sticky = "news")
		self.yLabel2.grid(row = 5, column = 0, sticky = "we")
		self.yPosEntry2.grid(row = 5, column = 1, sticky = "news")
		#endregion
		
		self.xPosVar1.trace_add("write", self.__EntryCallback)
		self.yPosVar1.trace_add("write", self.__EntryCallback)
		self.xPosVar2.trace_add("write", self.__EntryCallback)
		self.yPosVar2.trace_add("write", self.__EntryCallback)

		self.comp = None

	def __EntryCallback(self, name, *args):
		if name == "xPos1":
			var = self.xPosVar1
		elif name == "yPos1":
			var = self.yPosVar1
		elif name == "xPos2":
			var = self.xPosVar2
		elif name == "yPos2":
			var = self.yPosVar2

		try:
			n = float(var.get())
		except ValueError:
			return
		
		if name == "xPos1":
			self.comp.StartPos.x = n
		elif name == "yPos1":
			self.comp.StartPos.y = n
		elif name == "xPos2":
			self.comp.EndPos.x = n
		elif name == "yPos2":
			self.comp.EndPos.y = n
		
	def SetComp(self, comp):
		self.comp = comp

		self.xPosVar1.set(comp.StartPos.x)
		self.yPosVar1.set(comp.StartPos.y)
		self.xPosVar2.set(comp.EndPos.x)
		self.yPosVar2.set(comp.EndPos.y)

		self.xPosEntry1.delete(0, "end")
		self.xPosEntry1.insert(0, comp.StartPos.x)
		self.yPosEntry1.delete(0, "end")
		self.yPosEntry1.insert(0, comp.StartPos.y)

		self.xPosEntry2.delete(0, "end")
		self.xPosEntry2.insert(0, comp.EndPos.x)
		self.yPosEntry2.delete(0, "end")
		self.yPosEntry2.insert(0, comp.EndPos.y)

class ScriptEditor(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.filepathNameLabel = tk.Label(self, text = "Filepath: ", anchor = "w", bg = "white", font = ("Helvetica", 9, "bold"))
		self.filepathLabel = tk.Label(self, text = "", bg = "white", anchor = "w", font = ("Helvetica", 9, "italic"))
		self.previewText = tk.Text(self, bg = "white", font = ("Helvetica", 6), height = 11, width = 30)

		self.comp = None

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)
		self.filepathNameLabel.grid(row = 0, column = 0, sticky = "we")
		self.filepathLabel.grid(row = 0, column = 1, sticky = "we")
		self.previewText.grid(row = 1, column = 0, columnspan = 2, sticky = "news")
		#endregion

	def SetComp(self, comp):
		self.comp = comp

		self.filepathLabel.configure(text = comp.Filepath)
		self.previewText.configure(state = "normal")
		with open(comp.Filepath, "r") as f:
			for _ in range(10):
				line = f.readline()
				self.previewText.insert("end", line)
			
		self.previewText.insert("end", "...")
		self.previewText.configure(state = "disabled")

class TransformEditor(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.__rotMin = -360.0
		self.__rotMax = 360.0
		self.__posMin = -999.0
		self.__posMax = 999.0
		self.__scaleMin = 0.0
		self.__scaleMax = 999.0

		#region Variables
		self.rotVar = tk.StringVar(name = "rot")
		self.xPosVar = tk.StringVar(name = "xPos")
		self.yPosVar = tk.StringVar(name = "yPos")
		self.xScaleVar = tk.StringVar(name = "xScale")
		self.yScaleVar = tk.StringVar(name = "yScale")
		#endregion

		#region Labels
		self.posLabel = tk.Label(self, text = "Position: ", bg = "white", anchor = "w")
		self.scaleLabel = tk.Label(self, text = "Scale: ", bg = "white", anchor = "w")
		self.rotLabel = tk.Label(self, text = "Rotation: ", bg = "white", anchor = "w")

		self.xLabel1 = tk.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel1 = tk.Label(self, text = "Y: ", bg = "white", anchor = "w")
		self.xLabel2 = tk.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel2 = tk.Label(self, text = "Y: ", bg = "white", anchor = "w")
		#endregion

		#region Entries
		self.xPosEntry = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.xPosVar)
		self.yPosEntry = tk.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.yPosVar)

		self.xScaleEntry = tk.Spinbox(self, from_ = self.__scaleMin, to = self.__scaleMax, increment = 0.01, textvariable = self.xScaleVar)
		self.yScaleEntry = tk.Spinbox(self, from_ = self.__scaleMin, to = self.__scaleMax, increment = 0.01, textvariable = self.yScaleVar)

		self.rotEntry = tk.Spinbox(self, from_ = self.__rotMin, to = self.__rotMax, increment = 0.1, textvariable = self.rotVar)
		#endregion

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)

		self.posLabel.grid(row = 0, column = 0, sticky = "we", columnspan = 2)
		self.xLabel1.grid(row = 1, column = 0, sticky = "we")
		self.xPosEntry.grid(row = 1, column = 1, sticky = "news")
		self.yLabel1.grid(row = 2, column = 0, sticky = "we")
		self.yPosEntry.grid(row = 2, column = 1, sticky = "news")
		
		self.scaleLabel.grid(row = 3, column = 0, sticky = "we", columnspan = 2)
		self.xLabel2.grid(row = 4, column = 0, sticky = "we")
		self.xScaleEntry.grid(row = 4, column = 1, sticky = "news")
		self.yLabel2.grid(row = 5, column = 0, sticky = "we")
		self.yScaleEntry.grid(row = 5, column = 1, sticky = "news")

		self.rotLabel.grid(row = 6, column = 0, sticky = "we", columnspan = 2)
		self.rotEntry.grid(row = 7, column = 0, sticky = "we", columnspan = 2)
		#endregion

		self.rotVar.trace_add("write", self.__EntryCallback)
		self.xPosVar.trace_add("write", self.__EntryCallback)
		self.yPosVar.trace_add("write", self.__EntryCallback)
		self.xScaleVar.trace_add("write", self.__EntryCallback)
		self.yScaleVar.trace_add("write", self.__EntryCallback)

		self.comp = None

	def SetComp(self, comp):
		self.comp = comp

		self.xPosVar.set(comp.Position.x)
		self.yPosVar.set(comp.Position.y)
		self.xScaleVar.set(comp.Size.x)
		self.yScaleVar.set(comp.Size.y)
		self.rotVar.set(comp.Rotation)

		self.xPosEntry.delete(0, "end")
		self.xPosEntry.insert(0, comp.Position.x)
		self.yPosEntry.delete(0, "end")
		self.yPosEntry.insert(0, comp.Position.y)

		self.xScaleEntry.delete(0, "end")
		self.xScaleEntry.insert(0, comp.Size.x)
		self.yScaleEntry.delete(0, "end")
		self.yScaleEntry.insert(0, comp.Size.y)

		self.rotEntry.delete(0, "end")
		self.rotEntry.insert(0, comp.Rotation)
	
	def __EntryCallback(self, name, *args):
		if name == "rot":
			var = self.rotVar
		elif name == "xPos":
			var = self.xPosVar
		elif name == "yPos":
			var = self.yPosVar
		elif name == "xScale":
			var = self.xScaleVar
		elif name == "yScale":
			var = self.yScaleVar

		try:
			n = float(var.get())
			if name == "rot":
				if not (n >= self.__rotMin and n <= self.__rotMax):
					return
		except ValueError:
			return
		
		if name == "rot":
			self.comp.Rotation = n
		elif name == "xPos":
			self.comp.Position.x = n
		elif name == "yPos":
			self.comp.Position.y = n
		elif name == "xScale":
			self.comp.Size.x = n
		elif name == "yScale":
			self.comp.Size.y = n

class TextEditor(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.textVar = tk.StringVar(name = "text")
		self.sizeVar = tk.StringVar(name = "size")

		self.__sizeMin = 1
		self.__sizeMax = 999

		self.sizeLabel = tk.Label(self, text = "Size: ", bg = "white", anchor = "w")
		self.textEntry = tk.Entry(self, textvariable = self.textVar)
		self.sizeEntry = tk.Spinbox(self, from_ = self.__sizeMin, to = self.__sizeMax, textvariable = self.sizeVar)

		self.textVar.trace_add("write", self.__EntryCallback)
		self.sizeVar.trace_add("write", self.__EntryCallback)

		self.comp = None

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.grid_columnconfigure(1, weight = 1)
		self.textEntry.grid(row = 0, column = 0, columnspan = 2, sticky = "ew")
		self.sizeLabel.grid(row = 1, column = 0, sticky = "ew")
		self.sizeEntry.grid(row = 1, column = 1, sticky = "ew")
		#endregion

	def __EntryCallback(self, name, *args):
		if name == "text":
			self.comp.Text = self.textVar.get()
		elif name == "size":
			try:
				n = int(self.sizeVar.get())
				if not (n >= self.__sizeMin and n <= self.__sizeMax):
					return
			except ValueError:
				return
			
			self.comp.Size = n
	
	def SetComp(self, comp):
		self.comp = comp

		oldText = comp.Text
		self.textEntry.delete(0, "end")
		self.textEntry.insert(0, oldText)

		oldSize = comp.Size
		self.sizeEntry.delete(0, "end")
		self.sizeEntry.insert(0, oldSize)

class ColorEditor(tk.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.redSlider = tk.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "red")
		self.greenSlider = tk.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "green")
		self.blueSlider = tk.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "blue")
		self.alphaSlider = tk.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "#e8eaed")

		self.comp = None

		#region Grid
		self.grid_columnconfigure(0, weight = 1)
		self.redSlider.grid(row = 0, column = 0, sticky = "ew")
		self.greenSlider.grid(row = 1, column = 0, sticky = "ew")
		self.blueSlider.grid(row = 2, column = 0, sticky = "ew")
		self.alphaSlider.grid(row = 3, column = 0, sticky = "ew")
		#endregion
	
	def __SliderCallback(self, _):
		if not self.comp:
			return

		self.comp.R = self.redSlider.get()
		self.comp.G = self.greenSlider.get()
		self.comp.B = self.blueSlider.get()
		self.comp.A = self.alphaSlider.get()
	
	def SetComp(self, comp):
		self.comp = comp

		self.redSlider.set(comp.R)
		self.greenSlider.set(comp.G)
		self.blueSlider.set(comp.B)
		self.alphaSlider.set(comp.A)