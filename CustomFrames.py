import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from tkinter import messagebox
import queue, os, shutil, threading, subprocess
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from services import npm_service

class TerminalFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.pack()
        self.create_widgets()
        self.npm = npm_service.NpmService()
        
    def create_widgets(self):
        self.text = ScrolledText(self, width=100, height=20, autohide=True)
        self.text.pack(expand=True, fill='both')
        
        self.entry = ttk.Entry(self)
        self.entry.pack(expand=True, fill='x')
        
        self.button = ttk.Button(self, text="Ejecutar", command=self.run_command)
        self.button.pack(expand=True, fill='x')
        
    def run_command(self):
        command = self.entry.get()
        if not command:
            messagebox.showwarning("Advertencia", "No se ha proporcionado un comando para ejecutar")
            return
        self.text.insert(tk.END, f"{command}\n")
        self.text.insert(tk.END, self.npm._run(command.split(), allow_input=True))
        self.text.insert(tk.END, "\n\n")
        self.entry.delete(0, tk.END)
        
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    root.title("Terminal")
    root.geometry("800x600")
    app = TerminalFrame(root)
    app.mainloop()

