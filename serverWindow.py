import ttkbootstrap as ttk
import ttkbootstrap.constants as c
import tkinter as tk
from tkinter import messagebox, filedialog
from Actions import promptUser, configureSyntax, applySintax, centerWindow

class ServerWindow(ttk.Window):
    def __init__(self):
        def mostrarSeleccionArchivo():
            if seleccion := self._tablaArchivos.item(
                    self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '',
                    'values'
                ):
                print(seleccion)
        
        def crearArchivo(nombreArchivo):
            Id_ins = self._tablaArchivos.insert('', 'end', values=(nombreArchivo,))
            self._tablaArchivos.selection_set(Id_ins)
            self._tablaArchivos.focus(Id_ins)
        
        def agregarArchivo():
            archivo = filedialog.askopenfilename()
            if archivo:
                item_id = self._tablaArchivos.insert('', 'end', values=(archivo.split('/')[-1],))
                self._tablaArchivos.selection_set(item_id)
                self._tablaArchivos.focus(item_id)
        
        def eliminarArchivo():
            if seleccion := self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '':
                archivo = self._tablaArchivos.item(seleccion, 'values')[0]
                if messagebox.askyesno('Eliminar archivo', f'¿Está seguro de que desea eliminar el archivo {archivo}?'):
                    self._tablaArchivos.delete(seleccion)
            else:
                messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
        
        super().__init__(themename='superhero')

        self.title('Editor de código')
        self.resizable(False, False)
        
        self._frameTabla = ttk.Frame(self)
        encabezadoTabla = ['Archivos']
        self._tablaArchivos = ttk.Treeview(self._frameTabla, columns=tuple(encabezadoTabla), show='headings', height=20, style='info.Treeview')
        for encabezado in encabezadoTabla:
            self._tablaArchivos.heading(encabezado, text=encabezado)
            self._tablaArchivos.column(encabezado, width=80, anchor='center')
        item_id = self._tablaArchivos.insert('', 'end', values=('index.js',))
        self._tablaArchivos.grid(row=0, column=0, sticky='nsew')
        self._frameTabla.grid(row=0, rowspan=7, column=0, sticky='nsew')
        
        self._tablaArchivos.selection_set(item_id)
        self._tablaArchivos.focus(item_id)
        
        self._tablaArchivos.bind('<<TreeviewSelect>>', lambda event: mostrarSeleccionArchivo())
        
        self._frameOpciones = ttk.Frame(self)
        
        self.botonCreararchivo = ttk.Button(
            self._frameOpciones, 
            text='Crear archivo', 
            style='info.TButton',
            command=lambda: promptUser(
                self,
                'Crear archivo', 
                'Ingrese el nombre del archivo a crear',
                'info', 
                True,
                crearArchivo
            ))
        self.botonCreararchivo.grid(row=0, column=0, sticky='nsew', padx=1)
        self._botonAgregar = ttk.Button(self._frameOpciones, text='Agregar archivo', style='success.TButton', command=agregarArchivo)
        self._botonAgregar.grid(row=0, column=1, sticky='nsew', padx=1)
        self._botonEliminar = ttk.Button(self._frameOpciones, text='Eliminar archivo', style='danger.TButton', command=eliminarArchivo)
        self._botonEliminar.grid(row=0, column=2, sticky='nsew', padx=1)
        self._botonCrearcarpeta = ttk.Button(self._frameOpciones, text='Crear carpeta', style='info.TButton')
        self._botonCrearcarpeta.grid(row=0, column=3, sticky='nsew', padx=1)
        
        self._frameOpciones.grid(row=0, column=1, columnspan=3, sticky='nsew')
        
        self._frameEditor = ttk.Frame(self)
        self._areaTextoEditor = tk.Text(self._frameEditor, wrap='none', undo=True, autoseparators=True)
        self._areaTextoEditor["bg"] = "#282828"
        self._areaTextoEditor["font"] = ("Consolas", 10)
        self._yScroll = ttk.Scrollbar(self._frameEditor, orient='vertical', command=self._areaTextoEditor.yview)
        self._xScroll = ttk.Scrollbar(self._frameEditor, orient='horizontal', command=self._areaTextoEditor.xview)
        self._areaTextoEditor.config(yscrollcommand=self._yScroll.set, xscrollcommand=self._xScroll.set)
        self._areaTextoEditor.grid(row=0, column=0, sticky='nsew')
        self._yScroll.grid(row=0, column=1, sticky='ns')
        self._xScroll.grid(row=1, column=0, sticky='ew')
        self._frameEditor.grid(row=1, rowspan=6, column=1, columnspan=3, sticky='nsew')
        
        configureSyntax(self._areaTextoEditor)
        # Aplicar sintaxis destacada cuando se escribe o pega texto
        self._areaTextoEditor.bind("<KeyRelease>", lambda event: applySintax(self._areaTextoEditor, "javascript"))
        centerWindow(self)
    
    def iniciar(self):
        self.mainloop()
        
if __name__ == '__main__':
    ventana = ServerWindow()
    ventana.iniciar()