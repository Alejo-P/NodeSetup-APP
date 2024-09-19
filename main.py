import json
import tkinter as tk
from tkinter import Frame, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import * # type: ignore
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import queue, os, shutil, threading, subprocess
import time, ast, tempfile
from typing import Literal
from Actions import (
    clearQueue,
    doNothing,
    getBranchCommitsLog,
    getCurrentBrach,
    preventCloseWindow,
    getEvents,
    getVersionOf,
    setEvent,
    writeLog,
    getPathOf,
    runCommand,
    loadImageTk,
    getGitBranches,
    getDetailedModules
)
from Vars import listaArgumentos, carpetas, archivos, archivos_p, Registro_hilos, respuestas, registro_commits, BASE_DIR
from serverWindow import ServerWindow
from version import __version__ as appVersion

class NodeSetupApp(ttk.Window):
    def __init__(self):
        self._version = getVersionOf("node")
        self._versionGit = getVersionOf("git")
        self._veri_code = getPathOf("code")
        self._npm_path = getPathOf("npm")
        self._git_path = getPathOf("git")
        self._referencias = {}
        self._lista_widgets= []
        self._version_NPM = None
        self._ruta_temporal = tempfile.mkdtemp()
        
        if self._version is None:
            messagebox.showerror("Error", "Node.js no está instalado en el sistema")
            quit()
        
        super().__init__(themename="superhero")
        
        self.title("NodeSetup")
        self.resizable(0, 0)  # type: ignore
        self.protocol("WM_DELETE_WINDOW", lambda: preventCloseWindow("Accion no permitida", "No puede cerrar esta ventana, hay tareas que requieren usarla", "WARNING"))
        
        
        self._checkVars = []
        self._imagenes = {}
        self._ruta = tk.StringVar()
        self._cambiarDirectorio = tk.BooleanVar(value=False)
        self._modulosNPM = getDetailedModules()
        
        self._idAfterBar = "Temporal"
        self.frameInfo = ttk.LabelFrame(self, width=100, text="Informacion:", bootstyle=INFO) # type: ignore
        self.lbl_titulo = ttk.Label(self)
        self.lbl_versionApp = ttk.Label(self.frameInfo)
        self.lbl_version = ttk.Label(self.frameInfo)
        self.lbl_versionNPM = ttk.Label(self.frameInfo)
        self._lbl_ruta = ttk.Label(self, text="Ruta", width=50)
        self.entry_ruta = ttk.Entry(self, textvariable=self._ruta, width=50)
        self.entry_ruta.bind(
            "<Return>",
            lambda event: self.iniciar_creacion_proyecto()
        )
        self.boton_ruta = ttk.Button(self, text="Explorar", command=self.abrir_ruta, bootstyle=(WARNING, OUTLINE), width=50) # type: ignore
        self.frm_check = ttk.Labelframe(self, width=50, text="Opciones", bootstyle=PRIMARY) #type: ignore
        self._botonModulos = ttk.Button(self.frm_check, text="Instalar modulos", bootstyle=SECONDARY) # type: ignore
        self.labelGit = ttk.Label(self.frm_check, cursor="hand2")
        self.labelGit.bind(
            "<Button-1>",
            lambda event: self._ventanaOpcionesGit()
        )
        self.sec_botones = ttk.Frame(self)
        self.btn_crear = ttk.Button(self.sec_botones, text="Crear", command=self.iniciar_creacion_proyecto, bootstyle=(PRIMARY, OUTLINE), width=10) # type: ignore
        self.btn_salir = ttk.Button(self.sec_botones, text="Salir", command=lambda: preventCloseWindow("Accion no permitida", "No puede cerrar esta ventana, hay tareas que requieren usarla", "WARNING"), bootstyle=(DANGER, OUTLINE), width=10) # type: ignore
        
        self._crearRuta = tk.BooleanVar(value=True)
        self._chk_Ruta = ttk.Checkbutton(self, text="Crear ruta si no existe", variable=self._crearRuta, bootstyle="success-round-toggle", padding=6) # type: ignore
        
        self._eliminarContenido = tk.BooleanVar(value=True)
        self._chk_eliminarPrimero = ttk.Checkbutton(self, text="Eliminar todo el contenido de la carpeta", variable=self._eliminarContenido, bootstyle="success-round-toggle", padding=6) # type: ignore
        
        self._eliminarDatos = tk.BooleanVar(value=False)
        self._chk_eliminarEnFallo = ttk.Checkbutton(self, text="Eliminar contenido tras un fallo", variable=self._eliminarDatos, bootstyle="success-round-toggle", padding=6) # type: ignore
        
        self._pararEnFallo = tk.BooleanVar(value=False)
        self._chk_fallo = ttk.Checkbutton(self, text="Detener en caso de fallo", variable=self._pararEnFallo, bootstyle="success-round-toggle", padding=6) # type: ignore
        
        self.frm_progreso = ttk.Labelframe(self, text="Progreso:", width=100, bootstyle=PRIMARY) # type: ignore
        self.lbl_progreso = ttk.Label(self.frm_progreso, text="Descripcion: Ninguna tarea en ejecucion")
        self.frm_progreso.grid_columnconfigure(0, weight=1)
        self.progreso = ttk.Progressbar(self.frm_progreso, orient='horizontal', mode='determinate', maximum=100, bootstyle="success") # type: ignore
        
        self.completado = tk.BooleanVar(value=False)
        
        self.frm_estadoEv = ttk.LabelFrame(self, text="Registro de eventos", width=100)
        self.textArea = ScrolledText(self.frm_estadoEv, wrap=tk.WORD, width=50, height=15, font=('Arial', 8))
        #self.textArea.pack(expand=True, fill=tk.BOTH)
        
        self.repoURL = tk.StringVar()
        
        self._almacenar_imagenes()
        self.crear_widgets()
        self._menuContextual(None)
    
    def _almacenar_imagenes(self):
        # Cargar la imagen y guardarla en el diccionario
        ruta_assets = os.path.join(BASE_DIR, "assets")
        self._imagenes["Git"] = loadImageTk(os.path.join(ruta_assets, "gitIcon.png"), 25, 25)
        self._imagenes["Check"] = loadImageTk(os.path.join(ruta_assets, "checkIcon.png"), 25, 25)
        self._imagenes["Error"] = loadImageTk(os.path.join(ruta_assets, "errorIcon.png"), 25, 25)
    
    def mostrar_imagenes(self):
        try:
            self.labelGit.config(image=self._imagenes["Git"], text="Git", compound=tk.LEFT)
        except Exception as e:
            print(f"Error al cargar las imagenes: {e}")
    
    def _menuContextual(self, event):
        def showMenu(event):
            try:
                self._menu.tk_popup(event.x_root, event.y_root)
            finally:
                self._menu.grab_release()
        
        def hideMenu(event):
            self._menu.unpost()
        
        def _ventanaEditor():
            self.lock_unlock_widgets(estado="disabled")
            if not os.listdir(self._ruta_temporal):
                respuesta = runCommand([self._npm_path, "init", "-y"], self._ruta_temporal)
                if isinstance(respuesta, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al crear el archivo package.json: {respuesta}")
                    self.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana())
                    lista.put(False)
                    return
                
                respuesta = runCommand([self._npm_path, "install", "express"], self._ruta_temporal)
                if isinstance(respuesta, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al instalar el paquete express: {respuesta}")
                    self.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana())
                    lista.put(False)
                    return
                
                os.mkdir(os.path.join(self._ruta_temporal, "src"))
                os.mkdir(os.path.join(self._ruta_temporal, "public"))
                os.mkdir(os.path.join(self._ruta_temporal, "views"))
                    
                with open(os.path.join(self._ruta_temporal, "views", "index.html"), "w") as archivo:
                    archivo.write(
                        "<!DOCTYPE html>\n<html>\n<head>\n\t<title>Document</title>\n</head>\n<body>\n\t<h1>¡Hola Mundo!</h1>\n</body>\n</html>"
                    )
                    
                with open(os.path.join(self._ruta_temporal, "public", "styles.css"), "w", encoding="utf-8") as archivo:
                    archivo.write(
                        "body {\n\tfont-family: Arial, sans-serif;\n\tbackground-color: #f0f0f0;\n}\n\nh1 {\n\tcolor: #333;\n\ttext-align: center;\n}"
                    )
                    
                with open(os.path.join(self._ruta_temporal, "public", "scripts.js"), "w", encoding="utf-8") as archivo:
                    archivo.write("console.log('¡Hola Mundo!')")
                
                with open(os.path.join(self._ruta_temporal, "src", "index.js"), "w") as archivo:
                    archivo.write(
                        "const express = require('express')\nconst path = require('path');\nconst app = express();\n\napp.use(express.static('public'));\n\napp.get('/', (req, res) => {\n\tres.sendFile(path.join(__dirname, '..', 'views', 'index.html'));\n});\n\napp.listen(3000, () => {\n\tconsole.log('Servidor iniciado en el puerto 3000');\n});"
                    )
                
                with open(os.path.join(self._ruta_temporal, "appSettings.json"), "w", encoding="utf-8") as archivo:
                    JSON_content = json.dumps({
                        "isLoadedModules": False,
                        "isServerRunning": False,
                        "modulesLoaded" : []
                    }, indent=4)
                    archivo.write(JSON_content)
            
            lista.put(True)
            
        def _verificarCompletado():
            try:
                resultado = lista.get_nowait()
                if resultado:
                    self.lbl_progreso.config(text="Descripcion: Proyecto creado con éxito")
                    self.progreso.stop()
                    self.progreso.config(value=0, mode="determinate", maximum=100, bootstyle="success") # type: ignore
                    self.lock_unlock_widgets(estado="normal")
                    self.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana())
                    srv = ServerWindow(self, self._ruta_temporal)
                    srv.iniciar()
                else:
                    self.lbl_progreso.config(text="Descripcion: Error al crear el proyecto")
                    self.progreso.stop()
                    self.progreso.config(value=0, mode="determinate", maximum=100, bootstyle="success") # type: ignore
                    self.lock_unlock_widgets(estado="normal")
                    self.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana())
            except queue.Empty:
                self.protocol("WM_DELETE_WINDOW", doNothing)
                self.after(100, _verificarCompletado)
                return
                
            clearQueue(lista)
        
        def _iniciarVentana():
            self.protocol("WM_DELETE_WINDOW", doNothing)
            self.lbl_progreso.config(text="Descripcion: Cargando archivos e iniciando el editor de código")
            self.progreso.config(value=0, maximum=100, mode="indeterminate", bootstyle="success") # type: ignore
            self.progreso.start()
            threading.Thread(target=_ventanaEditor).start()
            self.after(100, _verificarCompletado)
            
        self._menu = tk.Menu(self, tearoff=0)
        
        submenu_Herramientas = tk.Menu(self._menu, tearoff=0)
        submenu_Herramientas.add_command(label="Editor de código", command=lambda: _iniciarVentana())
        
        self._menu.add_command(label="Opciones de la aplicación", state="disabled")
        self._menu.add_separator()
        self._menu.add_cascade(label="Herramientas", menu=submenu_Herramientas)
        self._menu.add_separator()
        self._menu.add_command(label="Acerca de", state="disabled")
        
        lista = queue.Queue()
        
        self._menu.bind("<FocusOut>", hideMenu)
        self.bind("<Button-3>", showMenu)
    
    def _ventanaOpcionesGit(self):
        def cerrarVentana():
            nonlocal entries, callbackName, callbackName2
            if callbackName:
                self._ruta.trace_remove("write", callbackName)
            
            if callbackName2:
                self._ruta.trace_remove("write", callbackName2)
            
            ventana.destroy()
            del entries, callbackName, callbackName2
        
        def _updateButton():
            if all(entries.values()):
                btnInicio.config(state="normal")
            else:
                btnInicio.config(state="disabled")
        
        def ValidarEntry():
            nonlocal entries
            if self.repoURL.get():
                entries["RepoURL"] = True
            else:
                entries["RepoURL"] = False
            
            _updateButton()
        
        def ValidarRuta():
            nonlocal entries
            btnInicio.config(state="disabled")
            if not self._ruta.get():
                mensajeRuta.config(text="Debe seleccionar una ruta", foreground="red")
                entries["Ruta"] = False
                _updateButton()
                return
            
            if not os.path.isdir(self._ruta.get()):
                mensajeRuta.config(text="La ruta no es un directorio", foreground="red")
                entries["Ruta"] = False
                _updateButton()
                return
            
            if not os.path.exists(self._ruta.get()):
                mensajeRuta.config(text="La ruta no existe", foreground="red")
                entries["Ruta"] = False
                _updateButton()
                return
                            
            if not os.access(self._ruta.get(), os.W_OK):
                mensajeRuta.config(text="No tiene permisos para escribir en la ruta", foreground="red")
                entries["Ruta"] = False
                _updateButton()
                return
                
            mensajeRuta.config(text="Ruta valida", foreground="green")
            entries["Ruta"] = True
            _updateButton()
        
        def iniciarClonacion():
            if not self.repoURL.get():
                messagebox.showwarning("Advertencia", "Debe ingresar una URL valida")
                return
            
            ventana.protocol("WM_DELETE_WINDOW", doNothing)
            frame_progreso.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            self._centrar_ventana(ventana, True)
            barraProgreso.start()
            btnInicio.config(state="disabled")
            e1.configure(state="disabled")
            e2.configure(state="disabled")
            nombre_repo = self.repoURL.get().split('/')[-1].replace('.git', '')
            resultado = runCommand([self._git_path, "clone", self.repoURL.get()], self._ruta.get())
            if isinstance(resultado, subprocess.CalledProcessError):
                messagebox.showerror("Error", f"Error al clonar el repositorio: {resultado}")
                e1.configure(state="normal")
                e2.configure(state="normal")
                return
            
            if self._cambiarDirectorio.get():
                try:
                    temRuta = self._ruta.get()
                    self._ruta.set(f"{temRuta}/{nombre_repo}")
                except Exception as e:
                    print(e)
            
            e1.configure(state="normal")
            e2.configure(state="normal")
            barraProgreso.stop()
            frame_progreso.grid_forget()
            btnInicio.config(state="normal")
            ventana.protocol("WM_DELETE_WINDOW", cerrarVentana)
            self._centrar_ventana(ventana, True)
            messagebox.showinfo("Información", "Repositorio clonado con éxito")
        
        def ValidarRepoGit():
            if self._ruta.get() and os.path.isdir(self._ruta.get()):
                rutacarpetaGIT = os.path.join(self._ruta.get(), ".git")
                if not os.path.isdir(rutacarpetaGIT):
                    mensajeRepo.config(text="No se encontro un repositorio Git", foreground="orange")
                    mensajeHistorial.config(text="No se encontro un repositorio Git", foreground="orange")
                    botonOK.config(state="disabled")
                    ecommit.config(state="disabled")
                    combo.config(state="disabled")
                    comboRama["values"] = ("No se pudo extraer las ramas",)
                    comboRama.current(0)
                    comboRama.config(state="disabled")
                    _limpiarTabla()
                    return
                
                mensajeRepo.config(text="Repositorio Git encontrado", foreground="green")
                mensajeHistorial.config(text="Repositorio Git encontrado", foreground="green")
                botonOK.config(state="normal")
                ecommit.config(state="normal")
                combo.config(state="readonly")
                comboRama.config(state="readonly")
                mostrarRamas()
                obtenerLogs()
            else:
                mensajeRepo.config(text="La ruta no es un directorio", foreground="red")
                mensajeHistorial.config(text="La ruta no es un directorio", foreground="red")
                botonOK.config(state="disabled")
                ecommit.config(state="disabled")
                combo.config(state="disabled")
                comboRama["values"] = ("Directorio no valido",)
                comboRama.current(0)
                comboRama.config(state="disabled")
                _limpiarTabla()
        
        def insertarPlaceHolder(event):
            estadoEntry = ecommit["state"]
            if estadoEntry == "disabled":
                ecommit.config(state="normal")
                
            if not mensajeCommit.get():
                ecommit.config(foreground="gray")
                mensajeCommit.set("Ingrese un mensaje de confirmación ...")
            
            if estadoEntry == "disabled":
                ecommit.config(state="disabled")
                
        def limpiarPlaceHolder(event):
            if mensajeCommit.get() == "Ingrese un mensaje de confirmación ...":
                ecommit.config(foreground="black")
                mensajeCommit.set("")
        
        def CambiarPestaña(event):
            nonlocal callbackName, callbackName2
            try:
                indice = notebook.index(notebook.select())
                notebook.select(indice)
            except Exception as e:
                print(e)
        
        def RealizarCommit():
            nonlocal ramaActual
            if mensajeCommit.get() == "Ingrese un mensaje de confirmación ...":
                messagebox.showwarning("Advertencia", "Debe ingresar un mensaje de confirmación")
                return
            
            if comboRama.get() != ramaActual:
                seleccion = messagebox.askyesno("Advertencia", "La rama de trabajo no es la rama actual del repositorio, ¿Desea continuar?")
                if seleccion == "no":
                    return
                
                resultado = runCommand([self._git_path, "checkout", comboRama.get()], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al cambiar de rama: {resultado}")
                    return
                messagebox.showinfo("Información", "Rama cambiada con éxito")
            
            if combo.get() == "Confirmar":
                resultado = runCommand([self._git_path, "add", "."], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al agregar los cambios: {resultado}")
                    return
                
                resultado = runCommand([self._git_path, "commit", "-m", mensajeCommit.get()], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al confirmar los cambios: {resultado}")
                    return
                
                messagebox.showinfo("Información", "Cambios confirmados con éxito")
            elif combo.get() == "Confirmar y enviar":
                resultado = runCommand([self._git_path, "add", "."], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al agregar los cambios: {resultado}")
                    return
                
                resultado = runCommand([self._git_path, "commit", "-m", mensajeCommit.get()], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al confirmar los cambios: {resultado}")
                    return
                
                resultado = runCommand([self._git_path, "push"], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al enviar los cambios: {resultado}")
                    return
                
                messagebox.showinfo("Información", "Cambios confirmados y enviados con éxito")
        
        def mostrarRamas():
            def _obtenerRamas():
                nonlocal ramaActual
                ramas = getGitBranches(self._ruta.get())
                ramaActual = getCurrentBrach(ramas)
                respuestas.put(tuple(ramas.keys()))
            
            threading.Thread(target=_obtenerRamas).start()
            ventana.after(100, _actualizarComboRamas)
            comboRama["values"] = ("Obteniendo ramas...",)
            comboRama.current(0)
           
        def _actualizarComboRamas():
            try:
                resultado = respuestas.get_nowait()
                if os.path.exists(os.path.join(self._ruta.get(), ".git")) and self._ruta.get():
                    comboRama["values"] = resultado
                    try:
                        comboRama.current(resultado.index(ramaActual))
                    except ValueError:
                        comboRama.current(0)
            except queue.Empty:
                ventana.after(100, _actualizarComboRamas)
                return
            
            clearQueue(respuestas)
         
        def obtenerLogs():
            def _obtenerCommits():
                logs = getBranchCommitsLog(self._ruta.get())
                registro_commits.put(logs)
            
            threading.Thread(target=_obtenerCommits).start()
            ventana.after(100, _actualizarTabla)
        
        def _actualizarTabla():
            try:
                resultado = registro_commits.get_nowait()
                if os.path.exists(os.path.join(self._ruta.get(), ".git")) and self._ruta.get():
                    tablaCommits.delete(*tablaCommits.get_children())
                    for i, commit in enumerate(resultado, 1):
                        tablaCommits.insert("", "end", text=f"#{i}", values=(commit["id"], commit["rama"], commit["mensaje"]))
            except queue.Empty:
                ventana.after(100, _actualizarTabla)
                return
            
            clearQueue(registro_commits)
        
        def _limpiarTabla():
            tablaCommits.delete(*tablaCommits.get_children())
        
        def Comenzar():
            threading.Thread(target=iniciarClonacion).start()
        
        ventana = tk.Toplevel(self)
        ventana.title("Opciones de Git")
        ventana.resizable(0, 0) # type: ignore
        ventana.transient(self)
        ventana.protocol("WM_DELETE_WINDOW", cerrarVentana)
        entries = {
            "RepoURL": False,
            "Ruta": False
        }
        ramaActual = ""
        
        frame_version = ttk.LabelFrame(ventana, text="Información de Git")
        ttk.Label(frame_version, text="Version de Git:").grid(row=0, column=0)
        ttk.Label(frame_version, text=self._versionGit if self._versionGit else "").grid(row=0, column=1)
        frame_version.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        notebook = ttk.Notebook(ventana, bootstyle=SECONDARY) # type: ignore
        mensajeCommit = tk.StringVar()
        
        frameClonacion = ttk.Frame(notebook)
        frameClonacion.grid_columnconfigure(0, weight=1)
        frameClonacion.grid_columnconfigure(1, weight=1)
        
        ttk.Label(frameClonacion, text="URL repositorio").grid(row=1, column=0, columnspan=2)
        e1 = ttk.Entry(frameClonacion, width=50, textvariable=self.repoURL)
        e1.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        ttk.Label(frameClonacion, text="Ruta para la clonación").grid(row=3, column=0, columnspan=2)
        e2 = ttk.Entry(frameClonacion, width=50, textvariable=self._ruta)
        e2.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        mensajeRuta = ttk.Label(frameClonacion) 
        mensajeRuta.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        btnInicio = ttk.Button(frameClonacion, text="Clonar", command=lambda: Comenzar(), state="disabled")
        btnInicio.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Checkbutton(frameClonacion, text="Cambiar automaticamente al nuevo directorio", variable=self._cambiarDirectorio).grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        frame_progreso = ttk.LabelFrame(frameClonacion, text="Progreso")
        frame_progreso.columnconfigure(0, weight=1)
        barraProgreso = ttk.Progressbar(frame_progreso, orient='horizontal', mode='indeterminate', length=100)
        barraProgreso.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        frameConfirmacion = ttk.Frame(notebook)
        frameConfirmacion.grid_columnconfigure(0, weight=1)
        frameConfirmacion.grid_columnconfigure(1, weight=1)
        
        ttk.Label(frameConfirmacion, text="Ruta del repositorio").grid(row=0, column=0, columnspan=2)
        eruta = ttk.Entry(frameConfirmacion, width=50, textvariable=self._ruta)
        eruta.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        mensajeRepo = ttk.Label(frameConfirmacion)
        mensajeRepo.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(frameConfirmacion, text="Mensaje de confirmacion").grid(row=3, column=0, columnspan=2)
        ecommit = ttk.Entry(frameConfirmacion, textvariable=mensajeCommit, width=50)
        ecommit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(frameConfirmacion, text="Rama:").grid(row=5, column=0)
        comboRama = ttk.Combobox(frameConfirmacion, state="readonly")
        comboRama.grid(row=5, column=1, padx=5, pady=5)
        
        opciones = ["Confirmar", "Confirmar y enviar"]
        ttk.Label(frameConfirmacion, text="Acciones").grid(row=6, column=0)
        combo = ttk.Combobox(frameConfirmacion, values=opciones, state="readonly")
        combo.current(0)
        combo.grid(row=6, column=1, padx=5, pady=5)
        
        botonOK = ttk.Button(frameConfirmacion, text="OK", command=lambda: RealizarCommit(), state="disabled")
        botonOK.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        frameLogs = ttk.Frame(notebook)
        frameLogs.grid_columnconfigure(0, weight=1)
        ttk.Label(frameLogs, text="Ruta del repositorio").grid(row=0, column=0)
        ttk.Entry(frameLogs, width=50, textvariable=self._ruta).grid(row=1, column=0, padx=5, pady=5)
        
        mensajeHistorial = ttk.Label(frameLogs)
        mensajeHistorial.grid(row=2, column=0, padx=5, pady=5)
        
        tablaCommits = ttk.Treeview(frameLogs, show="headings", selectmode="browse")
        tablaCommits["columns"] = ("Id", "Rama", "Mensaje")
        tablaCommits.column("Id", anchor=tk.W, width=60)
        tablaCommits.column("Rama", anchor=tk.W, width=80)
        tablaCommits.column("Mensaje", anchor=tk.W, width=300)
        tablaCommits.heading("Id", text="ID", anchor=tk.W)
        tablaCommits.heading("Rama", text="Rama", anchor=tk.W)
        tablaCommits.heading("Mensaje", text="Mensaje", anchor=tk.W)
        tablaCommits.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        
        yScroll = ttk.Scrollbar(frameLogs, orient="vertical", command=tablaCommits.yview)
        yScroll.grid(row=3, column=1, sticky="ns")
        tablaCommits.configure(yscrollcommand=yScroll.set)
        
        notebook.add(frameClonacion, text="Clonar repositorio")
        notebook.add(frameConfirmacion, text="Confirmar cambios")
        notebook.add(frameLogs, text="Registro de commits")
        
        notebook.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        e1.bind("<KeyRelease>", lambda event: ValidarEntry())
        
        notebook.bind("<<NotebookTabChanged>>", CambiarPestaña)
        
        callbackName = self._ruta.trace_add("write", lambda *args: ValidarRuta())
        callbackName2 = self._ruta.trace_add("write", lambda *args: ValidarRepoGit())
        
        ecommit.bind("<FocusIn>", limpiarPlaceHolder)
        ecommit.bind("<FocusOut>", insertarPlaceHolder)
        
        ValidarEntry()
        ValidarRuta()
        ValidarRepoGit()
        insertarPlaceHolder(None)
        
        self._centrar_ventana(ventana)
        
    def crear_widgets(self):
        def cargarinfo_versionNPM():
            self.lbl_versionNPM.config(text="Version de NPM: Cargando...")
            
            versionNPM = runCommand([self._npm_path, "-v"])
            if isinstance(versionNPM, subprocess.CalledProcessError):
                messagebox.showerror("Error", f"Error al obtener la version de NPM: {versionNPM}")
                self.lbl_versionNPM.config(text="Version de NPM: Error")
            else:
                self.lbl_versionNPM.config(text=f"Version de NPM: {versionNPM.stdout.strip()}")
            
            versiones_paquetesNPM = runCommand([self._npm_path, "show", "npm", "versions", "--depth=0"])
            lista_versionesNPM = list(ast.literal_eval(f"{versiones_paquetesNPM.stdout.strip()}"))
            
            if versionNPM.stdout.strip() < lista_versionesNPM[-1]:
                messagebox.showinfo("Debe actualizar NPM", f"Se encontro una nueva version de NPM:\nTiene la version: {versionNPM.stdout.strip()}\nSe encontro la version: {lista_versionesNPM[-1]}")
            self.update_idletasks()
            self.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana())
            self.btn_salir.config(command=lambda: self.cerrar_ventana())
        
        def ventana_seleccionModulos():
            def restablecer_seleccion():
                for dic in self._modulosNPM:
                    dic["usar"].set(False)
                    dic["global"].set(False)
                    dic["argumento"].set("")
                    dic["version"].set(dic["versiones"][-1] if dic["versiones"] else "Ocurrio un Error")
            
            def update_modulos_ui(msg_estado, progress_bar, modulos: tk.Toplevel):
                def CargarInfoModulos(listaModulos):
                    for dic in listaModulos:
                        if not dic["versiones"]:
                            versionesPaquetes = runCommand([self._npm_path, "show", dic["nombre"].lower(), "versions", "--depth=0"])
                            if isinstance(versionesPaquetes, subprocess.CalledProcessError):
                                writeLog("ERROR", f"Error al obtener versiones de {dic['nombre']}: {versionesPaquetes}", CargarInfoModulos.__name__)
                                return
                            dic["versiones"] = list(ast.literal_eval(f"{versionesPaquetes.stdout.strip()}"))

                        if not dic["usar"]:
                            dic["usar"] = tk.BooleanVar(value=False)
                        if not dic["global"]:
                            dic["global"] = tk.BooleanVar(value=False)
                        if not dic["argumento"]:
                            dic["argumento"] = tk.StringVar(value=listaArgumentos[0])
                        if not dic["version"]:
                            dic["version"] = tk.StringVar(value=dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")

                def CrearWidgets(listaModulos):
                    if not self._lista_widgets:
                        for dic in listaModulos:
                            check_usar = ttk.Checkbutton(modulos, variable=dic["usar"], bootstyle="success-round-toggle", padding=4) # type: ignore
                            label_nombre = ttk.Label(modulos, text=dic["nombre"], bootstyle=LIGHT, padding=4) # type: ignore
                            entry_argumento = ttk.Combobox(modulos, values=listaArgumentos, textvariable=dic["argumento"], state="readonly", bootstyle=SECONDARY, width=25) # type: ignore
                            combo_version = ttk.Combobox(modulos, values=dic["versiones"], textvariable=dic["version"], state="readonly", bootstyle=SECONDARY, width=25) # type: ignore
                            check_global = ttk.Checkbutton(modulos, variable=dic["global"], bootstyle="warning-round-toggle", padding=4) # type: ignore

                            self._lista_widgets.append([check_usar, label_nombre, entry_argumento, combo_version, check_global])

                def mostrar_widgets():
                    try:
                        for i, widget_list in enumerate(self._lista_widgets, 2):
                            for j, widget in enumerate(widget_list):
                                if isinstance(widget, (ttk.Checkbutton, ttk.Combobox)):
                                    widget.grid(row=i, column=j % len(encabezado_tabla), padx=5, pady=2)
                                elif isinstance(widget, ttk.Label):
                                    widget.grid(row=i, column=j % len(encabezado_tabla), padx=5, pady=2, sticky="w")

                        valor = len(self._lista_widgets) + 2  # Calcular la posición del botón Restablecer
                        frame_botones = ttk.Frame(modulos, width=100)
                        frame_botones.grid(row=valor, column=0, columnspan=len(encabezado_tabla), pady=5, sticky="nsew")

                        frame_botones.grid_columnconfigure(0, weight=1)
                        frame_botones.grid_columnconfigure(1, weight=1)

                        ttk.Button(frame_botones, text="Guardar", command=lambda: Cerrar_ventana()).grid(row=0, column=0, padx=10, sticky="nsew")
                        ttk.Button(frame_botones, text="Restablecer", command=restablecer_seleccion).grid(row=0, column=1, padx=10, sticky="nsew")

                        self._centrar_ventana(modulos, True)
                    except tk.TclError as e:
                        print(f"Error al mostrar widgets: {e}")

                def iniciar_carga():
                    n_listas = 6
                    progress_bar.start()
                    msg_estado.config(text="Cargando módulos de NPM... No cierre la ventana!")

                    if not self._lista_widgets:
                        modulos.protocol("WM_DELETE_WINDOW", lambda: doNothing())
                        for sublistas in dividir_lista(self._modulosNPM, n_listas):
                            hilo = threading.Thread(target=CargarInfoModulos, args=(sublistas,))
                            Registro_hilos.append(hilo)

                        for hilo in Registro_hilos:
                            hilo.start()

                        for hilo in Registro_hilos:
                            hilo.join()

                        if progress_bar.winfo_exists() and msg_estado.winfo_exists():
                            progress_bar.stop()
                            progress_bar.grid_forget()
                            msg_estado.grid_forget()

                        Registro_hilos.clear()

                    CrearWidgets(self._modulosNPM)
                    self._centrar_ventana(modulos)

                    # Mostrar los widgets en la interfaz
                    modulos.after(0, mostrar_widgets)  # Programar mostrar_widgets en el hilo principal

                    modulos.protocol("WM_DELETE_WINDOW", lambda: Cerrar_ventana())

                # Llama a iniciar_carga para empezar el proceso
                iniciar_carga()

            def Cerrar_ventana():
                self.modulos.withdraw() #type:ignore  # Ocultar la ventana en lugar de destruirla
                # Puedes realizar otras acciones al cerrar la ventana si lo necesitas

            if not hasattr(self, "modulos") or not self.modulos.winfo_exists(): # type: ignore
                self.modulos = tk.Toplevel(self) # type: ignore
                self.modulos.title("Escoje los módulos a instalar") # type: ignore
                self.modulos.resizable(0, 0) # type:ignore
                self.modulos.transient(self) # type: ignore

                encabezado_tabla = [
                    "Seleccionar",
                    "Nombre del módulo",
                    "Argumento",
                    "Versión",
                    "Inst. Global"
                ]

                for i, texto in enumerate(encabezado_tabla):
                    ttk.Label(self.modulos, text=texto).grid(row=0, column=i, padx=5, pady=2) # type: ignore

                # Añadir un separador horizontal a la ventana
                ttk.Separator(self.modulos, orient="horizontal").grid(row=1, column=0, columnspan=len(encabezado_tabla), sticky="ew") # type: ignore

                # Añadir una barra de progreso
                progress_bar = ttk.Progressbar(self.modulos, orient='horizontal', mode='indeterminate', length=280, style="TProgressbar") # type: ignore
                msg_estado = ttk.Label(self.modulos) # type: ignore

                progress_bar.grid(row=2, column=0, columnspan=len(encabezado_tabla), padx=5, pady=10)
                msg_estado.grid(row=3, column=0, columnspan=len(encabezado_tabla), padx=5, pady=2)

                self._centrar_ventana(self.modulos) # type: ignore

                # Llama a la función para cargar y actualizar los módulos
                threading.Thread(target=update_modulos_ui, args=(msg_estado, progress_bar, self.modulos)).start() # type: ignore
            else:
                self.modulos.deiconify() # type: ignore  # Mostrar la ventana si ya existe y está oculta
        
        self.lbl_titulo.config(text="Configurar Entorno Node", font=("Arial", 20, "bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=3)
        
        self.frameInfo.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.frameInfo.grid_columnconfigure(0, weight=1)
        self.frameInfo.grid_columnconfigure(1, weight=1)
        self.frameInfo.grid_columnconfigure(2, weight=1)
        
        self.lbl_versionApp.config(text=f"Version app: {appVersion}")
        self.lbl_versionApp.grid(row=0, column=0)
        
        if self._version:
            self.lbl_version.config(text=f"Versión de Node: {self._version}")
            self.lbl_version.grid(row=0, column=1)
        
        self.lbl_versionNPM.grid(row=0 , column=2)
        
        
        threading.Thread(target=cargarinfo_versionNPM).start()        
        
        self._lbl_ruta.grid(row=2, column=0, sticky="s")
        self.entry_ruta.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=5)
        self.boton_ruta.grid(row=4, column=0, columnspan=2, sticky="ew", padx=4)
        self._chk_eliminarPrimero.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=4)
        self._chk_Ruta.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=4)
        self._chk_eliminarEnFallo.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=4)
        self._chk_fallo.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=4)
        
        self.frm_check.grid(row=2, rowspan=8, column=2, padx=5)
        
        opciones = [
            "Crear archivos\nadicionales",
            "Abrir en VS Code\nal finalizar"
        ]
        
        self._opciones = [False for _ in range(len(opciones))]
        
        self._botonModulos["command"] = ventana_seleccionModulos
        self._botonModulos.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
        
        start = 1
        if self._versionGit:
            self.labelGit.grid(column=0, row=start)
            start +=1
        
        for i, item in enumerate(opciones, start):
            check_var = tk.BooleanVar(value=False)
            self._checkVars.append({item: check_var})
            if item == "Abrir en VS Code\nal finalizar":
                if self._veri_code:
                    ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="normal").grid(column=0, row=i, sticky="nsew", padx=5, pady=2)
                else:
                    ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="disabled").grid(column=0, row=i, sticky="nsew", padx=5, pady=2)
            else:   
                ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="normal").grid(column=0, row=i, sticky="nsew", padx=5, pady=2)
        
        self.sec_botones.grid(row=10, column=0, columnspan=3, pady=5)
        
        self.btn_crear.grid(row=0, column=0, padx=40)
        self.btn_salir.grid(row=0, column=1, padx=40)

        self.frm_progreso.grid(row=11, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")
        self.lbl_progreso.grid(row=0, column=0, padx=5, sticky="nsew")
        self.progreso.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

    def _centrar_ventana(self, ventana:tk.Tk | tk.Toplevel | None = None, restablecer_tamaño=False):
        if not ventana:
            ventana = self
        
        if restablecer_tamaño:
            ventana.wm_geometry("")
            
        ventana.update_idletasks()
        width = ventana.winfo_width()
        height = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana.winfo_screenheight() // 2) - (height // 2)
        ventana.geometry(f"{width}x{height}+{x}+{y}")
    
    def _borrar_contenido_ruta(self):
        archivos, carpetas = lista_archivos_directorios(self.entry_ruta.get())
        ruta = self.entry_ruta.get()
        for archivo in archivos:
            ruta_completa = os.path.join(ruta, archivo)
            os.remove(ruta_completa)
        
        for carpeta in carpetas:
            ruta_completa = os.path.join(ruta, carpeta)
            shutil.rmtree(ruta_completa)
    
    def abrir_ruta(self):
        self.ruta = filedialog.askdirectory()
        if self.ruta:
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, self.ruta)
    
    def iniciar_creacion_proyecto(self):
        threading.Thread(target=self.crear_proyecto).start()

    def lock_unlock_widgets(self, ventana: tk.Tk | tk.Toplevel | None = None, estado: Literal["normal", "disabled"] = "normal"):
        if ventana is None:
            ventana = self
        
        for item in ventana.winfo_children():
            if isinstance(item, (ttk.Entry, ttk.Button, ttk.Checkbutton, ttk.Radiobutton, ttk.Combobox)):
                item.config(state=estado)  # type: ignore
            elif isinstance(item, (ttk.LabelFrame, ttk.Frame, ttk.Label)):
                for child in item.winfo_children():
                    if isinstance(child, (ttk.Entry, ttk.Button, ttk.Checkbutton, ttk.Radiobutton, ttk.Combobox)):
                        child.config(state=estado)  # type: ignore
    
    def crear_proyecto(self):
        def incrementar_progreso(progreso:ttk.Progressbar, incremento:int | float, objetivo:int | float, delay:int=30):
            if self._idAfterBar:
                if progreso['value'] < objetivo:
                    progreso['value'] += incremento
                    self._idAfterBar = self.after(delay, incrementar_progreso, progreso, incremento, objetivo, delay)
                else:
                    progreso['value'] = objetivo
        
        def conteo_tareas():
            total_pasos = 1
            for dic in self._modulosNPM:
                if dic["usar"] is not None and dic["usar"].get():
                    total_pasos += 1
            
            for dic in self._checkVars:
                dic = dict(dic)
                for clave, var in dic.items():
                    if var.get() and clave == "Crear archivos\nadicionales":
                        total_pasos += 1
                    elif var.get() and clave == "Abrir en VS Code\nal finalizar":
                        total_pasos += 1
                    
            if self._crearRuta.get():
                total_pasos += 1
            
            if self._eliminarContenido.get():
                total_pasos += 1
            
            if self._eliminarDatos.get():
                total_pasos += 1
            
            return total_pasos
        
        def actualizar_progreso(mensaje: str, fill:bool=False):
            nonlocal pasos_completados, total_pasos
            self.lbl_progreso.config(text=f"Descripcion: {mensaje}")
            if fill:
                objetivo = 100
            else:
                pasos_completados += 1
                objetivo = (pasos_completados / total_pasos) * 100
            
            incremento = 1
            incrementar_progreso(self.progreso, incremento, objetivo, 50)
            self.update_idletasks()
        
        if len(self.entry_ruta.get()) == 0:
            messagebox.showwarning("Advertencia", "Debe seleccionar una ruta")
            return
        
        self.lock_unlock_widgets(estado="disabled")
        self.completado.set(False)
        total_pasos = conteo_tareas()
        pasos_completados = 0
        
        if self._crearRuta.get():
            try:
                actualizar_progreso("Creando ruta")
                self._crear_ruta()
            except NotADirectoryError as de:
                actualizar_progreso("Error en la ruta", fill=True)
                self.lock_unlock_widgets(estado="normal")
                messagebox.showerror("Ruta invalida", f"Error en la ruta: {de}")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear la ruta: {e}")
                self.lock_unlock_widgets(estado="normal")
                actualizar_progreso("Error al crear la ruta", fill=True)
                return
        
        if self._eliminarContenido.get():
            if messagebox.askyesno("Advertencia", f"Se eliminara todo el contenido de la carteta actual\n {self.entry_ruta.get()},\n ¿Desea contunuar?"):
                try:
                    actualizar_progreso("Eliminando contenido de la carpeta")
                    self._borrar_contenido_ruta()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar contenido de la carpeta: {e}")
                    self.lock_unlock_widgets(estado="normal")
                    actualizar_progreso("Error al eliminar contenido de la carpeta", fill=True)
                    return
            else:
                self.lock_unlock_widgets(estado="normal")
                actualizar_progreso("Operacion cancelada", fill=True)
                self.completado.set(True)
                return
        
        self.progreso['value'] = 0
        self.frm_estadoEv.grid(row=1, rowspan=11, column=4, columnspan=2, padx=5, sticky="nsew")
        self._centrar_ventana(restablecer_tamaño=True)
        def Iniciar_npm():
            try:
                actualizar_progreso("Inicializando proyecto Node")
                # Ejecutar `npm init -y` para inicializar el proyecto
                estado = runCommand([self._npm_path, "init", "-y"], self.entry_ruta.get())
                setEvent(
                    "INFO",
                    {
                        "Comando": " ".join([self._npm_path, "init", "-y"]),
                        "Resultado": estado,
                        "Funcion": Iniciar_npm.__name__
                    }
                )
                if isinstance(estado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al inicializar el proyecto Node: {estado}")
                    self.lock_unlock_widgets(estado="normal")
                    try:
                        self._borrar_contenido_ruta()
                    except:
                        pass
                    actualizar_progreso("Error al inicializar el proyecto Node", fill=True)
                    return int(-1)
                
                return int(0)
            except Exception as ex:
                messagebox.showerror("Error", f"Error al inicializar el proyecto Node: {ex}")
                self.lock_unlock_widgets(estado="normal")
                try:
                    self._borrar_contenido_ruta()
                except:
                    pass
                actualizar_progreso("Error al inicializar el proyecto Node", fill=True)
                self.completado.set(True)
                return int(-1)
        
        #threading.Thread(target=ActualizarScrolledText, args=(self.textArea, self, self.completado)).start()
        self.frm_estadoEv.after(0, self.actualizarEventsFrame, self.frm_estadoEv, self.completado)
        #threading.Thread(target=self.actualizarEventsFrame, args=(self.frm_estadoEv, self.completado)).start()
              
        if Iniciar_npm() == 0:
            for modulo in self._modulosNPM:
                if modulo["usar"] is not None and modulo["usar"].get():
                    actualizar_progreso(f"Instalando {modulo['nombre']}-{modulo["version"].get()} {'globalmente' if modulo['global'].get() else ''}")
                        
                    # Construir los argumentos del comando
                    comando = [
                        self._npm_path,
                        "i",
                        f"{modulo['nombre'].lower()}@{modulo['version'].get()}",
                    ]
                    
                    # Añadir el argumento global si está seleccionado
                    if modulo['global'].get():
                        comando.append("-g")
                    
                    # Añadir cualquier argumento adicional
                    argumento_adicional = modulo["argumento"].get()
                    if argumento_adicional:
                        comando.append(argumento_adicional)
                    
                    # Ejecutar el comando
                    estado = runCommand(comando, self.entry_ruta.get())
                    setEvent(
                        "INFO",
                        {
                            "Comando": " ".join(comando),
                            "Resultado": estado,
                            "Funcion": " ".join(comando)
                        }
                    )
                    if isinstance(estado, subprocess.CalledProcessError):
                        messagebox.showerror("Error", f"Error instalando {modulo['nombre']}: {estado}")
                        if self._pararEnFallo.get():
                            self.lock_unlock_widgets(estado="normal")
                            if self._eliminarDatos.get():
                                try:
                                    self._borrar_contenido_ruta()
                                except:
                                    pass
                            actualizar_progreso(f"Error al instalar {modulo['nombre']}", fill=True)
                            self.completado.set(True)
                            return
                       
            for dic in self._checkVars:
                dic = dict(dic)
                for clave, var in dic.items():
                    if var.get() and clave == "Crear archivos\nadicionales":
                        actualizar_progreso("Creando archivos adicionales")
                        self._crear_recursos_necesarios()
                    elif var.get() and clave == "Abrir en VS Code\nal finalizar":
                        actualizar_progreso("Abriendo en VS Code")
                        try:
                            code = os.system(f"code {self.entry_ruta.get()}")
                            if code != 0:
                                raise ValueError(f"codigo de estado: {code}, Razon probable: El comando no se pudo ejecutar")
                        except ValueError:
                            messagebox.showerror("Error", "Error al abrir en VS Code")
                            if self._pararEnFallo.get():
                                self.lock_unlock_widgets(estado="normal")
                                actualizar_progreso("Error al abrir en VS Code", fill=True)
                                return
            
            for archivo in archivos_p:
                actualizar_progreso(f"Creando {archivo}")
                with open(f"{self.entry_ruta.get()}/{archivo}", "w") as file:
                    if archivo == ".gitignore":
                        file.write("node_modules\n")
                        file.write(".env")
            
            self.lock_unlock_widgets(estado="normal")
            actualizar_progreso("Completado", True)
            messagebox.showinfo("Informacion", "Proyecto creado con éxito")
            self.completado.set(True)
            time.sleep(1)
            self.frm_estadoEv.grid_forget()
            self._centrar_ventana(restablecer_tamaño=True)
            del total_pasos, pasos_completados

    def _crear_ruta(self):
        if not os.path.exists(self.entry_ruta.get()):
            os.makedirs(self.entry_ruta.get())
    
    def _crear_recursos_necesarios(self):
        ruta = self.entry_ruta.get() + "/src"
        if not os.path.exists(ruta):
            os.makedirs(ruta)
        
        for archivo in archivos:
            with open(f"{ruta}/{archivo}", "w") as f:
                pass
            time.sleep(2)
        
        for carpeta in carpetas:
            if not os.path.exists(f"{ruta}/{carpeta}"):
                os.makedirs(f"{ruta}/{carpeta}")
    
    def cerrar_ventana(self, ventana:tk.Tk | tk.Toplevel | None = None):
        if not ventana:
            if self._idAfterBar:
                self.after_cancel(self._idAfterBar)
                self._idAfterBar = None

            ventana = self
        
        for item in ventana.winfo_children():
            item.destroy()
        
        ventana.destroy()
        
        # Eliminar la ruta temporal y todos los archivos y carpetas contenidos en la ruta
        if os.path.exists(self._ruta_temporal):
            shutil.rmtree(self._ruta_temporal)
    
    def actualizarEventsFrame(self, frame, completado):
        for widget in frame.winfo_children():
            widget.destroy()

        if completado.get():
            ttk.Label(frame, text="Tareas finalizadas").grid(row=0, column=0)
            return

        # Creación del Canvas
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Creación del Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configuración del Scrollbar en el Canvas
        canvas.config(yscrollcommand=scrollbar.set)

        # Creación de un Frame interno dentro del Canvas para contener los eventos
        contenido_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=contenido_frame, anchor="nw")

        # Función para ajustar el área desplazable
        def ajustar_scroll(event):
            canvas.config(scrollregion=canvas.bbox("all"))

        contenido_frame.bind("<Configure>", ajustar_scroll)

        # Creación de los eventos dentro del frame desplazable
        for evento in getEvents():  # Suponiendo que getEvents() es un método de la clase
            comando = evento["Comando"]
            if evento["Salida"]:
                bgColor = "#00FF00"
                mensaje = evento["Salida"]
                style = SUCCESS
                icon = self._imagenes["Check"]
            else:
                bgColor = "#FF0000"
                mensaje = evento["Error"]
                style = DANGER
                icon = self._imagenes["Error"]

            # SubFrame para cada evento
            subFrame = ttk.LabelFrame(contenido_frame, bootstyle=style) #type: ignore
            ttk.Label(subFrame, image=icon).grid(row=0, column=0)
            ttk.Label(subFrame, text=comando).grid(row=0, column=1)
            ttk.Label(subFrame, text=mensaje)#.grid(row=0, column=2)

            # Configuración de las columnas del subFrame
            columnas = subFrame.grid_size()[0]
            for columna in range(columnas):
                subFrame.grid_columnconfigure(columna, weight=1)

            # Empaquetar el subFrame
            subFrame.pack(fill="x", padx=5, pady=5)

        # Mantener el scroll y actualizar cada segundo
        frame.after(1000, self.actualizarEventsFrame, frame, completado)
        #TODO Implementar frame para mostrar los eventos en un widget ttk.Label (opcional: widget animado)
        #TODO Mejorar el diseño y la logica al mostrar los eventos

    def Iniciar(self):
        self.mainloop()

