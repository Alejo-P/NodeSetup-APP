import os, shutil, psutil, queue, json
import subprocess
import threading
from typing import Any
import ttkbootstrap as ttk
import ttkbootstrap.constants as BOOTSTRAP
import tkinter as tk
from tkinter import messagebox, filedialog
from Actions import (
    clearQueue,
    doNothing,
    getPathOf, 
    loadInfoNPMModules, 
    promptUser, 
    configureSyntax, 
    applySintax,
    centerWindow, 
    runCommand,
    getDetailedModules
)

class NodeServer:
    _enEjecucion = False
    def __init__(self, comando:list[str] | None = None, ruta:str | None = None) -> None:
        self._comando = comando if comando else []
        self._ruta = ruta if ruta else ''
        self._proceso = None
    
    def enEjecucion(self):
        return self._enEjecucion
    
    def ejecutar(self):
        if self._enEjecucion:
            print('El servidor ya se encuentra en ejecución')
            return
        
        if not self._comando or not all(fragmento for fragmento in self._comando) or not self._ruta:
            print('Comando incorrectamente definido o ruta no definida')
            return
        
        self._proceso = subprocess.Popen(self._comando, cwd=self._ruta)
        self._enEjecucion = True
    
    def detener(self):
        if not self._enEjecucion or not self._proceso:
            print('El servidor no se encuentra en ejecución')
            return
        
        self._enEjecucion = False
        
        if self._proceso.poll() is not None:
            print('El servidor ya ha sido detenido')
            return

        procesos = psutil.Process(self._proceso.pid)
        for proceso in procesos.children(recursive=True):
            proceso.terminate()
        
        procesos.kill()
        procesos.wait()
            
    def reiniciar(self):
        self.detener()
        self.ejecutar()
        
    def setComando(self, comando:list[str]):
        self._comando = comando
        
    def setRuta(self, ruta:str):
        self._ruta = ruta

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
                self._areaTextoEditor.delete('1.0', tk.END)
                self._areaTextoEditor.config(state='disabled')
            else:
                self._areaTextoEditor.config(state='normal')
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
            seleccion = self._tablaArchivos.selection()
            if not seleccion:
                messagebox.showwarning('Error', 'No se ha seleccionado ningún archivo')
                return
            
            # Verificar si el elemento a eliminar no es la carpeta principal (el elemento padre de todos los archivos)
            if seleccion[0] == self._tablaArchivos.get_children()[0]:
                messagebox.showwarning('Error', 'No se puede eliminar la carpeta principal')
                return
            
            if "package.json" in self._tablaArchivos.item(seleccion[0], 'values')[0]:
                messagebox.showwarning('Error', 'No se puede eliminar el archivo package.json')
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
            nonlocal PackageJSON
            try:
                ruta_seleccion = _obtenerRutaArchivo('/').split("/")
                ruta_absoluta = self._ruta.split("\\")[:-1]
                ruta_absoluta = '/'.join(ruta_absoluta)
                ruta_seleccion = '/'.join(ruta_seleccion)
                directorio = os.path.join(ruta_absoluta, ruta_seleccion)
                
                if directorio.endswith("package.json"):
                    try:
                        PackageJSON = json.loads(self._areaTextoEditor.get('1.0', tk.END))
                    except json.JSONDecodeError:
                        messagebox.showerror('Error', 'El archivo package.json no es un archivo JSON válido')
                        return
                
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
            nonlocal PackageJSON
            for elemento in listaElementos:
                if elemento['nombre'] == 'package.json':
                    with open(elemento['rutaCompleta'], 'r') as f:
                        PackageJSON = json.loads(f.read())
                        break
            for modulo in modulosNPM:
                dependencias = PackageJSON.get('dependencies', {})
                devDependencias = PackageJSON.get('devDependencies', {})
                if dependencias.get(modulo['nombre'].lower()) or devDependencias.get(modulo['nombre'].lower()):
                    modulo['usar'] = True
                    version = dependencias.get(modulo['nombre'].lower()) or devDependencias.get(modulo['nombre'].lower())
                    version = version[1:] if version[0] == "^" else version
                    modulo['version'] = version
                else:
                    modulo['usar'] = False
            
            _actualizarDataSettings("modulesLoaded", modulosNPM)
        
        def _actualizarValoresComboModulos():
            self._comboModulos['values'] = tuple([modulo['nombre'] for modulo in modulosNPM if not modulo["usar"]])
        
        def _actualizarTablaModulos():
            # Actualizar la tabla de archivos (borrar todo el contenido y volver a insertar)
            self._tablaModulos.delete(*self._tablaModulos.get_children())
            
            for modulo in modulosNPM:
                if modulo['usar']:
                    self._tablaModulos.insert('', 'end', values=(modulo['nombre'], modulo['version']))
        
        def _actualizarDataSettings(clave:str, valor:Any):
            nonlocal DataSettings
            DataSettings[clave] = valor
            with open(os.path.join(self._ruta, 'appSettings.json'), 'w') as f:
                f.write(json.dumps(DataSettings, indent=4))
            
        def instalarModulo(detalleModulo:dict[str, Any]):
            def _intalarmoduloBackgroud():
                resultado = runCommand([getPathOf("npm"), 'i', f"{detalleModulo['nombre'].lower()}@{detalleModulo['version']}"], self._ruta)
                if isinstance(resultado, subprocess.CalledProcessError):
                    detalleModulo['usar'] = False
                    tareas.put("instalar modulo - " + detalleModulo['nombre'] + " - False")
                    return
               
                detalleModulo['usar'] = True
                tareas.put("instalar modulo - " + detalleModulo['nombre'] + " - True")
            
            textoBoton, estadoBoton = self._botonInstalar.cget('text'), self._botonInstalar.cget('state')
            
            if textoBoton != "Instalar" or estadoBoton == 'disabled':
                messagebox.showwarning('Tarea en ejecución', 'Ya hay una tarea en ejecución')
                return
            
            if self._moduloSeleccionado.get() == "Seleccionar módulo":
                messagebox.showwarning('Error', 'No se ha seleccionado ningún módulo')
                return
            
            
            confirmacion = messagebox.askyesno('Instalar módulo', f'¿Está seguro de que desea instalar el módulo {detalleModulo["nombre"]}?')
            if confirmacion:
                self.root.protocol('WM_DELETE_WINDOW', doNothing)
                self._botonInstalar.config(text="Instalando", state='disabled')
                self._botonEjecutarServidor.config(state='disabled')
                centerWindow(self.root, True)
                hiloInstalacion = threading.Thread(target=_intalarmoduloBackgroud)
                hiloInstalacion.daemon = True
                hiloInstalacion.start()
                self._afterTareas = self.root.after(100, _verificarTarea)
                
        def EliminarModulo(detalleModulo:dict[str, Any]):
            def _desinstalarmoduloBackground():
                resultado = runCommand([getPathOf("npm"), 'uninstall', detalleModulo['nombre'].lower()], self._ruta)
                if isinstance(resultado, subprocess.CalledProcessError):
                    detalleModulo['usar'] = True
                    tareas.put("eliminar modulo - " + detalleModulo['nombre'] + " - False")
                    return
                
                detalleModulo['usar'] = False
                tareas.put("eliminar modulo - " + detalleModulo['nombre'] + " - True")
            
            if not self._tablaModulos.selection():
                messagebox.showwarning('Error', 'No se ha seleccionado ningún módulo')
                return
            
            textoBoton, estadoBoton = self._botonInstalar.cget('text'), self._botonInstalar.cget('state')
            
            if textoBoton != "Instalar" or estadoBoton == 'disabled':
                messagebox.showwarning('Tarea en ejecución', 'Ya hay una tarea en ejecución')
                return    
            
            confirmacion = messagebox.askyesno('Eliminar módulo', f'¿Está seguro de que desea eliminar el módulo {detalleModulo["nombre"]}?')
            if confirmacion:
                self.root.protocol('WM_DELETE_WINDOW', doNothing)
                self._botonInstalar.config(text="Eliminando", state='disabled')
                self._botonEjecutarServidor.config(state='disabled')
                centerWindow(self.root, True)
                hiloDesinstalacion = threading.Thread(target=_desinstalarmoduloBackground)
                hiloDesinstalacion.daemon = True
                hiloDesinstalacion.start()
                self._afterTareas = self.root.after(100, _verificarTarea)
        
        def _verificarTarea():
            try:
                tareaEjecutada = tareas.get_nowait()
                desglose = tareaEjecutada.split(" - ")
                self._botonInstalar.config(text="Instalar", state='normal')
                self._botonEjecutarServidor.config(state='normal')
                obtenerModulosInstalados()
                _actualizarValoresComboModulos()
                self._moduloSeleccionado.set("Seleccionar módulo")
                _actualizarTablaModulos()
                centerWindow(self.root, True)
                self.root.protocol('WM_DELETE_WINDOW', cerrarVentana)
                
                if desglose[0] == "instalar modulo":
                    if desglose[2] == "False":
                        messagebox.showerror('Error', f'No se pudo instalar el módulo\n{desglose[1]}')
                    else:
                        messagebox.showinfo('Instalado', f'El módulo {desglose[1]} ha sido instalado correctamente')
                elif desglose[0] == "eliminar modulo":
                    if desglose[2] == "False":
                        messagebox.showerror('Error', f'No se pudo eliminar el módulo\n{desglose[1]}')
                    else:
                        messagebox.showinfo('Eliminado', f'El módulo {desglose[1]} ha sido eliminado correctamente')
                self._afterTareas = ""
            except queue.Empty:
                self._afterTareas = self.root.after(100, _verificarTarea)
                return
        
        def _precargaInfoModulos():
            nonlocal modulosNPM, DataSettings
            
            with open(os.path.join(self._ruta, 'appSettings.json'), 'r') as f:
                DataSettings = json.loads(f.read())
            
            runCommand([getPathOf("explorer"), self._ruta])
            isLoaded = DataSettings.get("isLoadedModules")
            if not isLoaded:
                modulosNPM = loadInfoNPMModules(modulosNPM)
                _actualizarDataSettings("isLoadedModules", True)
            else:
                modulosNPM = DataSettings.get("modulesLoaded")
            
            
            tareas.put("modulos cargados")
        
        def _verificarPrecarga():
            self._botonInstalar.config(text="Cargando",state='disabled')
            self._tablaModulos.delete(*self._tablaModulos.get_children())
            self._tablaModulos.insert('', 'end', values=('Cargando...', 'Cargando...'))
            self._botonEjecutarServidor.config(state='disabled')
            centerWindow(self.root, True)
            try:
                tareas.get_nowait()
                self._botonInstalar.config(text="Instalar", state='normal')
                self._botonEjecutarServidor.config(state='normal')
                obtenerModulosInstalados()
                _actualizarValoresComboModulos()
                self._moduloSeleccionado.set("Seleccionar módulo")
                _actualizarTablaModulos()
                centerWindow(self.root, True)
                self._afterPrecarga = ""
            except queue.Empty:
                self._afterPrecarga = self.root.after(100, _verificarPrecarga)
                return
            
            clearQueue(tareas)
        
        def _detenerServidor():
            self._NodeServer.detener()
            self._botonEjecutarServidor.config(text='Ejecutar servidor', command=_ejecutarServidor)
            messagebox.showinfo('Servidor detenido', 'El servidor ha sido detenido correctamente')
            
        def _ejecutarServidor():
            def _ejecBackground():
                self._NodeServer.ejecutar()
                self._botonEjecutarServidor.config(text='Detener servidor', command=_detenerServidor)
                messagebox.showinfo('Servidor en ejecución', 'El servidor se encuentra en ejecución')
            
            scripts = PackageJSON.get('scripts', {})
            if not scripts.get(scriptEjecucion):
                messagebox.showwarning('Error', f'No se ha definido un script de inicio ({scriptEjecucion}) en el archivo package.json')
                return
            
            self._NodeServer.setComando([getPathOf("npm"), "run", scriptEjecucion])
            self._NodeServer.setRuta(self._ruta)   
            threading.Thread(target=_ejecBackground).start()
        
        def cerrarVentana():
            if self._NodeServer.enEjecucion():
                confirmacion = messagebox.askyesno('Servidor en ejecución', 'El servidor se encuentra en ejecución, ¿desea detenerlo?')
                if not confirmacion:
                    return
                
                _detenerServidor()
            
            if self._afterPrecarga:
                self.root.after_cancel(self._afterPrecarga)
            
            if self._afterTareas:
                self.root.after_cancel(self._afterTareas)
            
            self.root.destroy()
        
        def _cambiarScriptInicio():
            def _nuevoScript(script):
                nonlocal scriptEjecucion
                scriptEjecucion = script
                messagebox.showinfo('Script de inicio cambiado', f'El script de inicio ha sido cambiado a {scriptEjecucion}')
            
            scripts = PackageJSON.get('scripts', {})
            scripts = list(scripts.keys()) if scripts else ["No se pudo encontrar ningún script"]
            promptUser(
                self.root,
                'Cambiar script de inicio',
                'Seleccione el script de inicio',
                'info',
                esArchivo=False,
                esCarpeta=False,
                opciones=scripts,
                usarEntrada=False,
                callback=_nuevoScript
            )
        
        def _atajosTeclado():
            attec = ttk.Toplevel(master=self.root)
            attec.title('Atajos de teclado')
            attec.resizable(False, False)
            attec.transient(self.root)
            attec.protocol('WM_DELETE_WINDOW', attec.destroy)
            
            ttk.Label(attec, text='Atajos del teclado').grid(row=0, column=0, columnspan=2, sticky='nsew')
            
            frame_accionesArchivo = ttk.LabelFrame(attec, text='Acciones de archivos y/o carpetas', bootstyle='info.TLabelframe') #type: ignore
            frame_accionesArchivo.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
            ttk.Entry(frame_accionesArchivo, )
            ttk.Label(frame_accionesArchivo, text='Ctrl + S: Guardar un archivo').pack(expand=True, fill='x')
            ttk.Label(frame_accionesArchivo, text='Ctrl + O: Cargar un archivo').pack(expand=True, fill='x')
            ttk.Label(frame_accionesArchivo, text='Ctrl + Shift + O: Crear carpeta').pack(expand=True, fill='x')
            ttk.Label(frame_accionesArchivo, text='Ctrl + D: Eliminar un archivo').pack(expand=True, fill='x')
            ttk.Label(frame_accionesArchivo, text='Ctrl + R: Editar nombre de un archivo').pack(expand=True, fill='x')
            ttk.Label(frame_accionesArchivo, text='Ctrl + N: Crear un archivo').pack(expand=True, fill='x')
            
            frame_accionesServidor = ttk.LabelFrame(attec, text='Acciones de servidor', bootstyle='info.TLabelframe') #type: ignore
            frame_accionesServidor.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
            ttk.Label(frame_accionesServidor, text='Ctrl + E: Ejecutar/Detener servidor').pack(expand=True, fill='x')
            ttk.Label(frame_accionesServidor, text='Ctrl + M: Instalar módulo').pack(expand=True, fill='x')
            ttk.Label(frame_accionesServidor, text='Ctrl + Shift + M: Eliminar módulo').pack(expand=True, fill='x')
            
            ttk.Button(attec, text='Cerrar', command=attec.destroy, bootstyle=(BOOTSTRAP.DANGER, BOOTSTRAP.OUTLINE)).grid(row=2, column=0, columnspan=2, sticky='nsew', pady=5, padx=5) #type: ignore
            
            columnas = attec.grid_size()[0]
            for columna in range(columnas):
                attec.columnconfigure(columna, weight=1)
            
            centerWindow(attec, True)
            
        def _menuContextual():
            def _showMenu(event):
                menu.post(event.x_root, event.y_root)
            
            def _hideMenu(event):
                menu.unpost()
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Atajos de teclado", command=_atajosTeclado)
            menu.add_separator()
            menu.add_command(label="Cambiar script de inicio", command=_cambiarScriptInicio)
            
            self._entryRuta.bind("<Button-3>", _showMenu)
            menu.bind("<Leave>", _hideMenu)
        
        self.root = ttk.Toplevel(master=ventana)

        self.root.title('Editor de código')
        self.root.resizable(False, False)
        self.root.transient(ventana)
        self.root.protocol('WM_DELETE_WINDOW', cerrarVentana)
        self.root.after(100, _menuContextual)
        
        listaElementos:list[dict[str, Any]] = []
        tareas = queue.Queue()
        self._ruta = ruta
        self._NodeServer = NodeServer()
        self._varRuta = tk.StringVar()
        self._moduloSeleccionado = tk.StringVar()
        modulosNPM = getDetailedModules(excluirClaves=['versiones', 'global', 'argumento'])
        PackageJSON = {}
        DataSettings = {}
        scriptEjecucion = "start"
        
        hiloPrecarga = threading.Thread(target=_precargaInfoModulos)
        hiloPrecarga.daemon = True
        hiloPrecarga.start()
        self._afterPrecarga = self.root.after(100, _verificarPrecarga)
        self._afterTareas = ""
        
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
        
        columna, _ = self._frameOpciones.grid_size()
        for columna in range(columna):
            self._frameOpciones.columnconfigure(columna, weight=1)
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
        self._comboModulos = ttk.Combobox(self._frameModulos, textvariable=self._moduloSeleccionado, values=("Cargando modulos ...",), state='readonly', style='info.TCombobox')
        self._moduloSeleccionado.set("Cargando modulos ...")
        self._comboModulos.grid(row=0, column=0, sticky='nsew', padx=1)
        self._botonInstalar = ttk.Button(self._frameModulos, text='Instalar', style='info.TButton', command=lambda: instalarModulo(
                [modulo for modulo in modulosNPM if modulo['nombre'] == self._moduloSeleccionado.get()][0] if self._moduloSeleccionado.get() != "Seleccionar módulo" else {}
            )
        )
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
        
        self._tablaModulos.bind('<Double-Button-3>', lambda event: EliminarModulo(  
                [modulo for modulo in modulosNPM if modulo['nombre'] == self._tablaModulos.item(self._tablaModulos.selection()[0], 'values')[0]][0] if self._tablaModulos.selection() else {}
            )
        )
        self._tablaModulos.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5)
        
        self._frameModulos.grid(row=0, rowspan=7, column=4, columnspan=3, sticky='nsew', padx=2)
        
        self._botonEjecutarServidor = ttk.Button(self.root, text='Ejecutar servidor', style='success.TButton', command=_ejecutarServidor)
        self._botonEjecutarServidor.grid(row=7, column=4, columnspan=3, sticky='nsew', pady=5)
        
        configureSyntax(self._areaTextoEditor)
        self._areaTextoEditor.bind(
            '<KeyRelease>', 
            lambda event: _aplicarSintaxis(
                self._tablaArchivos.item(
                    self._tablaArchivos.selection()[0] if self._tablaArchivos.selection() else '',
                    'values'
                )[0])
            )
        self.root.bind('<Control-s>', lambda event: guardarArchivo())
        self.root.bind('<Control-o>', lambda event: agregarArchivo())
        self.root.bind('<Control-Shift-o>', lambda event: crearCarpeta())
        self.root.bind('<Control-d>', lambda event: eliminarArchivo())
        self.root.bind('<Control-r>', lambda event: editarNombre())
        self.root.bind('<Control-n>', lambda event: crearArchivo())
        self.root.bind('<Control-e>', lambda event: _ejecutarServidor())
        self.root.bind('<Control-m>', lambda event: instalarModulo(
            [modulo for modulo in modulosNPM if modulo['nombre'] == self._moduloSeleccionado.get()][0] if self._moduloSeleccionado.get() != "Seleccionar módulo" else {}
        ))
        self.root.bind('<Control-M>', lambda event: EliminarModulo(
            [modulo for modulo in modulosNPM if modulo['nombre'] == self._tablaModulos.item(self._tablaModulos.selection()[0], 'values')[0]][0] if self._tablaModulos.selection() else {}
        ))
        
        centerWindow(self.root)
    
    def iniciar(self):
        self.root.mainloop()