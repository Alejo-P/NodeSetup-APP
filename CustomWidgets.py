from collections.abc import Callable
import tkinter as tk
import ttkbootstrap as ttk

from Actions import doNothing

no_callback = lambda x: doNothing()

class SelectionLabel(ttk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._bind_str = ""
        self.type = "normal"
    
    def onClick(self, *, sequence:str = "<Button-1>", callback:Callable[[tk.Event], None] = no_callback):
        if not self._bind_str:
            self._bind_str = self.bind(sequence, callback)
    
    def deleteOnClick(self):
        if self._bind_str:
            self.unbind(self._bind_str)
            self._bind_str = ""