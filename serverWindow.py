import os, shutil, copy
from typing import Any
import ttkbootstrap as ttk
import ttkbootstrap.constants as c
import tkinter as tk
from tkinter import messagebox, filedialog
from Vars import lista_modulosNPM
from Actions import promptUser, configureSyntax, applySintax, centerWindow

class ServerWindow:
    def __init__(self, ventana:ttk.Window, ruta:str) -> None:
        def _aplicarSintaxis(nombreArchivo:str):
            if nombreArchivo.endswith('.js') or nombreArchivo.endswith('.json'):
                tipoSintaxis = 'javascript'
            elif nombreArchivo.endswith('.py'):
                tipoSintaxis = 'python'
            elif nombreArchivo.endswith('.html') or nombreArchivo.endswith('.xml') or nombreArchivo.endswith('.xhtml'):
                tipoSintaxis = 'html'
            elif nombreArchivo.endswith('.css') or nombreArchivo.endswith('.scss') or nombreArchivo.endswith('.sass'):
                tipoSintaxis = 'css'
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
            item_id = ""

            # Obtener las rutas de los archivos y carpetas
            for elemento in listaElementos:
                rutas = elemento['rutaCorta'].split('/')
                item_id = ""
                for i, ruta in enumerate(rutas):
                    # Construir la ruta completa hasta este punto
                    ruta_parcial = '/'.join(rutas[:i + 1])

                    # Solo insertar si esta ruta no ha sido insertada previamente
                    if ruta_parcial not in elementos_insertados:
                        item_id = self._tablaArchivos.insert(item_id, 'end', values=(ruta,), open=True)
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
            listaElementos.clear()
            directorioRaiz = self._ruta.split("\\")[-1]

            for root, dirs, files in os.walk(self._ruta):
                # Calcular la ruta relativa manualmente
                ruta_relativa = root.split(directorioRaiz)[-1].lstrip("\\")
                if ruta_relativa:
                    carpeta_padre = f"{directorioRaiz}/{ruta_relativa.replace('\\', '/')}"
                else:
                    carpeta_padre = directorioRaiz

                # Listar carpetas
                for dir in dirs:
                    if "node_modules" in root or dir == "node_modules":
                        continue
                    detalleElemento = {
                        "nombre": dir,
                        "rutaCorta": f"{carpeta_padre}/{dir}",
                        "rutaCompleta": os.path.join(root, dir).replace("\\", "/"),
                        "tipo": "carpeta",
                        "carpetaPadre": carpeta_padre
                    }
                    listaElementos.append(detalleElemento)

                # Listar archivos
                for file in files:
                    if "node_modules" in root or file == "package-lock.json":
                        continue
                    
                    detalleElemento = {
                        "nombre": file,
                        "rutaCorta": f"{carpeta_padre}/{file}",
                        "rutaCompleta": os.path.join(root, file).replace("\\", "/"),
                        "tipo": "archivo",
                        "carpetaPadre": carpeta_padre
                    }
                    listaElementos.append(detalleElemento)

            # Ordenar los diccionarios del arreglo a traves de la cantidad de '/'. Esto permite que los archivos se muestren antes que las carpetas
            listaElementos.sort(key=lambda x: x['rutaCorta'].count('/'))
           
        def mostrarSeleccionArchivo():
            _actualizarEntradaRuta()
            if self._varRuta.get().find('.') == -1:
                self._botonGuardar.config(state='disabled')
                self._botonEliminar.config(text='Eliminar carpeta')
            else:
                self._botonGuardar.config(state='normal')
                self._botonEliminar.config(text='Eliminar archivo')
            
            
            ruta = _obtenerRutaArchivo("/")
            contenidoArchivo = ""
            
            for elemento in listaElementos:
                if elemento['rutaCorta'] == ruta:
                    if os.path.isfile(elemento['rutaCompleta']):
                        with open(elemento['rutaCompleta'], 'r') as f:
                            contenidoArchivo = f.read()
                    break
            
            self._areaTextoEditor.delete('1.0', tk.END)
            self._areaTextoEditor.insert('1.0', contenidoArchivo)
            
            _aplicarSintaxis(ruta)
        
        def crearArchivo():
            def _crear(nombreArchivo):
                item_id = ""
                seleccion = self._tablaArchivos.selection()
                if not seleccion:
                    seleccion = self._tablaArchivos.get_children()
                    self._tablaArchivos.selection_set(seleccion[0])
                    self._tablaArchivos.focus(seleccion[0])
                
                ruta_seleccion = _obtenerRutaArchivo('/').split("/")[:-1] if _obtenerRutaArchivo('/').find('.') != -1 else _obtenerRutaArchivo('/').split("/")
                ruta_absoluta = self._ruta.split("\\")[:-1]
                ruta_absoluta = '/'.join(ruta_absoluta)
                ruta_seleccion = '/'.join(ruta_seleccion)
                directorio = os.path.join(ruta_absoluta, ruta_seleccion)
                archivo = os.path.join(directorio, nombreArchivo)
                
                if os.path.exists(archivo):
                    messagebox.showwarning('Error', 'El archivo ya existe')
                    return
                
                with open(archivo, 'w') as f:
                    f.write('')
                    
                cargarArchivos()
                item_id = _actualizarTabla()
                self._tablaArchivos.selection_set(item_id)
                self._tablaArchivos.focus(item_id)
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
            
            if not seleccion:
                seleccion = self._tablaArchivos.get_children()
                self._tablaArchivos.selection_set(seleccion[0])
                self._tablaArchivos.focus(seleccion[0])
            
            ruta_seleccion = _obtenerRutaArchivo('/').split("/")[:-1] if _obtenerRutaArchivo('/').find('.') != -1 else _obtenerRutaArchivo('/').split("/")
            ruta_absoluta = self._ruta.split("\\")[:-1]
            ruta_absoluta = '/'.join(ruta_absoluta)
            ruta_seleccion = '/'.join(ruta_seleccion)
            directorio = os.path.join(ruta_absoluta, ruta_seleccion)
            
            archivo = filedialog.askopenfilename()
            if archivo:
                directorio = os.path.join(directorio, archivo.split('/')[-1])
                if os.path.exists(directorio):
                    confirmacion = messagebox.askyesno('Archivo existente', 'El archivo ya existe, ¿desea sobreescribirlo?')
                    if not confirmacion:
                        return
                
                with open(archivo, 'rb') as f:
                    with open(directorio, 'wb') as f2:
                        f2.write(f.read())
                
                cargarArchivos()
                item_id = _actualizarTabla()
                self._tablaArchivos.selection_set(item_id)
                self._tablaArchivos.focus(item_id)
                _actualizarEntradaRuta()
                
        def eliminarArchivo():
            # Verificar si el elemento a eliminar no es la carpeta principal (el elemento padre de todos los archivos)
            if self._tablaArchivos.selection()[0] == self._tablaArchivos.get_children()[0]:
                messagebox.showwarning('Error', 'No se puede eliminar la carpeta principal')
                return
            
            seleccion = self._tablaArchivos.selection()
            if not seleccion:
                messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
                return
            
            ruta_seleccion = _obtenerRutaArchivo('/').split("/")
            ruta_absoluta = self._ruta.split("\\")[:-1]
            ruta_absoluta = '/'.join(ruta_absoluta)
            ruta_seleccion = '/'.join(ruta_seleccion)
            directorio = os.path.join(ruta_absoluta, ruta_seleccion)
            
            if messagebox.askyesno('Eliminar archivo', f'¿Está seguro de que desea eliminar la ubicacion \n {directorio}?'):
                if os.path.exists(directorio):
                    if os.path.isdir(directorio):
                        if os.listdir(directorio):
                            proceder = messagebox.askyesno('Eliminar carpeta', 'La carpeta no está vacía, ¿desea eliminarla junto con su contenido?')
                            if proceder:
                                shutil.rmtree(directorio)
                        else:
                            os.rmdir(directorio)
                    else:
                        os.remove(directorio)
                    
                    cargarArchivos()
                    item_id = _actualizarTabla()
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    _actualizarEntradaRuta()
                    messagebox.showinfo('Eliminado', 'El archivo o carpeta ha sido eliminado correctamente')
        
        def guardarArchivo():
            try:
                ruta_seleccion = _obtenerRutaArchivo('/').split("/")
                ruta_absoluta = self._ruta.split("\\")[:-1]
                ruta_absoluta = '/'.join(ruta_absoluta)
                ruta_seleccion = '/'.join(ruta_seleccion)
                directorio = os.path.join(ruta_absoluta, ruta_seleccion)
                
                if os.path.exists(directorio) and os.path.isfile(directorio):
                    with open(directorio, 'w') as f:
                        f.write(self._areaTextoEditor.get('1.0', tk.END))
                    messagebox.showinfo('Guardado', 'El archivo ha sido guardado correctamente')
                else:
                    messagebox.showwarning('Error', 'No se pudo guardar el archivo')
            except IndexError:
                    messagebox.showerror('Error', 'No se ha seleccionado ningún archivo')
        
        def editarNombre():
            def _editar(nuevoNombre):
                seleccion = self._tablaArchivos.selection()
                if not seleccion:
                    messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
                    return
                
                # Verificar si el elemento a eliminar no es la carpeta principal (el elemento padre de todos los archivos)
                if seleccion[0] == self._tablaArchivos.get_children()[0]:
                    messagebox.showwarning('Error', 'No se puede editar el nombre de la carpeta principal')
                    return
                
                if len(seleccion) == 1:
                    ruta_seleccion = _obtenerRutaArchivo('/').split("/")
                    ruta_absoluta = self._ruta.split("\\")[:-1]
                    ruta_absoluta = '/'.join(ruta_absoluta)
                    ruta_seleccion = '/'.join(ruta_seleccion)
                    nombreActual = os.path.join(ruta_absoluta, ruta_seleccion)
                    nombre = nombreActual.replace("\\","/").split('/')[:-1]
                    nombre.append(nuevoNombre.split('/')[-1])
                    nuevaRuta = '/'.join(nombre)
                    
                    if os.path.exists(nuevaRuta):
                        messagebox.showwarning('Error', 'El archivo o carpeta ya existe')
                        return
                    
                    os.rename(nombreActual, nuevaRuta)
                    cargarArchivos()
                    item_id = _actualizarTabla()
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
                    _actualizarEntradaRuta()
                    messagebox.showinfo('Editado', 'El archivo o carpeta ha sido editado correctamente')
            
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
                    self._tablaArchivos.selection_set(seleccion[0])
                    self._tablaArchivos.focus(seleccion[0])
                
                # Verificar si el elemento seleccionado es un archivo
                if self._tablaArchivos.item(seleccion[0], 'values')[0].find(".") != -1:
                    seleccion = (self._tablaArchivos.parent(seleccion[0]),)
                
                ruta_seleccion = _obtenerRutaArchivo('/').split("/")[:-1] if _obtenerRutaArchivo('/').find('.') != -1 else _obtenerRutaArchivo('/').split("/")
                ruta_absoluta = self._ruta.split("\\")[:-1]
                ruta_absoluta = '/'.join(ruta_absoluta)
                
                ruta_seleccion = '/'.join(ruta_seleccion)
                directorio = os.path.join(ruta_absoluta, ruta_seleccion)
                
                if not ruta_seleccion:
                    ruta_seleccion = self._ruta.split("\\")[-1]
                
                if nombreCarpeta:
                    if os.path.exists(os.path.join(directorio, nombreCarpeta)):
                        messagebox.showwarning('Error', 'La carpeta ya existe')
                        return
                    
                    os.mkdir(os.path.join(directorio, nombreCarpeta))
                    item_id = self._tablaArchivos.insert(seleccion[0], 'end', values=(nombreCarpeta,))
                    self._tablaArchivos.selection_set(item_id)
                    self._tablaArchivos.focus(item_id)
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
        
        def obtenerModulosInstalados():
            for elemento in listaElementos:
                if elemento['nombre'] == 'package.json':
                    with open(elemento['rutaCompleta'], 'r') as f:
                        contenido = f.read()
                        for modulo in modulosNPM:
                            if contenido.find(modulo['nombre'].lower()) != -1:
                                print(modulo['nombre'])
                                modulo['usar'] = True
                            else:
                                modulo['usar'] = False
        
        def instalarModulo():
            pass
        
        def EliminarModulo():
            pass
        
        self.root = ttk.Toplevel(master=ventana)

        self.root.title('Editor de código')
        self.root.resizable(False, False)
        self.root.transient(ventana)
        
        listaElementos:list[dict[str, Any]] = []
        self._ruta = ruta
        self._varRuta = tk.StringVar()
        self._moduloSeleccionado = tk.StringVar()
        modulosNPM = copy.deepcopy(lista_modulosNPM)
        
        self._frameTabla = ttk.Frame(self.root)
        encabezadoTabla = ['Archivos']
        self._tablaArchivos = ttk.Treeview(
            self._frameTabla, 
            columns=tuple(encabezadoTabla), 
            show='tree headings', 
            height=25, 
            style='info.Treeview'
        )
        
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
        item_id = _actualizarTabla()
        self._tablaArchivos.selection_set(item_id)
        self._tablaArchivos.focus(item_id)
        _actualizarEntradaRuta()
        
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
        self._frameEditor.grid(row=1, rowspan=6, column=1, columnspan=3, sticky='nsew', padx=2)
        
        self._frameRuta = ttk.Frame(self.root)
        self._frameRuta.columnconfigure(1, weight=1)
        self._labelRuta = ttk.Label(self._frameRuta, text='Ruta del archivo:', style='info.TLabel')
        self._labelRuta.grid(row=0, column=0, sticky='nsew')
        self._entryRuta = ttk.Entry(self._frameRuta, textvariable=self._varRuta, state='readonly', style='success.TEntry')
        self._entryRuta.grid(row=0, column=1, sticky='nsew')
        self._frameRuta.grid(row=7, column=0, columnspan=4, sticky='nsew', pady=5, padx=5)
        
        self._frameModulos = ttk.Frame(self.root, style='info.TLabelframe')
        self._frameModulos.grid_rowconfigure(1, weight=1)
        self._comboModulos = ttk.Combobox(self._frameModulos, textvariable=self._moduloSeleccionado, values=tuple([modulo['nombre'] for modulo in modulosNPM if not modulo["usar"]]), state='readonly', style='info.TCombobox')
        self._moduloSeleccionado.set('Seleccionar módulo')
        self._comboModulos.grid(row=0, column=0, sticky='nsew', padx=1)
        self._botonInstalar = ttk.Button(self._frameModulos, text='Instalar', style='info.TButton', command=instalarModulo)
        self._botonInstalar.grid(row=0, column=1, sticky='nsew', padx=1)
        
        encabezadoTablaModulos = ['Nombre', 'Versión']
        self._tablaModulos = ttk.Treeview(
            self._frameModulos,
            columns=tuple(encabezadoTablaModulos),
            show='headings',
            height=5,
            style='info.Treeview'
        )
        
        # Configurar la primera columna de la tabla
        for encabezado in encabezadoTablaModulos:
            self._tablaModulos.heading(encabezado, text=encabezado)
            self._tablaModulos.column(encabezado, width=80)
        
        obtenerModulosInstalados()
        
        #TODO: Agregar funcionalidad para instalar y eliminar módulos
        #TODO: Mostrar los módulos instalados en la tabla
        #TODO: Mostrar mas informacion en la pantalla de instalacion de modulos (Label Instalar modulos)
        
        self._tablaModulos.bind('<Double-Button-3>', lambda event: EliminarModulo())
        self._tablaModulos.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5)
        
        self._frameModulos.grid(row=0, rowspan=8, column=4, columnspan=3, sticky='nsew', padx=2)
        
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