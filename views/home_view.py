import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, filedialog
import time, ast, os

class MainWindow(ttk.Window):
    def __init__(self, title="ttkbootstrap", themename="litera", iconphoto='', size=None, position=None, minsize=None, maxsize=None, resizable=None, hdpi=True, scaling=None, transient=None, overrideredirect=False, alpha=1):
        super().__init__(
            title,
            themename,
            iconphoto,
            size,
            position,
            minsize,
            maxsize,
            resizable,
            hdpi,
            scaling,
            transient,
            overrideredirect,
            alpha
        )
        
    