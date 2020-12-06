import tkinter as tk

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