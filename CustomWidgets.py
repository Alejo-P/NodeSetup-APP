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