from collections.abc import Callable
import tkinter as tk
from typing import Literal
import ttkbootstrap as ttk

from Actions import doNothing

no_callback = lambda x: doNothing()

class SelectionLabel(ttk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._bindsSecuences = {}
        self.type = "normal"
    
    def onClick(self, *, button:Literal["left", "middle", "right",] = "left", callback:Callable[[tk.Event], None] = no_callback):
        if button == "right":
            sequence = "<Button-3>"
        elif button == "left":
            sequence = "<Button-1>"
        elif button == "middle":
            sequence = "<Button-2>"
        else:
            raise ValueError("Invalid button")
        
        self._bindsSecuences[sequence] = self.bind(sequence, callback)
    
    def onDoubleClick(self, *, button:Literal["left", "middle", "right",] = "left", callback:Callable[[tk.Event], None] = no_callback):
        if button == "right":
            sequence = "<Double-Button-3>"
        elif button == "left":
            sequence = "<Double-Button-1>"
        elif button == "middle":
            sequence = "<Double-Button-2>"
        else:
            raise ValueError("Invalid button")
        
        self._bindsSecuences[sequence] = self.bind(sequence, callback)
    
    def getBinds(self):
        return self._bindsSecuences
        
    def deleteBind(self, sequence:str = "<Button-1>"):
        self.unbind(sequence)
        self._bindsSecuences.pop(sequence)

class ScrolledFrame(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = ttk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    
    
        
        