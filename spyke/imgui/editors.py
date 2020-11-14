from ..utils import Abstract

import tkinter

class TransformEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.__rotMin = -360.0
		self.__rotMax = 360.0
		self.__posMin = -999.0
		self.__posMax = 999.0
		self.__scaleMin = 0.0
		self.__scaleMax = 999.0

		#region Variables
		self.rotVar = tkinter.StringVar(name = "rot")
		self.xPosVar = tkinter.StringVar(name = "xPos")
		self.yPosVar = tkinter.StringVar(name = "yPos")
		self.xScaleVar = tkinter.StringVar(name = "xScale")
		self.yScaleVar = tkinter.StringVar(name = "yScale")
		#endregion

		#region Labels
		self.posLabel = tkinter.Label(self, text = "Position: ", bg = "white", anchor = "w")
		self.scaleLabel = tkinter.Label(self, text = "Scale: ", bg = "white", anchor = "w")
		self.rotLabel = tkinter.Label(self, text = "Rotation: ", bg = "white", anchor = "w")

		self.xLabel1 = tkinter.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel1 = tkinter.Label(self, text = "Y: ", bg = "white", anchor = "w")
		self.xLabel2 = tkinter.Label(self, text = "X: ", bg = "white", anchor = "w")
		self.yLabel2 = tkinter.Label(self, text = "Y: ", bg = "white", anchor = "w")
		#endregion

		#region Entries
		self.xPosEntry = tkinter.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.xPosVar)
		self.yPosEntry = tkinter.Spinbox(self, from_ = self.__posMin, to = self.__posMax, increment = 0.01, textvariable = self.yPosVar)

		self.xScaleEntry = tkinter.Spinbox(self, from_ = self.__scaleMin, to = self.__scaleMax, increment = 0.01, textvariable = self.xScaleVar)
		self.yScaleEntry = tkinter.Spinbox(self, from_ = self.__scaleMin, to = self.__scaleMax, increment = 0.01, textvariable = self.yScaleVar)

		self.rotEntry = tkinter.Spinbox(self, from_ = self.__rotMin, to = self.__rotMax, increment = 0.1, textvariable = self.rotVar)
		#endregion
	
		self.rotVar.trace_add("write", self.__EntryCallback)
		self.xPosVar.trace_add("write", self.__EntryCallback)
		self.yPosVar.trace_add("write", self.__EntryCallback)
		self.xScaleVar.trace_add("write", self.__EntryCallback)
		self.yScaleVar.trace_add("write", self.__EntryCallback)

		self.comp = None

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

		text = var.get()

		try:
			n = float(text)
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

class TextEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.textVar = tkinter.StringVar(name = "text")
		self.sizeVar = tkinter.StringVar(name = "size")

		self.__sizeMin = 1
		self.__sizeMax = 999

		self.sizeLabel = tkinter.Label(self, text = "Size: ", bg = "white", anchor = "w")
		self.textEntry = tkinter.Entry(self, textvariable = self.textVar)
		self.sizeEntry = tkinter.Spinbox(self, from_ = self.__sizeMin, to = self.__sizeMax, textvariable = self.sizeVar)

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

class ColorEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.redSlider = tkinter.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "red")
		self.greenSlider = tkinter.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "green")
		self.blueSlider = tkinter.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "blue")
		self.alphaSlider = tkinter.Scale(self, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.__SliderCallback, bg = "#e8eaed")

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