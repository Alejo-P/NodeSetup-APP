import os
from typing import Any
import ttkbootstrap as ttk
import ttkbootstrap.constants as c
import tkinter as tk
from tkinter import messagebox, filedialog
from Actions import promptUser, configureSyntax, applySintax, centerWindow

class ServerWindow:
    def __init__(self, ventana:ttk.Window, ruta:str) -> None:
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
        
        def _actualizarEntradaRuta():
            ruta = _obtenerRutaArchivo()
            self._varRuta.set(ruta)
        
        def _actualizarTabla():
            # Actualizar la tabla de archivos (borrar todo el contenido y volver a insertar)
            self._tablaArchivos.delete(*self._tablaArchivos.get_children())

            # Variable para mantener un seguimiento de los elementos ya insertados
            elementos_insertados = {}

            # Obtener las rutas de los archivos
            archivos = contenido.keys()
            item_id = ""

            for archivo in archivos:
                elementos = archivo.split('/')
                item_id = ""
                
                # Recorrer cada parte de la ruta (ej. "Backend", "src", "database.js")
                for i, elemento in enumerate(elementos):
                    # Construir la ruta completa hasta este punto
                    ruta_parcial = "/".join(elementos[:i + 1])

                    # Solo insertar si esta ruta no ha sido insertada previamente
                    if ruta_parcial not in elementos_insertados:
                        item_id = self._tablaArchivos.insert(item_id, 'end', values=(elemento,), open=True)
                        elementos_insertados[ruta_parcial] = item_id
                    else:
                        # Obtener el item_id del elemento ya insertado
                        item_id = elementos_insertados[ruta_parcial]
            return str(item_id)
        
        def _obtenerRutaArchivo(concatenarPor=' > '):
            # Obtener el elemento seleccionado
            seleccion = self._tablaArchivos.selection()
            
            if not seleccion:
                return ""
            
            # Comenzar desde el elemento seleccionado
            item_id = seleccion[0]
            ruta = []
            
            while item_id:
                # Obtener el nombre del elemento actual y agregarlo a la lista
                nombre = self._tablaArchivos.item(item_id, 'values')[0]
                ruta.append(nombre)
                
                # Moverse al elemento padre
                item_id = self._tablaArchivos.parent(item_id)
            
            # Invertir la lista para obtener el orden desde el elemento raíz al seleccionado
            ruta.reverse()
            
            # Concatenar los nombres en una cadena
            ruta_concatenada = concatenarPor.join(ruta)
            return ruta_concatenada
        
        def cargarArchivos():
            archivos = []
            directorioRaiz = self._ruta.split("\\")[-1]
             # Recorre todos los directorios y archivos en el directorio base
            for root, _ , files in os.walk(self._ruta):
                for file in files:
                    resto_cadena = os.path.join(root, file)
                    indice_cadena = root.find(directorioRaiz)
                    sub_rutas = resto_cadena[indice_cadena:]
                    if ("node_modules" in sub_rutas) or ("package-lock.json" in sub_rutas):
                        continue
                    sub_rutas = sub_rutas.replace("\\", "/")
                    
                    with open(os.path.join(root, file), 'rb') as f:
                        contenido[sub_rutas] = f.read().decode('utf-8')
                    archivos.append(sub_rutas)
            return archivos
           
        def mostrarSeleccionArchivo():
            _actualizarEntradaRuta()
            if self._varRuta.get().find('.') == -1:
                self._botonGuardar.config(state='disabled')
                self._botonEliminar.config(text='Eliminar carpeta')
            else:
                self._botonGuardar.config(state='normal')
                self._botonEliminar.config(text='Eliminar archivo')
            
            print(cargarArchivos())
            ruta = _obtenerRutaArchivo("/")
            
            tipo = 'archivo' if '.' in ruta else 'carpeta'
            self._labelRuta.config(text=f'Ruta del {tipo}:')
            
            if tipo == 'archivo':
                self._botonEliminar.config(text='Eliminar archivo')
                self._areaTextoEditor.config(state='normal')
                nombreArchivo = ruta
                if nombreArchivo in contenido:
                    self._areaTextoEditor.delete('1.0', tk.END)
                    self._areaTextoEditor.insert('1.0', contenido[nombreArchivo])
                else:
                    contenido[nombreArchivo] = ''
                    self._areaTextoEditor.delete('1.0', tk.END)
            else:
                self._areaTextoEditor.config(state='disabled')
                self._botonEliminar.config(text='Eliminar carpeta')
                self._areaTextoEditor.delete('1.0', tk.END)
                
            _aplicarSintaxis(ruta)
        
        def crearArchivo():
            def _crear(nombreArchivo):
                item_id = ""
                seleccion = self._tablaArchivos.selection()
                if not seleccion:
                    seleccion = self._tablaArchivos.get_children()
                    
                print(
                    self._tablaArchivos.get_children(),
                    self._tablaArchivos.item(seleccion[0], 'values')[0],
                    self._tablaArchivos.item(seleccion[0], 'values')[0].find(".")
                )
                if self._tablaArchivos.item(seleccion[0], 'values')[0].find(".") != -1:
                    item_id = self._tablaArchivos.parent(item_id)
                else:
                    item_id = seleccion[0]
                
                print(seleccion, item_id)
                
                Id_ins = self._tablaArchivos.insert(item_id, 'end', values=(nombreArchivo,))
                self._tablaArchivos.selection_set(Id_ins)
                self._tablaArchivos.focus(Id_ins)
                _actualizarEntradaRuta()
            
            promptUser(
                self.root,
                'Crear archivo', 
                'Ingrese el nombre del archivo a crear',
                'info', 
                esArchivo=True,
                esCarpeta=False,
                callback=_crear
            )
        
        def agregarArchivo():
            seleccion = self._tablaArchivos.selection()
            ruta = _obtenerRutaArchivo('/').split('/')[:-1] if _obtenerRutaArchivo('/').find('.') != -1 else _obtenerRutaArchivo('/').split('/')
            ruta = '/'.join(ruta)
            if not seleccion:
                seleccion = self._tablaArchivos.get_children()
                return
            
            archivo = filedialog.askopenfilename()
            if archivo:
                ruta += '/' + archivo.split('/')[-1]
                item_id = seleccion[0]
                if self._tablaArchivos.item(item_id, 'values')[0].find(".") != -1:
                    item_id = self._tablaArchivos.parent(item_id)
                
                if ruta not in contenido:
                    item_id = self._tablaArchivos.insert(item_id, 'end', values=(archivo.split('/')[-1],))
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    
                    ruta = _obtenerRutaArchivo('/')
                    with open(archivo, 'r') as f:
                        contenido[ruta] = f.read()
                    mostrarSeleccionArchivo()
                    return
                
                if messagebox.askyesno('Archivo existente', f'El archivo {ruta.split("/")[-1]} ya existe, ¿desea sobreescribirlo?'):
                    with open(archivo, 'r', encoding="utf-8") as f:
                        contenido[ruta] = f.read()
                    self._areaTextoEditor.delete('1.0', tk.END)
                    self._areaTextoEditor.insert('1.0', contenido[ruta])
                    
                    # Actualizar la tabla de archivos
                    item_id = _actualizarTabla() 
                    
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    mostrarSeleccionArchivo()
                    return 
         
        def eliminarArchivo():
            # Verificar si el elemento a eliminar no es la carpeta principal (el elemento padre de todos los archivos)
            if self._tablaArchivos.selection()[0] == self._tablaArchivos.get_children()[0]:
                messagebox.showwarning('Error', 'No se puede eliminar la carpeta principal')
                return
            
            seleccion = self._tablaArchivos.selection()
            ruta = _obtenerRutaArchivo('/')
            if not ruta:
                messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
                return
            
            if messagebox.askyesno('Eliminar archivo', f'¿Está seguro de que desea eliminar la ubicacion \n {ruta}?'):
                self._tablaArchivos.delete(seleccion[0])
                contenido.pop(ruta)
                self._areaTextoEditor.delete('1.0', tk.END)
        
        def guardarArchivo():
            try:
                ruta = _obtenerRutaArchivo('/')
                if ruta in contenido:
                    contenido[ruta] = self._areaTextoEditor.get('1.0', tk.END)
                    messagebox.showinfo('Guardado', 'El archivo ha sido guardado correctamente')
                else:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
            except IndexError:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
        
        def editarNombre():
            def _editar(nuevoNombre):
                seleccion = self._tablaArchivos.selection()
                if not seleccion:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
                    return
                
                if len(seleccion) == 1:
                    ruta = _obtenerRutaArchivo('/')
                    nombre = ruta.split('/')[:-1]
                    nombre.append(nuevoNombre.split('/')[-1])
                    nuevaRuta = '/'.join(nombre)
                    if nuevoNombre:
                        self._tablaArchivos.item(seleccion[0], values=(nuevoNombre.split('/')[-1],))
                        contenido[nuevaRuta] = contenido.pop(ruta)
                        _actualizarEntradaRuta()
            
            seleccion = self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else ''
            if seleccion:
                if self._tablaArchivos.item(seleccion, 'values')[0].find(".") != -1:
                    promptUser(
                        self.root,
                        'Cambiar nombre de archivo', 
                        'Ingrese el nuevo nombre del archivo',
                        'info', 
                        esArchivo=True,
                        esCarpeta=False,
                        callback=_editar
                    )
                else:
                    promptUser(
                        self.root,
                        'Cambiar nombre de carpeta', 
                        'Ingrese el nuevo nombre de la carpeta',
                        'info', 
                        esArchivo=False,
                        esCarpeta=True,
                        callback=_editar
                    )
                
        def crearCarpeta():
            def _crear(nombreCarpeta):
                seleccion = self._tablaArchivos.selection()
                if not seleccion:
                    seleccion = self._tablaArchivos.get_children()
                
                # Verificar si el elemento seleccionado es un archivo
                if self._tablaArchivos.item(seleccion[0], 'values')[0].find(".") != -1:
                    seleccion = (self._tablaArchivos.parent(seleccion[0]),)
                
                if nombreCarpeta:
                    if nombreCarpeta.split('/')[-1] not in contenido:
                        print(seleccion)
                        item_id = self._tablaArchivos.insert(seleccion[0], 'end', values=(nombreCarpeta.split('/')[-1],))
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
                            item_id = self._tablaArchivos.insert(seleccion[0], 'end', values=(archivo,))

                        self._tablaArchivos.selection_set(item_id)
                        self._tablaArchivos.focus(item_id)
                        mostrarSeleccionArchivo()
                        return
            
            promptUser(
                self.root,
                'Crear carpeta', 
                'Ingrese el nombre de la carpeta a crear',
                'info', 
                esArchivo=False,
                esCarpeta=True,
                callback=_crear
            )
        
        self.root = ttk.Toplevel(master=ventana)

        self.root.title('Editor de código')
        self.root.resizable(False, False)
        self.root.transient(ventana)
        
        contenido:dict[str, Any] = {}
        self._ruta = ruta
        
        self._frameTabla = ttk.Frame(self.root)
        encabezadoTabla = ['Archivos']
        self._tablaArchivos = ttk.Treeview(self._frameTabla, columns=tuple(encabezadoTabla), show='tree headings', height=25, style='info.Treeview')
        
        # Configurar la primera columna de la tabla
        self._tablaArchivos.column('#0', width=40)
        self._tablaArchivos.heading('#0', text='Nivel')
        for encabezado in encabezadoTabla:
            self._tablaArchivos.heading(encabezado, text=encabezado)
            self._tablaArchivos.column(encabezado, width=150)
            
        self._tablaArchivos.bind('<<TreeviewSelect>>', lambda event: mostrarSeleccionArchivo())
        self._tablaArchivos.bind('<Double-Button-3>', lambda event: editarNombre())
        self._tablaArchivos.pack(expand=True, fill='both')
        self._frameTabla.grid(row=0, rowspan=7, column=0, sticky='nsew')
        cargarArchivos()
        _actualizarTabla()
        
        self._frameOpciones = ttk.Frame(self.root)
        
        self.botonCreararchivo = ttk.Button(self._frameOpciones, text='Crear archivo', style='info.TButton', command=crearArchivo)
        self.botonCreararchivo.grid(row=0, column=0, sticky='nsew', padx=1)
        self._botonAgregar = ttk.Button(self._frameOpciones, text='Cargar archivo', style='warning.TButton', command=agregarArchivo)
        self._botonAgregar.grid(row=0, column=1, sticky='nsew', padx=1)
        self._botonEliminar = ttk.Button(self._frameOpciones, text='Eliminar archivo', style='danger.TButton', command=eliminarArchivo)
        self._botonEliminar.grid(row=0, column=2, sticky='nsew', padx=1)
        self._botonCrearcarpeta = ttk.Button(self._frameOpciones, text='Crear carpeta', style='info.TButton', command=crearCarpeta)
        self._botonCrearcarpeta.grid(row=0, column=3, sticky='nsew', padx=1)
        self._botonGuardar = ttk.Button(self._frameOpciones, text='Guardar archivo', style='success.TButton', command=guardarArchivo)
        self._botonGuardar.grid(row=0, column=4, sticky='nsew', padx=1)
        
        self._frameOpciones.grid(row=0, column=1, columnspan=3, sticky='nsew')
        
        self._frameRuta = ttk.Frame(self.root)
        self._frameRuta.columnconfigure(1, weight=1)
        self._varRuta = tk.StringVar()
        self._labelRuta = ttk.Label(self._frameRuta, text='Ruta del archivo:', style='info.TLabel')
        self._labelRuta.grid(row=0, column=0, sticky='nsew')
        self._entryRuta = ttk.Entry(self._frameRuta, textvariable=self._varRuta, state='readonly', style='success.TEntry')
        self._entryRuta.grid(row=0, column=1, sticky='nsew')
        
        self._frameRuta.grid(row=7, column=0, columnspan=4, sticky='nsew', pady=5, padx=5)
        
        self._frameEditor = ttk.Frame(self.root)
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
        self._areaTextoEditor.bind('<Control-Shift-o>', lambda event: crearCarpeta())
        self._areaTextoEditor.bind('<Control-d>', lambda event: eliminarArchivo())
        self._areaTextoEditor.bind('<Control-r>', lambda event: editarNombre())
        self._areaTextoEditor.bind('<Control-n>', lambda event: crearArchivo())
        self._areaTextoEditor.bind(
            '<KeyRelease>', 
            lambda event: _aplicarSintaxis(
                self._tablaArchivos.item(
                    self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '',
                    'values'
                )[0])
            )
        centerWindow(self.root)
    
    def iniciar(self):
        self.root.mainloop()
        
if __name__ == '__main__':
    app = ttk.Window(themename='superhero')
    ventana = ServerWindow(app, "")
    #ventana.iniciar()
    app.mainloop()