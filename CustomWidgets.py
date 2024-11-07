from collections.abc import Callable
import tkinter as tk
from typing import List, Literal
import ttkbootstrap as ttk

from Actions import doNothing
from Vars import listaArgumentos

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

class MultiChoice(ttk.Frame):
    def __init__(self, master=None, values:List[str] = [""], textVar:ttk.Variable | None=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Almacenar valores y selecciones
        self.list_values = values
        self.selected_values:List[str] = []
        self._ListVar = tk.StringVar()
        self._textVariable = textVar if textVar else tk.StringVar()
        
        # Frame para mostrar las selecciones
        self._selected_values_frame = ttk.Frame(self)
        self._selected_values_frame.grid(row=0, column=0, sticky="nsew")
        
        # Canvas para desplazamiento horizontal
        self._canvas = ttk.Canvas(self._selected_values_frame, height=30, width=170)
        self._xScroll = ttk.Scrollbar(self._selected_values_frame, orient="horizontal", command=self._canvas.xview, bootstyle="success-round") # type: ignore[attr-defined]
        self._canvas.config(xscrollcommand=self._xScroll.set)
        
        # Frame dentro del Canvas para contener las selecciones
        self._show_selection_frame = ttk.Frame(self._canvas)
        self._canvas.create_window((0, 0), window=self._show_selection_frame, anchor="nw")
        
        # Configurar grid y eventos de redimensionamiento
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._xScroll.grid(row=1, column=0, sticky="ew")
        
        # Configurar el scroll para auto-hide
        self._selected_values_frame.bind("<Enter>", lambda e: self._xScroll.grid())
        self._selected_values_frame.bind("<Leave>", lambda e: self._xScroll.grid_remove())
        self._xScroll.grid_remove() # Ocultar el scroll inicialmente
        
        self._selected_values_frame.grid_columnconfigure(0, weight=1)
        self._canvas.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        
        self._add_values_lbl = ttk.Label(self, text="+", style="Custom.TLabel")
        self._add_values_lbl.grid(row=0, column=1, sticky="nsew")
        self._add_values_lbl.bind("<Button-1>", lambda e: self.showList() if self._add_values_lbl.cget("text") == "+" else self.hideList())
        
        # Configurar el grid principal
        self.grid_columnconfigure(0, weight=1)
      
    def hideList(self):
        if self.top_level_list:
            self.top_level_list.destroy()
        
        self._add_values_lbl.config(text="+")
        return
    
    def showList(self):
        self._add_values_lbl.config(text=" - ")
        
        # Mostrar la lista de opciones en un Toplevel
        self.top_level_list = tk.Toplevel(self)
        self.top_level_list.wm_overrideredirect(True)
        
        # Posicionar el Toplevel cerca del botón de agregar
        self.top_level_list.geometry(f"200x150+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}") # Ajustar la posición según la ventana principal
        
        # Listbox con selección múltiple
        listbox = tk.Listbox(self.top_level_list, selectmode="multiple", listvariable=self._ListVar, height=10, exportselection=False)
        self._listboxScroll = ttk.Scrollbar(self.top_level_list, orient="vertical", command=listbox.yview, bootstyle="success-round") # type: ignore[attr-defined]
        listbox.config(yscrollcommand=self._listboxScroll.set)
        
        for value in self.list_values:
            listbox.insert(tk.END, value)
        
        listbox.grid(row=0, column=0, sticky="nsew")
        self._listboxScroll.grid(row=0, rowspan=2, column=1, sticky="ns")
        
        # Botón para confirmar selección
        confirm_button = ttk.Button(self.top_level_list, text="Seleccionar", command=lambda: self.update_selection(listbox), width=10)
        confirm_button.grid(row=1, column=0, sticky="ew")
        
        # Configurar el grid del Toplevel
        self.top_level_list.grid_columnconfigure(0, weight=1)
        self.top_level_list.grid_rowconfigure(0, weight=1)

    def update_selection(self, listbox):
        # Obtener los índices seleccionados
        selected_indices = listbox.curselection()
        
        # Limpiar el frame de selecciones previas
        for widget in self._show_selection_frame.winfo_children():
            widget.destroy()
        
        # Actualizar la lista de valores seleccionados
        self.selected_values = [self.list_values[i] for i in selected_indices]
        
        # Actualizar los valores seleccionados en el texto
        self._textVariable.set(", ".join(self.selected_values))
        
        #TODO: Implementar funcion de limiar los valores seleccionados
        
        # Mostrar cada elemento seleccionado en el frame
        for value in self.selected_values:
            label = ttk.Label(self._show_selection_frame, text=value, relief="solid", padding=(5, 3))
            label.pack(side="left", padx=2, pady=2)
        
        self._canvas.grid_columnconfigure(0, weight=1)
        
        # Actualizar el área de desplazamiento del canvas
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        
        # Cerrar el Toplevel
        self.hideList()
    
    def setValues(self, values:List[str]):
        self.list_values = values

    def getSelection(self):
        if len(self.selected_values) == 0:
            return [""]
        
        return self.selected_values
    
if __name__ == "__main__":
    
    root = ttk.Window(themename="superhero")
    seleccion = ttk.StringVar()
    
    label = MultiChoice(root, textVar=seleccion, border=1, relief="solid")
    label.setValues(listaArgumentos)
    label.pack()
    
    btn_mostrar = ttk.Button(root, text="Mostrar selección", command=lambda: print(seleccion.get()))
    btn_mostrar.pack()
    
    root.mainloop()