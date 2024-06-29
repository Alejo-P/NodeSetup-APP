import tkinter as tk
from tkinter import ttk

class VentanaRegistro(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Registro de eventos")
        self.transient(master)
        self.geometry("500x600")
        self.mensaje = tk.StringVar()
        self.frames = []
        listaFrames = ["Eventos"]
        self.notebook = ttk.Notebook(self)
        for frame in range(len(listaFrames)):
            self.frames.append(ttk.Frame(self.notebook, padding=(10, 10, 10, 10), relief="raised"))
        
        for i, (frame, nombre) in enumerate(zip(self.frames, listaFrames)):
            self.notebook.add(frame, text=nombre)
        self.notebook.pack(expand=True, fill=tk.BOTH)
        self.notebook.select(0)

        # Crear estilo
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # Cambia el tema, puedes probar otros como 'default', 'alt', 'classic', etc.
        
        # Configurar estilos personalizados
        self.style.configure('TFrame', background='#d9d9d9')
        self.style.configure('TNotebook', background='#d9d9d9')
        self.style.configure('TNotebook.Tab', background='#d9d9d9', font=('Helvetica', 12, 'bold'))
        self.style.configure('TEntry', font=('Helvetica', 12))

        # Crear widgets en el primer frame
        self.label_nombre = ttk.Label(self.frames[0], text="Nombre del evento:", font=('Helvetica', 12, 'bold'))
        self.label_nombre.pack(pady=(0, 10), padx=10, anchor='w')

        self.entry_nombre = ttk.Entry(self.frames[0])
        self.entry_nombre.pack(expand=True, fill=tk.BOTH, padx=10)

        self.boton_guardar = ttk.Button(self.frames[0], text="Guardar", command=self.guardar)
        self.boton_guardar.pack(pady=20, padx=10, anchor='e')

    def guardar(self):
        nombre_evento = self.entry_nombre.get()
        print(f"Nombre del evento guardado: {nombre_evento}")

    def mostrar(self):
        self.grab_set()
        self.wait_window()

if __name__ == "__main__":
    root = tk.Tk()
    VentanaRegistro(root).mostrar()
    root.mainloop()
