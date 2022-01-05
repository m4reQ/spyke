import tkinter as tk

class ResourcesInfo(tk.Frame):
    def __init__(self, master: tk.Frame):
        super().__init__(master)

        self.title_label = tk.Label(self, text='Resources')
        self.textures_label = tk.Label(self, text='Textures')
        self.textures_list = tk.Listbox(self, state=tk.NORMAL)

    def grid(self):
        pass

    def update(self):
        pass