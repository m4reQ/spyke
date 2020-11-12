from ..utils import Abstract

import tkinter

class TransformEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.__rotMin = -360.0
		self.__rotMax = 360.0

		self.rotVar = tkinter.StringVar(name = "rot")
		self.xPosVar = tkinter.StringVar(name = "xPos")
		self.yPosVar = tkinter.StringVar(name = "yPos")
		self.xScaleVar = tkinter.StringVar(name = "xScale")
		self.yScaleVar = tkinter.StringVar(name = "yScale")

		self.posLabel = tkinter.Label(master, text = "Position: ", bg = "white")
		self.scaleLabel = tkinter.Label(master, text = "Scale: ", bg = "white")
		self.rotLabel = tkinter.Label(master, text = "Rotation: ", bg = "white")

		self.xLabel = tkinter.Label(master, text = "X: ", bg = "white")
		self.yLabel = tkinter.Label(master, text = "Y: ", bg = "white")

		self.xPosEntry = tkinter.Spinbox(master, increment = 0.1, textvariable = self.xPosVar)
		self.yPosEntry = tkinter.Spinbox(master, increment = 0.1, textvariable = self.yPosVar)

		self.xScaleEntry = tkinter.Spinbox(master, increment = 0.1, textvariable = self.xScaleVar)
		self.yScaleEntry = tkinter.Spinbox(master, increment = 0.1, textvariable = self.xScaleVar)

		self.rotEntry = tkinter.Spinbox(master, from_ = self.__rotMin, to = self.__rotMax, increment = 0.1, textvariable = self.rotVar)
	
		self.rotVar.trace_add("write", self.__EntryCallback)
		self.xPosVar.trace_add("write", self.__EntryCallback)
		self.yPosVar.trace_add("write", self.__EntryCallback)
		self.xScaleVar.trace_add("write", self.__EntryCallback)
		self.yScaleVar.trace_add("write", self.__EntryCallback)

		self.comp = None
	
	def Use(self):
		self.posLabel.grid(row = 0, column = 0)
		self.xLabel.grid(row = 1, column = 0)
		self.xPosEntry.grid(row = 1, column = 1)
		self.yLabel.grid(row = 2, column = 0)
		self.yPosEntry.grid(row = 2, column = 1)

		# self.scaleLabel.pack(expand = False, fill = "x")
		# self.xLabel.pack(expand = False, side = "left")
		# self.xScaleEntry.pack(expand = False, side = "right", fill = "x")
		# self.yLabel.pack(expand = False, side = "left")
		# self.yScaleEntry.pack(expand = False, side = "right", fill = "x")
		# self.rotLabel.pack(expand = False, side = "left")
		# self.rotEntry.pack(expand = False, side = "left")
	
	def Forget(self):
		self.xPosEntry.grid_forget()
		self.yPosEntry.grid_forget()
		self.xScaleEntry.grid_forget()
		self.yScaleEntry.grid_forget()
		self.rotEntry.grid_forget()
	
	def SetComp(self, comp):
		self.comp = comp

		self.xPosVar.set(comp.Position.x)
		self.yPosVar.set(comp.Position.y)
		self.rotVar.set(comp.Rotation)

		self.xPosEntry.delete(0, "end") 
		self.xPosEntry.insert(0, comp.Position.x)
		self.yPosEntry.delete(0, "end") 
		self.yPosEntry.insert(0, comp.Position.y)

		self.rotEntry.delete(0, "end")
		self.rotEntry.insert(0, comp.Rotation)
	
	def __EntryCallback(self, name, *args):
		valid = False
		text = self.rotVar.get()

		if text.isdigit():
			n = int(text)
			if (n >= self.__rotMin and n <= self.__rotMax):
				valid = True
		
		if not valid:
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

		self.var = tkinter.StringVar()
		self.sizeVar = tkinter.StringVar()

		self.__sizeMin = 0
		self.__sizeMax = 999

		self.entry = tkinter.Entry(master, textvariable = self.var)
		self.sizeLabel = tkinter.Label(master, text = "Size: ", bg = "white")
		self.size = tkinter.Spinbox(master, from_ = self.__sizeMin, to = self.__sizeMax, textvariable = self.sizeVar)

		self.var.trace_add("write", self.EditText)
		self.sizeVar.trace_add("write", self.EditSize)

		self.comp = None

	def EditSize(self, *args):
		valid = False
		text = self.sizeVar.get()
		if text.isdigit():
			n = int(text)
			if (n >= self.__sizeMin and n <= self.__sizeMax):
				valid = True
		
		if valid:
			self.comp.Size = n

	def EditText(self, *args):
		self.comp.Text = self.var.get()
	
	def SetComp(self, comp):
		self.comp = comp
		self.var.set(comp.Text)
		self.size.delete(0, "end")
		self.size.insert(0, comp.Size)

	def Use(self):
		self.entry.pack(expand = False, fill = "x", anchor = "n")
		self.sizeLabel.pack(expand = False, anchor = "n", side = "left")
		self.size.pack(expand = False, anchor = "n", side = "right", fill = "x")

	def Forget(self):
		self.entry.forget()
		self.size.forget()
		self.sizeLabel.forget()

class ColorEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.redSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues, bg = "red")
		self.greenSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues, bg = "green")
		self.blueSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues, bg = "blue")
		self.alphaSlider = tkinter.Scale(master, from_ = 0.0, to = 1.0, resolution = 0.01, orient = "horizontal", command = self.ChangeValues, bg = "#e8eaed")

		self.comp = None
	
	def ChangeValues(self, _):
		if not self.comp:
			return

		self.comp.R = self.redSlider.get()
		self.comp.G = self.greenSlider.get()
		self.comp.B = self.blueSlider.get()
		self.comp.A = self.alphaSlider.get()

	def Use(self):
		self.redSlider.pack(fill = "x", expand = False, anchor = "n")
		self.greenSlider.pack(fill = "x", expand = False, anchor = "n")
		self.blueSlider.pack(fill = "x", expand = False, anchor = "n")
		self.alphaSlider.pack(fill = "x", expand = False, anchor = "n")
	
	def Forget(self):
		self.redSlider.forget()
		self.greenSlider.forget()
		self.blueSlider.forget()
		self.alphaSlider.forget()
	
	def SetComp(self, comp):
		self.comp = comp

		self.redSlider.set(comp.R)
		self.greenSlider.set(comp.G)
		self.blueSlider.set(comp.B)
		self.alphaSlider.set(comp.A)