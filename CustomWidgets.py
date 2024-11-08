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
    def __init__(self, master=None, values: List[str] = [""], textVar: ttk.Variable | None = None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Almacenar valores y selecciones
        self.list_values = values
        self.selected_values: List[str] = []
        self._textVariable = textVar if textVar else tk.StringVar()
        
        # Asociar la función de limpieza cuando `self._textVariable` cambia
        self._textVariable.trace_add("write", self._on_textvariable_change)
        
        # Frame para mostrar las selecciones
        self._selected_values_frame = ttk.Frame(self)
        self._selected_values_frame.grid(row=0, column=0, sticky="nsew")
        
        # Canvas para desplazamiento horizontal
        self._canvas = ttk.Canvas(self._selected_values_frame, height=30, width=170)
        self._xScroll = ttk.Scrollbar(self._selected_values_frame, orient="horizontal", command=self._canvas.xview, bootstyle="info-rounded") # type: ignore
        self._canvas.config(xscrollcommand=self._xScroll.set)
        
        # Frame dentro del Canvas para contener las selecciones
        self._show_selection_frame = ttk.Frame(self._canvas)
        self._canvas.create_window((0, 0), window=self._show_selection_frame, anchor="nw")
        
        # Configurar grid y eventos de redimensionamiento
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._xScroll.grid(row=1, column=0, sticky="ew")
        self._xScroll.grid_remove()  # Ocultar el scroll inicialmente
        
        # Configurar el grid y eventos de redimensionamiento
        self._selected_values_frame.grid_columnconfigure(0, weight=1)
        self._canvas.bind("<Configure>", self._update_scroll_visibility)
        
        
        self._selected_values_frame.grid_columnconfigure(0, weight=1)
        
        self._add_values_lbl = ttk.Label(self, text="+", style="Custom.TLabel")
        self._add_values_lbl.grid(row=0, column=1, sticky="nsew")
        self._add_values_lbl.bind("<Button-1>", lambda e: self.showList() if self._add_values_lbl.cget("text") == "+" else self.hideList())
        
        self._canvas.bind("<Button-1>", lambda e: self.showList() if self._add_values_lbl.cget("text") == "+" else self.hideList())
        
        # Configurar el grid principal
        self.grid_columnconfigure(0, weight=1)
      
    def _update_scroll_visibility(self, event=None):
        """Actualiza la visibilidad del scrollbar según el tamaño del contenido."""
        # Obtener el área total del contenido dentro del canvas
        content_bbox = self._canvas.bbox("all")

        # Si el contenido excede el ancho visible del canvas, mostrar el scrollbar
        if content_bbox and content_bbox[2] > self._canvas.winfo_width():
            self._xScroll.grid() # Mostrar el scrollbar
        else:
            self._xScroll.grid_remove()  # Ocultar el scrollbar
    
    def hideList(self):
        for widget in self.top_level_list.winfo_children():
            widget.destroy()
        
        if self.top_level_list:
            self.top_level_list.destroy()
        
        self._add_values_lbl.config(text="+")
        return
    
    def showList(self):
        self._add_values_lbl.config(text="×")
        
        # Mostrar la lista de opciones en un Toplevel
        self.top_level_list = ttk.Toplevel()
        self.top_level_list.wm_overrideredirect(True)
        
        # Vincula el evento FocusOut para que oculte la lista al perder el foco
        self.top_level_list.bind("<FocusOut>", lambda e: self.hideList())
        
        # Obtener la posición de la ventana principal y el tamaño de la pantalla
        widget_x, widget_y = self.winfo_rootx(), self.winfo_rooty()
        widget_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Dimensiones del Toplevel
        top_level_width = self.winfo_width()
        top_level_height = 160

        # Calcula la posición inicial del Toplevel
        x_position = widget_x
        y_position = widget_y + widget_height

        # Ajusta la posición si el Toplevel se sale de la pantalla a la derecha
        if x_position + top_level_width > screen_width:
            x_position = screen_width - top_level_width

        # Ajusta la posición si el Toplevel se sale de la pantalla por abajo
        if y_position + top_level_height > screen_height:
            y_position = widget_y - top_level_height

        # Posicionar el Toplevel ajustado
        self.top_level_list.geometry(f"{top_level_width}x{top_level_height}+{x_position}+{y_position}")
        
        # Listbox con selección múltiple
        listbox = tk.Listbox(self.top_level_list, selectmode="multiple", exportselection=False)
        self._listboxScroll = ttk.Scrollbar(self.top_level_list, orient="vertical", command=listbox.yview, bootstyle="info-rounded") # type: ignore
        listbox.config(yscrollcommand=self._listboxScroll.set)
        
        for value in self.list_values:
            listbox.insert(tk.END, value)
        
        listbox.grid(row=0, column=0, sticky="nsew")
        self._listboxScroll.grid(row=0, rowspan=2, column=1, sticky="ns")
        
        # Vincular el evento de Enter para confirmar la selección
        listbox.bind("<Return>", lambda e: self.update_selection(listbox))
        
        # Botón para confirmar selección
        info_frame = ttk.Frame(self.top_level_list)
        ttk.Label(info_frame, text="Presiona Enter para confirmar\nla seleccion", anchor="center", style="warning.TLabel").pack(side="left", padx=5)
        info_frame.grid(row=1, column=0, sticky="ew")
        
        # Configurar el grid del Toplevel
        self.top_level_list.grid_columnconfigure(0, weight=1)
        self.top_level_list.grid_rowconfigure(0, weight=1)
        
        # Darle el foco al Toplevel para que capture eventos FocusOut
        self.top_level_list.focus_set()

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
        
        # Mostrar cada elemento seleccionado en el frame
        for value in self.selected_values:
            label = ttk.Label(self._show_selection_frame, text=value, relief="solid", padding=(5, 3))
            label.pack(side="left", padx=2, pady=2)
        
        self._canvas.grid_columnconfigure(0, weight=1)
        
        # Actualizar el área de desplazamiento del canvas
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        
        # Verificar si el scroll debe mostrarse
        self._update_scroll_visibility()
        
        # Cerrar el Toplevel
        self.hideList()
    
    def _on_textvariable_change(self, *args):
        # Verificar si el valor de la variable es vacío
        if self._textVariable.get() == "":
            # Limpiar el frame de selecciones y la lista de valores seleccionados
            self.clear_selection()
    
    def clear_selection(self):
        # Limpiar los widgets en el frame de selección
        for widget in self._show_selection_frame.winfo_children():
            widget.destroy()
        
        # Limpiar la lista de valores seleccionados
        self.selected_values = []
        
        # Restablecer la región de desplazamiento a un área mínima
        self._show_selection_frame.config(width=1)
        self._show_selection_frame.update_idletasks()  # Asegúrate de que se haya procesado la eliminación
        
        # Ajusta el tamaño del frame interno a un valor mínimo
        self._canvas.configure(scrollregion=(0, 0, 1, 1))
        self._canvas.update_idletasks()  # Actualiza el canvas para reflejar los cambios

        # Ajusta el scroll_visibility después de limpiar
        self._update_scroll_visibility()
    
    def setValues(self, values: List[str]):
        self.list_values = values

    def getSelection(self):
        if len(self.selected_values) == 0:
            return [""]
        
        return self.selected_values
    
if __name__ == "__main__":
    def limpiar():
        seleccion.set("")
    
    root = ttk.Window(themename="superhero")
    seleccion = ttk.StringVar()
    
    label = MultiChoice(root, textVar=seleccion, border=1, relief="solid")
    label.setValues(listaArgumentos)
    label.pack()
    
    btn_mostrar = ttk.Button(root, text="Mostrar selección", command=lambda: print(seleccion.get()))
    btn_mostrar.pack()
    
    btn_limpiar = ttk.Button(root, text="Limpiar selección", command=limpiar)
    btn_limpiar.pack()
    
    root.mainloop()