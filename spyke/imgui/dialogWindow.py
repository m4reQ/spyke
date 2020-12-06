import tkinter as tk

class DialogWindow(object):
	def __init__(self, master: tk.Frame, title: str, prompt: str):
		self.master = master

		self.top = tk.Toplevel(master)
		self.top.title(title)

		self.label = tk.Label(self.top, text = prompt)
		self.entry = tk.Entry(self.top)
		self.button = tk.Button(self.top, text = "OK", command = self.Exit)

		self.label.pack()
		self.entry.pack()
		self.button.pack()

		self.value = None

	def Exit(self):
		self.value = self.entry.get()
		self.top.destroy()

	def AwaitWindow(self):
		self.master.wait_window(self.top)