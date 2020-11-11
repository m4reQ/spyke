from ..utils import Abstract

import tkinter

class TransformEditor(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)

		self.__rotMin = -360.0
		self.__rotMax = 360.0

		self.rotVar = tkinter.StringVar()
		self.xPosVar = tkinter.StringVar()
		self.yPosVar = tkinter.StringVar()

		self.posLabel = tkinter.Label(master, text = "Position: ")
		self.scaleLabel = tkinter.Label(master, text = "Scale: ")
		self.rotLabel = tkinter.Label(master, text = "Rotation: ")

		self.xLabel = tkinter.Label(master, text = "X: ")
		self.yLabel = tkinter.Label(master, text = "Y: ")

		self.xPosEntry = tkinter.Spinbox(master)
		self.yPosEntry = tkinter.Spinbox(master)

		self.xScaleEntry = tkinter.Spinbox(master)
		self.yScaleEntry = tkinter.Spinbox(master)

		self.rotEntry = tkinter.Spinbox(master, from_ = self.__rotMin, to = self.__rotMax, resolution = 0.1, textvariable = self.rotVar)
	
		self.rotVar.trace_add("write", self.__EditRot)

		self.comp = None
	
	def Use(self):
		self.posLabel.pack(fill = "x", expand = False)
		self.xLabel.pack(side = "left", expand = False)
		self.xPosEntry.pack(fill = "x", expand = False)
		self.yLabel.pack(side = "left", expand = False)
		self.yPosEntry.pack(fill = "x", expand = False)
	
	def Forget(self):
		self.xPosEntry.forget()
		self.yPosEntry.forget()
		self.xScaleEntry.forget()
		self.yScaleEntry.forget()
		self.rotEntry.forget()
	
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
	
	def __EditRot(self, *args):
		valid = False
		text = self.rotVar.get()

		if text.isdigit():
			n = int(text)
			if (n >= self.__rotMin and n <= self.__rotMax):
				valid = True
		
		if valid:
			self.comp.Rotation = n

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
		self.entry.pack(fill = "x", expand = False)
		self.sizeLabel.pack(expand = False, anchor = "top")#, side = "left")
		self.size.pack(expand = False, anchor = "top", fill = "x")#, side = "right", fill = "x")

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
		self.redSlider.pack(fill = "x", expand = False)
		self.greenSlider.pack(fill = "x", expand = False)
		self.blueSlider.pack(fill = "x", expand = False)
		self.alphaSlider.pack(fill = "x", expand = False)
	
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