def lista_archivos_directorios(directorio_buscar:str):
    contenido_directorio = os.listdir(directorio_buscar)
    lista_archivos = []
    lista_directorios = []
    for elemento in contenido_directorio:
        if os.path.isfile(f"{directorio_buscar}/{elemento}"):
            lista_archivos.append(elemento)
        else:
            lista_directorios.append(elemento)
    return lista_archivos, lista_directorios

def ActualizarScrolledText(textArea:ScrolledText, ventana:tk.Tk, completado:tk.BooleanVar):
    if not completado.get():
        textArea.delete(1.0, tk.END)
        try:
            for evento in getEvents():
                textArea.insert(tk.END, "_"*25)
                textArea.insert(tk.END, f"""
\nCMD: {evento["Comando"]}
SALIDA: {str(evento["Salida"]).strip() if evento["Salida"] else str(evento["Error"]).strip()}
CODIGO: {evento["CodigoRetorno"]}
FUNCION: {evento["Funcion"]}\n""")
                textArea.insert(tk.END, "_"*25)
                textArea.see(tk.END)
        except Exception as e:
            print("Error al actualizar el texto:", e)
        
        ventana.after(1000, ActualizarScrolledText, textArea, ventana, completado)
    else:
        textArea.delete(1.0, tk.END)
        textArea.insert(tk.END, "Tareas finalizadas")
        textArea.see(tk.END)
        return

def dividir_lista(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

if __name__ == "__main__":
    app = NodeSetupApp()
    app.mostrar_imagenes()
    app._centrar_ventana()
    app.Iniciar()