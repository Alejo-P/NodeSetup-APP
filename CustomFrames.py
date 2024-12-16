import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from tkinter import messagebox
import queue
import threading
import sys
import os

# Agrega el servicio de npm al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from services import npm_service

class TerminalFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.master = master
        self.pack(expand=True, fill="both")
        self.create_widgets()
        self.npm = npm_service.NpmService()
        self.output_queue = queue.Queue()  # Cola para manejar la salida de los comandos
    
    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Área de texto para salida
        self.text = ScrolledText(self, width=100, height=20, autohide=True)
        self.text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Entrada para comandos
        self.entry = ttk.Entry(self)
        self.entry.pack(expand=True, fill="x", padx=5, pady=5)
        
        # Botón para ejecutar comandos
        self.button = ttk.Button(self, text="Ejecutar", command=self.run_command)
        self.button.pack(expand=True, fill="x", padx=5, pady=5)
    
    def run_command(self):
        """Ejecuta el comando ingresado en un hilo separado."""
        command = self.entry.get()
        if not command:
            messagebox.showwarning("Advertencia", "No se ha proporcionado un comando para ejecutar")
            return
        
        # Limpia la entrada
        self.entry.delete(0, tk.END)
        
        # Muestra el comando en la salida
        self.text.insert(tk.END, f"\n> {command}\n")
        self.text.see(tk.END)
        
        # Ejecuta el comando en un hilo separado
        threading.Thread(target=self.execute_command, args=(command,), daemon=True).start()
        self.master.after(100, self.update_output)
    
    def execute_command(self, command):
        """Maneja la ejecución del comando y la salida."""
        try:
            if command.startswith("npm"):  # Comandos relacionados con npm
                output = self.npm._run(command.split(), newWindow=False, allow_input=True)
            else:
                output = f"Comando '{command}' no reconocido."
            
            # Coloca la salida en la cola
            self.output_queue.put(output)
        except Exception as e:
            self.output_queue.put(f"Error: {e}")
    
    def update_output(self):
        """Actualiza la salida en la interfaz en tiempo real."""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.text.insert(tk.END, f"{line}\n")
                self.text.see(tk.END)
        except queue.Empty:
            pass
        
        # Vuelve a comprobar la cola periódicamente
        self.master.after(100, self.update_output)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    root.title("Terminal")
    root.geometry("800x600")
    app = TerminalFrame(root)
    app.mainloop()
