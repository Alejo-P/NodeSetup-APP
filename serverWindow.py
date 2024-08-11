from typing import Any
import ttkbootstrap as ttk
import ttkbootstrap.constants as c
import tkinter as tk
from tkinter import messagebox, filedialog
from Actions import promptUser, configureSyntax, applySintax, centerWindow

class ServerWindow(ttk.Window):
    def __init__(self):
        def _aplicarSintaxis(nombreArchivo:str):
            if nombreArchivo.endswith('.js') or nombreArchivo.endswith('.json'):
                tipoSintaxis = 'javascript'
            elif nombreArchivo.endswith('.py'):
                tipoSintaxis = 'python'
            elif nombreArchivo.endswith('.env'):
                tipoSintaxis = 'basic'
            else:
                tipoSintaxis = 'disabled'
            
            applySintax(
                self._areaTextoEditor,
                tipoSintaxis
            )
        
        def mostrarSeleccionArchivo():
            if seleccion := self._tablaArchivos.item(
                    self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '',
                    'values'
                ):
                self._areaTextoEditor.config(state='normal')
                nombreArchivo = seleccion[0]
                esArchivo = '.' in nombreArchivo
                
                if nombreArchivo in contenido:
                    self._areaTextoEditor.delete('1.0', tk.END)
                    if esArchivo:
                        self._areaTextoEditor.insert('1.0', contenido[nombreArchivo])
                    else:
                        self._areaTextoEditor.insert('1.0', f'Contenido de la carpeta {nombreArchivo}')
                        self._areaTextoEditor.config(state='disabled')       
                else:
                    contenido[nombreArchivo] = ''
                    self._areaTextoEditor.delete('1.0', tk.END)
                
                _aplicarSintaxis(nombreArchivo)
        
        def crearArchivo(nombreArchivo):
            Id_ins = self._tablaArchivos.insert('', 'end', values=(nombreArchivo,))
            self._tablaArchivos.selection_set(Id_ins)
            self._tablaArchivos.focus(Id_ins)
        
        def agregarArchivo():
            archivo = filedialog.askopenfilename()
            if archivo:
                if archivo.split('/')[-1] not in contenido:
                    item_id = self._tablaArchivos.insert('', 'end', values=(archivo.split('/')[-1],))
                    with open(archivo, 'r') as f:
                        contenido[archivo.split('/')[-1]] = f.read()
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    mostrarSeleccionArchivo()
                    return
                
                nomArch = archivo.split('/')[-1]
                if messagebox.askyesno('Archivo existente', f'El archivo {nomArch} ya existe, ¿desea sobreescribirlo?'):
                    with open(archivo, 'rb') as f:
                        contenido[nomArch] = f.read().decode('utf-8')
                    self._areaTextoEditor.delete('1.0', tk.END)
                    self._areaTextoEditor.insert('1.0', contenido[nomArch])
                    
                    # Actualizar la tabla de archivos (borrar todo el contenido y volver a insertar)
                    self._tablaArchivos.delete(*self._tablaArchivos.get_children())
                    
                    for archivo in contenido.keys():
                        item_id = self._tablaArchivos.insert('', 'end', values=(archivo,))

                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    mostrarSeleccionArchivo()
                    return 
                
        def eliminarArchivo():
            # Verificar si hay mas de un archivo en la tabla
            if len(self._tablaArchivos.get_children()) == 1:
                messagebox.showwarning('Error', 'No se puede eliminar el único archivo existente')
                return
            
            if seleccion := self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '':
                archivo = self._tablaArchivos.item(seleccion, 'values')[0]
                if messagebox.askyesno('Eliminar archivo', f'¿Está seguro de que desea eliminar el archivo {archivo}?'):
                    self._tablaArchivos.delete(seleccion)
                    contenido.pop(archivo)
            else:
                messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
        
        def guardarArchivo():
            try:
                nombreArchivo = self._tablaArchivos.item(self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '','values')[0]
                if nombreArchivo in contenido:
                    contenido[nombreArchivo] = self._areaTextoEditor.get('1.0', tk.END)
                    messagebox.showinfo('Guardado', 'El archivo ha sido guardado correctamente')
                else:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
            except IndexError:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
        
        def editarNombre():
            def _editar(nuevoNombre):
                if seleccion := self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '':
                    archivo = self._tablaArchivos.item(seleccion, 'values')[0]
                    
                    if nuevoNombre:
                        self._tablaArchivos.item(seleccion, values=(nuevoNombre.split('/')[-1],))
                        contenido[nuevoNombre.split('/')[-1]] = contenido.pop(archivo)
            
            seleccion = self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else ''
            if seleccion:
                if self._tablaArchivos.item(seleccion, 'values')[0].find(".") != -1:
                    promptUser(
                        self,
                        'Cambiar nombre de archivo', 
                        'Ingrese el nuevo nombre del archivo',
                        'info', 
                        esArchivo=True,
                        esCarpeta=False,
                        callback=_editar
                    )
                else:
                    promptUser(
                        self,
                        'Cambiar nombre de carpeta', 
                        'Ingrese el nuevo nombre de la carpeta',
                        'info', 
                        esArchivo=False,
                        esCarpeta=True,
                        callback=_editar
                    )
                
        
        def crearCarpeta(nombreCarpeta):
            if nombreCarpeta:
                if nombreCarpeta.split('/')[-1] not in contenido:
                    item_id = self._tablaArchivos.insert('', 'end', values=(nombreCarpeta.split('/')[-1],))
                    contenido[nombreCarpeta.split('/')[-1]] = ''
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    mostrarSeleccionArchivo()
                    return
                
                nomArch = nombreCarpeta.split('/')[-1]
                if messagebox.askyesno('Carpeta existente', f'La carpeta {nomArch} ya existe, ¿desea sobreescribirla?'):
                    contenido[nomArch] = ''
                    self._areaTextoEditor.delete('1.0', tk.END)
                    self._areaTextoEditor.insert('1.0', contenido[nomArch])
                    
                    # Actualizar la tabla de archivos (borrar todo el contenido y volver a insertar)
                    self._tablaArchivos.delete(*self._tablaArchivos.get_children())
                    
                    for archivo in contenido.keys():
                        item_id = self._tablaArchivos.insert('', 'end', values=(archivo,))

                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    mostrarSeleccionArchivo()
                    return
        
        super().__init__(themename='superhero')

        self.title('Editor de código')
        self.resizable(False, False)
        
        contenido:dict[str, Any] = {}
        
        self._frameTabla = ttk.Frame(self)
        encabezadoTabla = ['Archivos']
        self._tablaArchivos = ttk.Treeview(self._frameTabla, columns=tuple(encabezadoTabla), show='headings', height=20, style='info.Treeview')
        for encabezado in encabezadoTabla:
            self._tablaArchivos.heading(encabezado, text=encabezado)
            self._tablaArchivos.column(encabezado, width=120, anchor='center')
        item_id = self._tablaArchivos.insert('', 'end', values=('index.js',))
        self._tablaArchivos.selection_set(item_id)
        self._tablaArchivos.focus(item_id)
        self._tablaArchivos.bind('<<TreeviewSelect>>', lambda event: mostrarSeleccionArchivo())
        self._tablaArchivos.bind('<Double-Button-1>', lambda event: editarNombre())
        self._tablaArchivos.grid(row=0, column=0, sticky='nsew')
        self._frameTabla.grid(row=0, rowspan=7, column=0, sticky='nsew')
        
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
                esArchivo=True,
                esCarpeta=False,
                callback=crearArchivo
            ))
        self.botonCreararchivo.grid(row=0, column=0, sticky='nsew', padx=1)
        self._botonAgregar = ttk.Button(self._frameOpciones, text='Cargar archivo', style='warning.TButton', command=agregarArchivo)
        self._botonAgregar.grid(row=0, column=1, sticky='nsew', padx=1)
        self._botonEliminar = ttk.Button(self._frameOpciones, text='Eliminar archivo', style='danger.TButton', command=eliminarArchivo)
        self._botonEliminar.grid(row=0, column=2, sticky='nsew', padx=1)
        self._botonCrearcarpeta = ttk.Button(
            self._frameOpciones, text='Crear carpeta', 
            style='info.TButton', command=lambda: promptUser(
                self,
                'Crear carpeta', 
                'Ingrese el nombre de la carpeta a crear',
                'info', 
                esArchivo=False,
                esCarpeta=True,
                callback=crearCarpeta
            )
        )
        self._botonCrearcarpeta.grid(row=0, column=3, sticky='nsew', padx=1)
        self._botonGuardar = ttk.Button(self._frameOpciones, text='Guardar archivo', style='success.TButton', command=guardarArchivo)
        self._botonGuardar.grid(row=0, column=4, sticky='nsew', padx=1)
        
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
        self._areaTextoEditor.bind('<Control-s>', lambda event: guardarArchivo())
        self._areaTextoEditor.bind('<Control-o>', lambda event: agregarArchivo())
        self._areaTextoEditor.bind(
            '<Control-Shift-s>', 
            lambda event: promptUser(
                self,
                'Crear carpeta', 
                'Ingrese el nombre de la carpeta a crear',
                'info', 
                esArchivo=False,
                esCarpeta=True,
                callback=crearCarpeta
            )
        )
        self._areaTextoEditor.bind('<Control-d>', lambda event: eliminarArchivo())
        self._areaTextoEditor.bind('<Control-r>', lambda event: editarNombre())
        self._areaTextoEditor.bind('<Control-n>', lambda event: promptUser(
            self,
            'Crear archivo', 
            'Ingrese el nombre del archivo a crear',
            'info', 
            esArchivo=True,
            esCarpeta=False,
            callback=crearArchivo
        ))
        self._areaTextoEditor.bind(
            '<KeyRelease>', 
            lambda event: _aplicarSintaxis(
                self._tablaArchivos.item(
                    self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '',
                    'values'
                )[0])
            )
        centerWindow(self)
    
    def iniciar(self):
        self.mainloop()
        
if __name__ == '__main__':
    ventana = ServerWindow()
    ventana.iniciar()