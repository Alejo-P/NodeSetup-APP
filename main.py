import json
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from plyer import notification
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.constants import * # type: ignore
from tkinter import messagebox
import queue, os, shutil, threading, subprocess
import time, ast, tempfile
from typing import Any, Literal
from Actions import (
    ValidateOnlyPath,
    addGitRemote,
    centerWindow,
    clearQueue,
    doNothing,
    getBranchCommitsLog,
    getCurrentBrach,
    getFileExtension,
    getGitEmail,
    getGitRemotes,
    getGitUser,
    getModifiedFilesGit,
    isFileInPath,
    isFolderInPath,
    isValidURL,
    preventCloseWindow,
    getVersionOf,
    printLog,
    removeGitRemote,
    writeLog,
    getPathOf,
    runCommand,
    loadImageTk,
    getGitBranches,
    getDetailedModules
)
from CustomWidgets import MultiChoice, ScrolledFrame, SelectionLabel
from Tools import ToolTip
from Vars import (
    listaArgumentos,
    carpetas, archivos,
    archivos_p,
    Registro_hilos,
    respuestas,
    registro_commits,
    ruta_assets,
    GitRemotes_args
)
from serverWindow import ServerWindow
from version import __version__ as appVersion

class NodeSetupApp(ttk.Window):
    def __init__(self):
        def ajustar_scroll(event):
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self._version = getVersionOf("node")
        self._versionGit = getVersionOf("git")
        self._veri_code = getPathOf("code")
        self._npm_path = getPathOf("npm")
        self._git_path = getPathOf("git")
        self._referencias = {}
        self._lista_widgets= []
        self._version_NPM = None
        self._ruta_temporal = tempfile.mkdtemp()
        self._accionesRealizar = []
        
        if self._version is None:
            messagebox.showerror("Error", "Node.js no está instalado en el sistema")
            quit()
        
        super().__init__(themename="superhero")
        
        self.title("NodeSetup")
        self.resizable(0, 0)  # type: ignore
        self.protocol("WM_DELETE_WINDOW", lambda: preventCloseWindow("Accion no permitida", "No puede cerrar esta ventana, hay tareas que requieren usarla", "WARNING"))
        
        
        self._checkVars = []
        self._imagenes = {}
        self._task_widgets = {}
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
        self.canvas = tk.Canvas(self.frm_estadoEv)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.frm_estadoEv, orient=tk.VERTICAL, command=self.canvas.yview, bootstyle="danger-round") #type: ignore
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.contenido_frame = ttk.Frame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.contenido_frame, anchor=tk.NW)
        
        self.contenido_frame.bind("<Configure>", ajustar_scroll)
        
        self.repoURL = tk.StringVar()
        
        self._almacenar_imagenes()
        self.crear_widgets()
        self._menuContextual(None)
    
    def _almacenar_imagenes(self):
        self._imagenes["Git"] = loadImageTk(os.path.join(ruta_assets, "gitIcon.png"), 25, 25)
        self._imagenes["Check"] = loadImageTk(os.path.join(ruta_assets, "checkIcon.png"), 25, 25)
        self._imagenes["Error"] = loadImageTk(os.path.join(ruta_assets, "errorIcon.png"), 25, 25)
        self._imagenes["Pending"] = loadImageTk(os.path.join(ruta_assets, "timerIcon.png"), 25, 25)
        self._imagenes["Running"] = loadImageTk(os.path.join(ruta_assets, "dotAndCircleIcon.png"), 25, 25)
    
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
            
        self._menu = ttk.Menu(self, tearoff=0)
        
        submenu_Herramientas = ttk.Menu(self._menu, tearoff=0)
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
                ecommit.config(foreground="white")
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
            self._accionesRealizar.clear()
            self._task_widgets.clear()
            if self._crearRuta.get():
                tarea = {
                    "accion": "Crear ruta",
                    "estado": "Pendiente",
                    "info": None
                }
                self._accionesRealizar.append(tarea.copy())
                total_pasos += 1
            
            if self._eliminarContenido.get():
                tarea = {
                    "accion": "Eliminar contenido de la carpeta",
                    "estado": "Pendiente",
                    "info": None
                }
                self._accionesRealizar.append(tarea.copy())
                total_pasos += 1
            
            tarea = {
                "accion": "Inicializar proyecto Node",
                "estado": "Pendiente",
                "info": None
            }
            self._accionesRealizar.append(tarea.copy())
            
            for dic in self._modulosNPM:
                if dic["usar"] is not None and dic["usar"].get():
                    tarea = {
                        "accion": f"Instalar modulo {dic['nombre']} - {dic['version'].get()}",
                        "estado": "Pendiente",
                        "info": dic
                    }
                    self._accionesRealizar.append(tarea.copy())
                    total_pasos += 1
            
            for dic in self._checkVars:
                dic = dict(dic)
                for clave, var in dic.items():
                    if var.get() and clave == "Crear archivos\nadicionales":
                        tarea = {
                            "accion": "Crear archivos adicionales",
                            "estado": "Pendiente",
                            "info": None
                        }
                        self._accionesRealizar.append(tarea.copy())
                        total_pasos += 1
                    elif var.get() and clave == "Abrir en VS Code\nal finalizar":
                        tareas = {
                            "accion": "Abrir en VS Code",
                            "estado": "Pendiente",
                            "info": None
                        }
                        self._accionesRealizar.append(tareas.copy())
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
        
        def Iniciar_npm():
            try:
                actualizar_progreso("Inicializando proyecto Node")
                # Ejecutar `npm init -y` para inicializar el proyecto
                estado = runCommand([self._npm_path, "init", "-y"], self.entry_ruta.get())
                
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
        
        if len(self.entry_ruta.get()) == 0:
            messagebox.showwarning("Advertencia", "Debe seleccionar una ruta")
            return
        
        self.lock_unlock_widgets(estado="disabled")
        self.completado.set(False)
        total_pasos = conteo_tareas()
        pasos_completados = 0
        
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.progreso['value'] = 0
        self.frm_estadoEv.grid(row=1, rowspan=11, column=4, columnspan=2, padx=5, sticky="nsew")
        self._centrar_ventana(restablecer_tamaño=True)
        
        for tarea in self._accionesRealizar:
            if tarea["accion"] == "Crear ruta":
                try:
                    tarea["estado"] = "En progreso"
                    self.actualizarEventsFrame()
                    actualizar_progreso("Creando ruta")
                    self._crear_ruta()
                    tarea["estado"] = "Completado"
                    self.actualizarEventsFrame()
                except NotADirectoryError as de:
                    actualizar_progreso("Error en la ruta", fill=True)
                    self.lock_unlock_widgets(estado="normal")
                    tarea["estado"] = "Error"
                    self.actualizarEventsFrame()
                    messagebox.showerror("Ruta invalida", f"Error en la ruta: {de}")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Error al crear la ruta: {e}")
                    self.lock_unlock_widgets(estado="normal")
                    actualizar_progreso("Error al crear la ruta", fill=True)
                    tarea["estado"] = "Error"
                    self.actualizarEventsFrame()
                    return
            
            if tarea["accion"] == "Eliminar contenido de la carpeta":
                if messagebox.askyesno("Advertencia", f"Se eliminara todo el contenido de la carteta actual\n {self.entry_ruta.get()},\n ¿Desea contunuar?"):
                    try:
                        tarea["estado"] = "En progreso"
                        self.actualizarEventsFrame()
                        actualizar_progreso("Eliminando contenido de la carpeta")
                        self._borrar_contenido_ruta()
                        tarea["estado"] = "Completado"
                        self.actualizarEventsFrame()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al eliminar contenido de la carpeta: {e}")
                        self.lock_unlock_widgets(estado="normal")
                        actualizar_progreso("Error al eliminar contenido de la carpeta", fill=True)
                        tarea["estado"] = "Error"
                        self.actualizarEventsFrame()
                        return
                else:
                    self.lock_unlock_widgets(estado="normal")
                    actualizar_progreso("Operacion cancelada", fill=True)
                    tarea["estado"] = "Error"
                    self.actualizarEventsFrame()
                    return
            
            if tarea["accion"] == "Inicializar proyecto Node":
                tarea["estado"] = "En progreso"
                self.actualizarEventsFrame()
                
                if Iniciar_npm() != 0:
                    tarea["estado"] = "Error"
                    self.actualizarEventsFrame()
                    return
                
                tarea["estado"] = "Completado"
                self.actualizarEventsFrame()
            
            if tarea["accion"].startswith("Instalar modulo"):
                modulo = tarea["info"]
                if modulo["usar"] is not None and modulo["usar"].get():
                    actualizar_progreso(f"Instalando {modulo['nombre']}-{modulo['version'].get()} {'globalmente' if modulo['global'].get() else ''}")
                    tarea["estado"] = "En progreso"
                    self.actualizarEventsFrame()
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
                    if isinstance(estado, subprocess.CalledProcessError):
                        messagebox.showerror("Error", f"Error instalando {modulo['nombre']}: {estado}")
                        tarea["estado"] = "Error"
                        self.actualizarEventsFrame()
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
                    else:
                        tarea["estado"] = "Completado"
                        self.actualizarEventsFrame()
            
            if tarea["accion"] == "Crear archivos adicionales":
                tarea["estado"] = "En progreso"
                self.actualizarEventsFrame()
                actualizar_progreso("Creando archivos adicionales")
                self._crear_recursos_necesarios()
                tarea["estado"] = "Completado"
                self.actualizarEventsFrame()
            
            for archivo in archivos_p:
                with open(f"{self.entry_ruta.get()}/{archivo}", "w") as file:
                    if archivo == ".gitignore":
                        file.write("node_modules\n")
                        file.write(".env")
            
            if tarea["accion"] == "Abrir en VS Code":
                tarea["estado"] = "En progreso"
                self.actualizarEventsFrame()
                actualizar_progreso("Abriendo en VS Code")
                try:
                    resultado = runCommand([self._veri_code, "."], self.entry_ruta.get())
                    if isinstance(resultado, subprocess.CalledProcessError):
                        tarea["estado"] = "Error"
                        self.actualizarEventsFrame()
                        actualizar_progreso("Error al abrir en VS Code", fill=True)
                        self.lock_unlock_widgets(estado="normal")
                        messagebox.showerror("Error", f"Error al abrir en VS Code: {resultado}")
                        return
                    else:
                        tarea["estado"] = "Completado"
                        self.actualizarEventsFrame()
                except Exception as e:
                    tarea["estado"] = "Error"
                    self.actualizarEventsFrame()
                    actualizar_progreso("Error al abrir en VS Code", fill=True)
                    self.lock_unlock_widgets(estado="normal")
                    messagebox.showerror("Error", f"Error al abrir en VS Code: {e}")
                    return
                            
        if pasos_completados == total_pasos:
            self.lock_unlock_widgets(estado="normal")
            actualizar_progreso("Completado", True)
            messagebox.showinfo("Informacion", "Proyecto creado con éxito")
            time.sleep(4.5)
            if self.winfo_exists():
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
    
    def actualizarEventsFrame(self):
        for i, tarea in enumerate(self._accionesRealizar, 1):
            if tarea["estado"] == "Pendiente":
                style = WARNING
                icon = self._imagenes["Pending"]
            elif tarea["estado"] == "En progreso":
                style = INFO
                icon = self._imagenes["Running"]
            elif tarea["estado"] == "Completado":
                style = SUCCESS
                icon = self._imagenes["Check"]
            else:
                style = DANGER
                icon = self._imagenes["Error"]
            
            if i not in self._task_widgets:
                subFrame = ttk.LabelFrame(self.contenido_frame, text=f"Tarea {i} de {len(self._accionesRealizar)}", bootstyle=style) # type: ignore
                ttk.Label(subFrame, image=icon).grid(row=0, column=0, sticky="nsew", padx=3)
                ttk.Label(subFrame, text=tarea["accion"]).grid(row=0, column=1, sticky="nsew", padx=9)
                ttk.Label(subFrame, text=tarea["estado"]).grid(row=0, column=2, sticky="nsew", padx=3)
                
                columnas = subFrame.grid_size()[0]
                for columna in range(columnas):
                    subFrame.grid_columnconfigure(columna, weight=1)

                subFrame.grid(row=i-1, column=0, sticky="nsew", padx=5, pady=5)
                self._task_widgets[i] = subFrame
            else:
                subFrame = self._task_widgets[i]
                subFrame.config(text=f"Tarea {i} de {len(self._accionesRealizar)}", bootstyle=style)  # type: ignore
                subFrame.grid_slaves(row=0, column=0)[0].config(image=icon)
                subFrame.grid_slaves(row=0, column=1)[0].config(text=tarea["accion"])
                subFrame.grid_slaves(row=0, column=2)[0].config(text=tarea["estado"])

        columnas = self.contenido_frame.grid_size()[0]
        for columna in range(columnas):
            self.contenido_frame.grid_columnconfigure(columna, weight=1)
        
        # Eliminar los frames que no se han actualizado
        for key in list(self._task_widgets.keys()):
            if key not in range(1, len(self._accionesRealizar)+1):
                frame = self._task_widgets.pop(key)
                frame.destroy()
        # Opción: Si alguna tarea se elimina o no está presente en `self._accionesRealizar`, se puede eliminar de `_task_widgets` si es necesario

    def Iniciar(self):
        self.mainloop()

class NodeSetupAppNew(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        
        def onFrameClick(event:tk.Event):
            if str(event.widget["state"]) == "disabled":
                return
            
            for widget in self.frameSeleccion.winfo_children():
                if str(widget.cget("state")) == "disabled":
                    continue
                
                if isinstance(widget, SelectionLabel):
                    if widget.type == "warning":
                        widget.config( # type: ignore
                            style="Warning.TLabel",
                            cursor="hand2",
                        )
                        widget.onClick(callback=onFrameClick)
                        continue
                    
                    widget.type = "normal"
                    widget.config( # type: ignore
                        style="Custom.TLabel",
                        cursor="hand2",
                    )
                    widget.onClick(callback=onFrameClick)
            
            event.widget.config(style="Selected.TLabel", cursor="arrow")
            event.widget.deleteBind("<Button-1>")
            event.widget.type = "selected"
            showSelectedFrame(event.widget.cget("text"))
        
        def onUpdateFrames():
            for frame in self.frameSeleccion.winfo_children():
                #TODO: Manejar la actualizacion de frames con el SelectedLabel
                if str(frame.cget("state")) == "disabled":
                    frame.config( # type: ignore
                        style="Disabled.TLabel",
                        cursor="arrow"
                    )
                    frame.unbind("<Button-1>")
                    continue
                
                if isinstance(frame, SelectionLabel):
                    if frame.type == "warning":
                        frame.config( # type: ignore
                            style="Warning.TLabel",
                            cursor="hand2",
                        )
                        frame.onClick(callback=onFrameClick)
                        continue
                    
                    if frame.type == "selected":
                        frame.config( # type: ignore
                            style="Selected.TLabel",
                            cursor="arrow"
                        )
                        frame.unbind("<Button-1>")
                        continue
                        
                    frame.type = "normal"
                    frame.config( # type: ignore
                        style="Custom.TLabel",
                        cursor="hand2",
                    )
                    frame.onClick(callback=onFrameClick)
                
                # if str(frame.cget("style")) == "Selected.TLabel":
                #     frame.config( # type: ignore
                #         style="Selected.TLabel",
                #         cursor="arrow"
                #     )
                #     frame.unbind("<Button-1>")
                #     continue
                
                # frame.config( # type: ignore
                #     style="Custom.TLabel",
                #     cursor="hand2"
                # )
                # frame.bind("<Button-1>", onFrameClick)
            
            setToolTipText()
        
        def showSelectedFrame(frameName:str):
            for frame in self.winfo_children():
                if frame.winfo_class() == "TFrame" and frame.winfo_name() != "selector":
                    frame.pack_forget()
            
            if frameName == "Principal":
                self.framePrincipal.pack(side="right", fill="both", expand=True)
            elif frameName == "Modulos":
                self.frameModulos.pack(side="right", fill="both", expand=True)
            elif frameName == "Git":
                self.frameGit.pack(side="right", fill="both", expand=True)
            elif frameName == "Tareas":
                self.frameTareas.pack(side="right", fill="both", expand=True)
            elif frameName == "Configuracion":
                self.frameConfiguracion.pack(side="right", fill="both", expand=True)
        
        def goToFrame(frameName:str):
            for frame in self.frameSeleccion.winfo_children():
                if frame.cget("text") == frameName:
                    frame.event_generate("<Button-1>")
                    break
            else:
                messagebox.showerror("Error", f"El frame {frameName} no existe")
        
        def setToolTipText():
            textoTipPrincipal = self.toolTipPrincipal.getText().split("\n")
            textoTipModulos = self.toolTipModulos.getText().split("\n")
            textoTipGit = self.toolTipGit.getText().split("\n")
            textoTipTareas = self.toolTipTareas.getText().split("\n")
            textoTipConfiguracion = self.toolTipConfiguracion.getText().split("\n")
            
            textoTipPrincipal[0] = "Configurar el entorno Node"
            if self.Principal.cget("style") == "Disabled.TLabel":
                if "(No se puede acceder a este frame)" not in textoTipPrincipal:
                    textoTipPrincipal.insert(1, "(No se puede acceder a este frame)")
            else:
                if "(No se puede acceder a este frame)" in textoTipPrincipal:
                    textoTipPrincipal.remove("(No se puede acceder a este frame)")
            self.toolTipPrincipal.setText("\n".join(textoTipPrincipal))
            
            
            mensajeFrameModulos = "Seleccionar los módulos a instalar"
            if self.Modulos.cget("style") == "Disabled.TLabel":
                mensajeFrameModulos += "\n(No se puede acceder a este frame)" 
            self.toolTipModulos.setText(mensajeFrameModulos)
            
            mensajeFrameGit = "Configurar Git en el proyecto"
            if self.Git.cget("style") == "Disabled.TLabel":
                mensajeFrameGit += "\n(No se puede acceder a este frame)"
            self.toolTipGit.setText(mensajeFrameGit)
            
            mensajeTareas = "Ver las tareas realizadas"
            if self.Tareas.cget("style") == "Disabled.TLabel":
                mensajeTareas += "\n(No se puede acceder a este frame)"
            self.toolTipTareas.setText(mensajeTareas)
            
            self.toolTipConfiguracion.setText("Configurar la aplicación")
        
        self.title(f"Node Setup App")
        self.geometry("800x600")
        self.resizable(False, False)
        
        self._imagenes = {}
        self._tareas = []
        self._taskWidgets = []
        self._version = appVersion
        
        self._funcGoToFrame = goToFrame
        self._funcOnUpdateFrames = onUpdateFrames
        
        self._node_path = getPathOf("node")
        self._npm_path = getPathOf("npm")
        self._git_path = getPathOf("git")
        self._code_path = getPathOf("code")
        
        self._versionGit = getVersionOf(self._git_path) if self._git_path else None
        self._versionNPM = getVersionOf(self._npm_path) if self._npm_path else None
        self._versionNode = getVersionOf(self._node_path) if self._node_path else None
        
        estilos = ttk.Style()
        estilos.configure("Custom.TFrame", background="#3E556A")
        estilos.configure("Response.TLabel", background="#526170")
        estilos.configure("Custom.TLabel", background="#3E556A", foreground="white")
        estilos.configure("Disabled.TLabel", background="#3E556A", foreground="gray")
        estilos.configure("Selected.TLabel", background="#2B3E50", foreground="white")
        estilos.configure("Warning.TLabel", background="#FFC107", foreground="black")
        estilos.configure("Error.TLabel", background="#DC3545", foreground="white")
        
        self.frameSeleccion = ttk.Frame(self, name="selector", style="Custom.TFrame")
        
        self.Principal = SelectionLabel(self.frameSeleccion, text="Principal", style="Custom.TLabel")
        self.Modulos = SelectionLabel(self.frameSeleccion, text="Modulos", style="Disabled.TLabel", state="disabled")
        self.Git = SelectionLabel(self.frameSeleccion, text="Git", style="Custom.TLabel" if self._versionGit else "Disabled.TLabel", state="normal" if self._versionGit else "disabled")
        self.Tareas = SelectionLabel(self.frameSeleccion, text="Tareas", style="Disabled.TLabel", state="disabled")
        self.Configuracion = SelectionLabel(self.frameSeleccion, text="Configuracion", style="Custom.TLabel")
        
        self.toolTipPrincipal = ToolTip(self.Principal)
        self.toolTipModulos = ToolTip(self.Modulos)
        self.toolTipGit = ToolTip(self.Git)
        self.toolTipTareas = ToolTip(self.Tareas)
        self.toolTipConfiguracion = ToolTip(self.Configuracion)
        
        self.Principal.pack(fill="both", expand=True)
        self.Modulos.pack(fill="both", expand=True)
        self.Git.pack(fill="both", expand=True)
        self.Tareas.pack(fill="both", expand=True)
        self.Configuracion.pack(fill="both", expand=True)
        
        self.Principal.bind("<Enter>", lambda e: self.toolTipPrincipal.showtip("e"))
        self.Principal.bind("<Leave>", lambda e: self.toolTipPrincipal.hidetip())
        
        self.Modulos.bind("<Enter>", lambda e: self.toolTipModulos.showtip("e"))
        self.Modulos.bind("<Leave>", lambda e: self.toolTipModulos.hidetip())
        
        self.Git.bind("<Enter>", lambda e: self.toolTipGit.showtip("e"))
        self.Git.bind("<Leave>", lambda e: self.toolTipGit.hidetip())
        
        self.Tareas.bind("<Enter>", lambda e: self.toolTipTareas.showtip("e"))
        self.Tareas.bind("<Leave>", lambda e: self.toolTipTareas.hidetip())
        
        self.Configuracion.bind("<Enter>", lambda e: self.toolTipConfiguracion.showtip("e"))
        self.Configuracion.bind("<Leave>", lambda e: self.toolTipConfiguracion.hidetip())
        
        self.frameSeleccion.pack(fill="y", side="left", ipadx=5)
        
        self.framePrincipal = ttk.Frame(self)
        self.frameModulos = ttk.Frame(self)
        self.frameGit = ttk.Frame(self)
        self.frameTareas = ttk.Frame(self)
        self.frameConfiguracion = ttk.Frame(self)
        
        self._toast = None
        
        self._loadImages()
        
        self._configuracionFrame()
        self._principalFrame()
        self._modulosFrame()
        if self._git_path:
            self._gitFrame()
        self._tareasFrame()
        
        onUpdateFrames()
        goToFrame("Principal")
        
    def _sendNotification(self, title:str, message:str, duration:int=3000, **kwargs):
        iconName = kwargs.pop("icon", "principal")
        
        notification.notify( # type: ignore
            title=title,
            message=message,
            app_name="Node Setup App",
            app_icon="",
            timeout=duration,
            **kwargs
        )
    
    def _principalFrame(self):
        def abrir_ruta():
            if ruta:=filedialog.askdirectory():
                self._ruta.set(ruta)
                onUpdateEntryRuta(None)
                    
        def onUpdateEntryRuta(event):
            textoTooltip = self.toolTipPrincipal.getText()
            mensajes = 0
            
            if not self._ruta.get():
                btn_irModulos.config(state="disabled")
                btn_proceder.config(state="disabled")
                self.Modulos.config(state="disabled")
                self._funcOnUpdateFrames()
                
                mensajes += 1
                if self.Principal.type != "selected":
                    self.Principal.type = "warning"
                    self.Principal.config(style="Warning.TLabel")
                
                if "-> Debe seleccionar una ruta" not in textoTooltip:
                    self.toolTipPrincipal.setText(f"{textoTooltip}\n-> Debe seleccionar una ruta")
            else:
                if "-> Debe seleccionar una ruta" in textoTooltip:
                    textoTooltip = textoTooltip.replace("-> Debe seleccionar una ruta", "").strip()
                    self.toolTipPrincipal.setText(textoTooltip)
            
            if not os.path.exists(self._ruta.get()) and not self.CrearRutaVar.get():
                btn_irModulos.config(state="disabled")
                btn_proceder.config(state="disabled")
                self.Modulos.config(state="disabled")
                self._funcOnUpdateFrames()
                
                mensajes += 1
                if self.Principal.type != "selected":
                    self.Principal.type = "warning"
                    self.Principal.config(style="Warning.TLabel")
                
                if "-> La ruta no existe" not in textoTooltip:
                    self.toolTipPrincipal.setText(f"{textoTooltip}\n-> La ruta no existe")
            else:
                if "-> La ruta no existe" in textoTooltip:
                    textoTooltip = textoTooltip.replace("-> La ruta no existe", "").strip()
                    self.toolTipPrincipal.setText(textoTooltip)
            
            if os.path.isfile(self._ruta.get()) or getFileExtension(self._ruta.get()):
                btn_irModulos.config(state="disabled")
                btn_proceder.config(state="disabled")
                self.Modulos.config(state="disabled")
                self._funcOnUpdateFrames()
                
                mensajes += 1
                if self.Principal.type != "selected":
                    self.Principal.type = "warning"
                    self.Principal.config(style="Warning.TLabel")
                
                if "-> La ruta no es un directorio" not in textoTooltip:
                    self.toolTipPrincipal.setText(f"{textoTooltip}\n-> La ruta no es un directorio")
            else:
                if "-> La ruta no es un directorio" in textoTooltip:
                    textoTooltip = textoTooltip.replace("-> La ruta no es un directorio", "").strip()
                    self.toolTipPrincipal.setText(textoTooltip)
            
            if not self._npm_path or not self._node_path:
                btn_irModulos.config(state="disabled")
                btn_proceder.config(state="disabled")
                self.Modulos.config(state="disabled")
                self._funcOnUpdateFrames()
                
                mensajes += 1
                if self.Principal.type != "selected":
                    self.Principal.type = "warning"
                    self.Principal.config(style="Warning.TLabel")
                
                if "-> Node o NPM no encontrados" not in textoTooltip:
                    self.toolTipPrincipal.setText(f"{textoTooltip}\n-> Node o NPM no encontrados")
            else:
                if "-> Node o NPM no encontrados" in textoTooltip:
                    textoTooltip = textoTooltip.replace("-> Node o NPM no encontrados", "").strip()
                    self.toolTipPrincipal.setText(textoTooltip)
            
            if mensajes == 0:
                self.Principal.type = "normal"
                self.Principal.config(style="Custom.TLabel")
                self.Modulos.config(state="normal")
                btn_proceder.config(state="normal")
                btn_irModulos.config(state="normal")
                self._funcOnUpdateFrames()
        
        def disableInfoEntries():
            for widget in frameInformacion.winfo_children():
                if widget.winfo_class() == "TEntry":
                    widget.config(state="readonly") # type: ignore
        
        def crearProyecto():
            if self._funcConteoTareas() == 0:
                messagebox.showerror("Error", "No se ha seleccionado ningun modulo")
                return

            self.Tareas.config(state="normal")
            self._funcOnUpdateFrames()
            self._funcGoToFrame("Tareas")
            self._funcInicioTareas()
        
        def iniciarPrecargaModulos():
            self._funcGoToFrame("Modulos")
            self._funcIniciarCargaModulos()
        
        #StringVars
        self._ruta = tk.StringVar()
        
        frameInformacion = ttk.LabelFrame(self.framePrincipal, text="Informacion")
        ttk.Label(frameInformacion, text="Version de la app:", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        entryAppV = ttk.Entry(frameInformacion)
        entryAppV.insert(0, appVersion)
        entryAppV.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        
        ttk.Label(frameInformacion, text="Version de Node:", anchor="center").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        entryNodeV = ttk.Entry(frameInformacion)
        entryNodeV.insert(0, self._versionNode if self._versionNode else "No disponible")
        entryNodeV.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        
        ttk.Label(frameInformacion, text="Version de NPM:", anchor="center").grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        entryNPMV = ttk.Entry(frameInformacion)
        entryNPMV.insert(0, self._versionNPM if self._versionNPM else "No disponible")
        entryNPMV.grid(row=1, column=2, pady=5, padx=5, sticky="ew")
        
        columnas, filas = frameInformacion.grid_size()
        for columna in range(columnas):
            frameInformacion.grid_columnconfigure(columna, weight=1)
            
        for fila in range(filas):
            frameInformacion.grid_rowconfigure(fila, weight=1)
        
        frameInformacion.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.framePrincipal.after(100, disableInfoEntries)
        
        ttk.Label(self.framePrincipal, text="Directorio del proyecto").grid(row=1, column=0, columnspan=2, padx=5)
        scrollEntry = ttk.Scrollbar(self.framePrincipal, orient="horizontal", bootstyle="info-round") # type: ignore
        entryRuta = ttk.Entry(self.framePrincipal, textvariable=self._ruta, width=50)
        scrollEntry.config(command=entryRuta.xview)
        entryRuta.config(xscrollcommand=scrollEntry.set)
        
        entryRuta.grid(row=2, column=0, padx=5, sticky="ew")
        scrollEntry.grid(row=3, column=0, padx=5, sticky="ew")
        entryRuta.bind("<Return>", onUpdateEntryRuta)
        entryRuta.bind("<FocusOut>", onUpdateEntryRuta)
        
        ttk.Button(self.framePrincipal, text="Seleccionar", command=abrir_ruta, bootstyle=(WARNING, OUTLINE)).grid(row=2, rowspan=2, column=1, padx=5, sticky="nsew", pady=7) # type: ignore
        
        self.EliminarContenidoVar = tk.BooleanVar()
        self.CrearRutaVar = tk.BooleanVar()
        self.CrearRutaVar.trace_add("write", lambda *args: onUpdateEntryRuta(None))
        self.EliminarEnFalloVar = tk.BooleanVar()
        self.PararEnFalloVar = tk.BooleanVar()
        
        ttk.Checkbutton(self.framePrincipal, text="Eliminar contenido de la carpeta", variable=self.EliminarContenidoVar, bootstyle="warning-round-toggle").grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) # type: ignore
        ttk.Checkbutton(self.framePrincipal, text="Crear ruta", variable=self.CrearRutaVar, bootstyle="warning-round-toggle").grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) # type: ignore
        ttk.Checkbutton(self.framePrincipal, text="Eliminar en caso de fallo", variable=self.EliminarEnFalloVar, bootstyle="warning-round-toggle").grid(row=6, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) # type: ignore
        ttk.Checkbutton(self.framePrincipal, text="Parar en caso de fallo", variable=self.PararEnFalloVar, bootstyle="warning-round-toggle").grid(row=7, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) # type: ignore
        
        frameBotones = ttk.Frame(self.framePrincipal)
        btn_irModulos = ttk.Button(frameBotones, text="Seleccion de modulos", command=iniciarPrecargaModulos, bootstyle=(INFO, OUTLINE)) # type: ignore
        btn_irModulos.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        btn_proceder = ttk.Button(frameBotones, text="Crear el proyecto", command=crearProyecto, bootstyle=(SUCCESS, OUTLINE)) # type: ignore
        btn_proceder.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        btn_salir = ttk.Button(frameBotones, text="Salir", command=self.destroy, bootstyle=(DANGER, OUTLINE)) # type: ignore
        btn_salir.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        columnas, filas = frameBotones.grid_size()
        for columna in range(columnas):
            frameBotones.grid_columnconfigure(columna, weight=1)
        
        for fila in range(filas):
            frameBotones.grid_rowconfigure(fila, weight=1)
        frameBotones.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        onUpdateEntryRuta(None)
        
        columnas = self.framePrincipal.grid_size()[0]
        for columna in range(columnas):
            self.framePrincipal.grid_columnconfigure(columna, weight=1)

    def _modulosFrame(self):
        def onClickPrompt(infoModulo:dict):
            def onClosePopUp():
                for widget in popUp_prompt.winfo_children():
                    widget.destroy()
                
                popUp_prompt.destroy()
            
            def onCopy():
                self.clipboard_clear()
                self.clipboard_append(entryComando.get())
                self.update()
            
            if not infoModulo["usar"].get():
                messagebox.showwarning("Advertencia", "Debe seleccionar el modulo para poder mostrar el comando a ejecutar")
                return
            
            comando = [
                self._npm_path,
                "i"
            ]
            
            if infoModulo["argumento"].get():
                #Ejemplo del valor de argumento.get() -> "-S, -D, -O, --no-save, --production, --only=dev, --only=prod"
                argumentos = " ".join(infoModulo["argumento"].get().split(", "))
                comando.append(argumentos)
            
            comando.append(f"{infoModulo['nombre'].lower()}@{infoModulo['version'].get()}")
            
            popUp_prompt = ttk.Toplevel()
            popUp_prompt.title("Prompt")
            popUp_prompt.resizable(False, False)
            popUp_prompt.protocol("WM_DELETE_WINDOW", onClosePopUp)
            popUp_prompt.transient(self)
            popUp_prompt.grab_set()
            
            ttk.Label(popUp_prompt, text="Comando a ejecutar:").grid(row=0, column=0, padx=5, pady=5)
            entryComando = ttk.Entry(popUp_prompt, width=70)
            entryComando.insert(0, " ".join(comando))
            entryComando.config(state="readonly")
            entryComando.grid(row=1, column=0, padx=5)
            
            scrollEntry = ttk.Scrollbar(popUp_prompt, orient="horizontal", bootstyle="info-round") # type: ignore
            entryComando.config(xscrollcommand=scrollEntry.set)
            scrollEntry.config(command=entryComando.xview)
            scrollEntry.grid(row=2, column=0, padx=5, sticky="ew")
            
            frame_botones = ttk.Frame(popUp_prompt)
            ttk.Button(frame_botones, text="Copiar", command=onCopy, bootstyle=(SUCCESS, OUTLINE)).grid(row=0, column=0, padx=5, pady=5, sticky="nsew") # type: ignore
            ttk.Button(frame_botones, text="Cerrar", command=onClosePopUp, bootstyle=(DANGER, OUTLINE)).grid(row=0, column=1, padx=5, pady=5, sticky="nsew") # type: ignore
            
            columnas = frame_botones.grid_size()[0]
            for columna in range(columnas):
                frame_botones.grid_columnconfigure(columna, weight=1)
            
            frame_botones.grid(row=3, column=0, padx=5, pady=5)
            
            popUp_prompt.grid_columnconfigure(0, weight=1)
            centerWindow(popUp_prompt)
        
        def RestablecerSeleccion():
            for dic in self._modulosNPM:
                dic["usar"].set(False)
                dic["argumento"].set("")
                dic["version"].set(dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")
        
        def CargarInfoModulos(listaModulos):
            for dic in listaModulos:
                if not dic["versiones"]:
                    versionesPaquetes = runCommand([self._npm_path, "show", dic["nombre"].lower(), "versions", "--depth=0"])
                    if isinstance(versionesPaquetes, subprocess.CalledProcessError):
                        writeLog("ERROR", f"Error al obtener versiones de {dic['nombre']}: {versionesPaquetes}", CargarInfoModulos.__name__)
                        continue
                    dic["versiones"] = list(ast.literal_eval(f"{versionesPaquetes.stdout.strip()}"))

                if not dic["usar"]:
                    dic["usar"] = tk.BooleanVar(value=False)
                if not dic["argumento"]:
                    dic["argumento"] = tk.StringVar(value="")
                if not dic["version"]:
                    dic["version"] = tk.StringVar(value=dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")
        
        def CrearWidgets(listaModulos):
            if not listaWidgets:
                for dic in listaModulos:
                    check_usar = ttk.Checkbutton(scrolledModulos, variable=dic["usar"], bootstyle="success-round-toggle", padding=4) # type: ignore
                    label_nombre = ttk.Label(scrolledModulos, text=dic["nombre"], bootstyle=LIGHT, padding=4) # type: ignore
                    multiChoice_argumento = MultiChoice(scrolledModulos, listaArgumentos, dic["argumento"],  border=1, relief="solid") # type: ignore
                    combo_version = ttk.Combobox(scrolledModulos, values=dic["versiones"], textvariable=dic["version"], state="readonly", bootstyle=SECONDARY, width=25) # type: ignore
                    label_prompt = ttk.Label(scrolledModulos, image=self._imagenes["Info"], anchor="center")
                    label_prompt.bind("<Button-1>", lambda e, dic=dic: onClickPrompt(dic))

                    listaWidgets.append([check_usar, label_nombre, multiChoice_argumento, combo_version, label_prompt])
        
        def mostrar_widgets():
            try:
                for i, widget_list in enumerate(listaWidgets, 2):
                    for j, widget in enumerate(widget_list):
                        if isinstance(widget, (ttk.Checkbutton, ttk.Combobox, MultiChoice)):
                            widget.grid(row=i, column=j % len(encabezado), padx=5, pady=2)
                        elif isinstance(widget, ttk.Label):   
                            widget.grid(
                                row=i, column=j % len(encabezado), 
                                padx=5, pady=2, 
                                sticky="w" if not str(widget.cget("image")) else ""
                            )

                scrolledModulos.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                frame_botones = ttk.Frame(self.frameModulos, width=100)
                frame_botones.grid(row=1, column=0, pady=5, sticky="nsew")

                frame_botones.grid_columnconfigure(0, weight=1)
                frame_botones.grid_columnconfigure(1, weight=1)

                ttk.Button(frame_botones, text="Regresar", command=lambda: self._funcGoToFrame("Principal"), style="info.TButton").grid(row=0, column=0, padx=10, sticky="nsew")
                ttk.Button(frame_botones, text="Restablecer", command=RestablecerSeleccion, style="warning.TButton").grid(row=0, column=1, padx=10, sticky="nsew")
                
                columnas, filas = scrolledModulos.grid_size()
                for columna in range(columnas):
                    scrolledModulos.grid_columnconfigure(columna, weight=1)
                
                for fila in range(filas):
                    scrolledModulos.grid_rowconfigure(fila, weight=1)
                
                self.frameModulos.grid_columnconfigure(0, weight=1)
                self.frameModulos.grid_rowconfigure(0, weight=1)
            except tk.TclError as e:
                print(f"Error al mostrar widgets: {e}")
        
        def iniciarCarga():
            nonlocal cargando
            n_listas = 6
            progress_bar.grid(row=2, column=0, columnspan=len(encabezado), padx=5, pady=10)
            progress_bar.start()
            msg_estado.config(text="Cargando módulos de NPM... No cierre la ventana!")
            btn_carga.grid_forget()

            if not listaWidgets:
                cargando = True
                self.protocol("WM_DELETE_WINDOW", lambda: doNothing())
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
                cargando = False
            
            CrearWidgets(self._modulosNPM)

            # Mostrar los widgets en la interfaz
            self.frameModulos.after(0, mostrar_widgets)  # Programar mostrar_widgets en el hilo principal

            self.protocol("WM_DELETE_WINDOW", lambda: self._cerrarVentana())
        
        def IniciarPregarga():
            if not listaWidgets and not cargando:
                threading.Thread(target=iniciarCarga).start()
        
        self._modulosNPM = getDetailedModules()
        
        scrolledModulos = ScrolledFrame(self.frameModulos, "warning-rounded")
        
        encabezado = [
            "Seleccionar",
            "Nombre",
            "Argumentos",
            "Version",
            "Ver comando"
        ]
        
        listaWidgets = []
        cargando = False
        
        for i, txt in enumerate(encabezado):
            ttk.Label(scrolledModulos, text=txt, anchor="center").grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        
        ttk.Separator(scrolledModulos, orient="horizontal", bootstyle="warning").grid(row=1, column=0, columnspan=len(encabezado), sticky="ew") # type: ignore
        
        # Añadir una barra de progreso
        progress_bar = ttk.Progressbar(self.frameModulos, orient='horizontal', mode='indeterminate', length=280, bootstyle="warning") # type: ignore
        msg_estado = ttk.Label(self.frameModulos, text="Para ver los modulos disponibles, inicie la carga!")

        msg_estado.grid(row=0, column=0, padx=5, pady=2)
        
        btn_carga = ttk.Button(
            self.frameModulos,
            text="Cargar módulos",
            command=lambda: threading.Thread(target=iniciarCarga).start(),
            bootstyle=(INFO, OUTLINE) # type: ignore
        )
        btn_carga.grid(row=1, column=0, padx=5, pady=5, sticky="nsew", ipadx=10) 
        
        columnas = self.frameModulos.grid_size()[0]
        for columna in range(columnas):
            self.frameModulos.grid_columnconfigure(columna, weight=1)
        
        self._funcIniciarCargaModulos = IniciarPregarga
        self.frameModulos.grid_rowconfigure(0, weight=1)
        
    def _gitFrame(self):
        def onClickFrame(event:tk.Event):
            if str(event.widget["state"]) == "disabled":
                return
            
            for widget in lbl_frame.winfo_children():
                if str(widget.cget("state")) == "disabled":
                    continue
                
                if isinstance(widget, SelectionLabel):
                    if widget.type == "warning":
                        widget.config( # type: ignore
                            style="Warning.TLabel",
                            cursor="arrow",
                        )
                        widget.onClick(callback=onClickFrame)
                        continue
                
                    widget.config( # type: ignore
                        style="Custom.TLabel",
                        cursor="hand2",
                    )
                    widget.onClick(callback=onClickFrame)
            
            event.widget.config(style="Selected.TLabel", cursor="arrow")
            event.widget.deleteBind("<Button-1>")
            showSelectedFrame(event.widget.cget("text"))
        
        def goToGitFrame(framename:str):
            for frame in lbl_frame.winfo_children():
                if frame.cget("text") == framename:
                    frame.event_generate("<Button-1>")
                    break
            else:
                messagebox.showerror("Error", f"El frame {framename} no existe")
        
        def showSelectedFrame(frameName:str):
            for frame in self.frameGit.winfo_children():
                if frame.winfo_class() == "TFrame" and frame.winfo_name() != "git_selector":
                    frame.grid_forget()
            
            if frameName == "Inicio":
                frameInicio.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            elif frameName == "Commit":
                frameCommit.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            elif frameName == "Logs":
                frameLogs.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        def setGitTooltipText():
            self.toolTip_GitInicio.setText("Clonar un repositorio de Git")
            self.toolTip_GitCommit.setText("Realizar commits en un repositorio de Git")
            self.toolTip_GitLogs.setText("Ver los logs de un repositorio de Git")
        
        def ChangePath():
            if ruta:=filedialog.askdirectory():
                self._ruta.set(ruta)
        
        def contentFrameInicio():
            def onClonarRepositorio():
                def verificar_clonacion():
                    try:
                        exito, mensaje = resultado_clonacion.get_nowait()
                         
                        btn_clonacion.config(state="normal", text="Clonar")
                        if not exito:
                            messagebox.showerror("Error", f"Error al clonar el repositorio: {mensaje}")
                            return
                        messagebox.showinfo("Información", mensaje)
                    except queue.Empty:
                        frameInicio.after(100, verificar_clonacion)
                
                def clonar_background():
                    resultado = runCommand([self._git_path, "clone", URLrepo.get(), self._ruta.get()])
                    if isinstance(resultado, subprocess.CalledProcessError):
                        resultado_clonacion.put((False, resultado.stderr))
                        return
                    resultado_clonacion.put((True, "El repositorio se clonó correctamente"))
                
                btn_clonacion.config(state="disabled", text="Clonando...")
                resultado_clonacion = queue.Queue()
                threading.Thread(target=clonar_background).start()
                frameInicio.after(100, verificar_clonacion)
            
            def ValidarEntries():
                textoTooltip = self.toolTip_GitInicio.getText()
                mensajes = 0

                # Validación de la URL del repositorio
                if not URLrepo.get():
                    btn_clonacion.config(state="disabled")
                    mensajes += 1
                    lblInicio.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    btnInitGit.config(state="normal")
                    lblInicio.type = "warning"
                    if "-> La URL del repositorio no puede estar vacía" not in textoTooltip:
                        self.toolTip_GitInicio.setText(f"{textoTooltip}\n-> La URL del repositorio no puede estar vacía")
                else:
                    # Si se ha corregido, eliminar la advertencia
                    if "-> La URL del repositorio no puede estar vacía" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La URL del repositorio no puede estar vacía", "").strip()
                        self.toolTip_GitInicio.setText(textoTooltip)
                
                # Validación de la ruta de destino vacía
                if not self._ruta.get():
                    btn_clonacion.config(state="disabled")
                    mensajes += 1
                    lblInicio.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    btnInitGit.config(state="disabled")
                    lblInicio.type = "warning"
                    if "-> La ruta de destino no puede estar vacía" not in textoTooltip:
                        self.toolTip_GitInicio.setText(f"{textoTooltip}\n-> La ruta de destino no puede estar vacía")
                else:
                    # Si se ha corregido, eliminar la advertencia
                    if "-> La ruta de destino no puede estar vacía" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta de destino no puede estar vacía", "").strip()
                        self.toolTip_GitInicio.setText(textoTooltip)

                # Validación de la ruta de destino válida
                if not ValidateOnlyPath(self._ruta.get()):
                    btn_clonacion.config(state="disabled")
                    mensajes += 1
                    lblInicio.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblInicio.type = "warning"
                    btnInitGit.config(state="disabled")
                    if "-> La ruta de destino no es válida" not in textoTooltip:
                        self.toolTip_GitInicio.setText(f"{textoTooltip}\n-> La ruta de destino no es válida")
                else:
                    # Si se ha corregido, eliminar la advertencia
                    if "-> La ruta de destino no es válida" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta de destino no es válida", "").strip()
                        self.toolTip_GitInicio.setText(textoTooltip)

                # Si no hay mensajes de advertencia, habilitar el botón
                if mensajes == 0:
                    lblInicio.config(image="", compound="center", style="Selected.TLabel")
                    lblInicio.type = "normal"
                    btn_clonacion.config(state="normal")
                    btnInitGit.config(state="disabled")
            
            def onClickRemotos():
                def obtener_remotos_background():
                    remotos = getGitRemotes(self._ruta.get())
                    if not remotos:
                        resultado_remotos.put("No hay remotos en el repositorio")
                        return
                    resultado_remotos.put(remotos)
                
                def verificar_remotos():
                    nonlocal idPopAfter
                    try:
                        remotos = resultado_remotos.get_nowait()
                        if isinstance(remotos, str):
                            comboRemotos.config(values=[remotos])
                            comboRemotos.current(0)
                            return
                        
                        if remotos[0] == "No hay remotos en el repositorio":
                            comboRemotos.config(values=[remotos[0]])
                            comboRemotos.current(0)
                            idPopAfter = None
                            return
                        
                        setURLs = set([remoto["url"] for remoto in remotos])
                        comboRemotos.config(values=tuple(setURLs))
                        comboRemotos.current(0)
                        btn_seleccion.config(state="normal")
                        idPopAfter = None
                    except queue.Empty:
                        idPopAfter = frameInicio.after(100, verificar_remotos)
                
                def guardar_remoto_seleccionado():
                    if comboRemotos.get() == "No hay remotos en el repositorio":
                        messagebox.showerror("Error", "No hay remotos en el repositorio")
                        return
                    
                    URLrepo.set(comboRemotos.get())
                    onCloseRemotos()
                
                def onClickManageRemotes():
                    def onContinue():
                        pass
                    
                    def validar_entradas():
                        if not entry_name.get():
                            boton_continuar.config(state="disabled")
                            return
                        
                        if not entry_url.get():
                            boton_continuar.config(state="disabled")
                            return
                        
                        boton_continuar.config(state="normal")
                    
                    def onChangeAccion():
                        if combo_args.get()  == "add":
                            entry_name.config(state="normal")
                            entry_url.config(state="normal")
                            validar_entradas()
                        elif combo_args.get() == "remove":
                            entry_name.config(state="normal")
                            entry_url.config(state="readonly")
                            validar_entradas()
                        elif combo_args.get() == "rename":
                            entry_name.config(state="normal")
                            entry_url.config(state="normal")
                            validar_entradas()
                        elif combo_args.get() == "prune":
                            entry_name.config(state="readonly")
                            entry_url.config(state="readonly")
                            boton_continuar.config(state="normal")
                    
                    def onClose():
                        for widget in popUp_manage.winfo_children():
                            widget.destroy()
                        
                        popUp_manage.destroy()
                    
                    popUp_manage = ttk.Toplevel()
                    popUp_manage.title("Administrar remotos")
                    popUp_manage.resizable(False, False)
                    popUp_manage.transient(self)
                    popUp_manage.protocol("WM_DELETE_WINDOW", onClose)
                    popUp_manage.grab_set()
                    
                    ttk.Label(popUp_manage, text="Accion:", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                    combo_args = ttk.Combobox(popUp_manage, values=GitRemotes_args, state="readonly")
                    combo_args.current(0)
                    combo_args.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                    
                    ttk.Label(popUp_manage, text="Nombre del remoto:", anchor="center").grid(row=1, column=0, padx=5, sticky="nsew")
                    entry_name = ttk.Entry(popUp_manage, width=50)
                    entry_name.grid(row=1, column=1, padx=5, sticky="nsew")
                    
                    ttk.Label(popUp_manage, text="URL del remoto:", anchor="center").grid(row=2, column=0, padx=5, sticky="nsew")
                    entry_url = ttk.Entry(popUp_manage, width=50)
                    entry_url.grid(row=2, column=1, padx=5, sticky="nsew")
                    
                    boton_continuar = ttk.Button(popUp_manage, text="Ejecutar accion", command=lambda: addRemote(entry_name.get(), entry_url.get()), bootstyle=(SUCCESS, OUTLINE)) # type: ignore
                    boton_continuar.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
                    centerWindow(popUp_manage)
               
                def onCloseRemotos():
                    if idPopAfter:
                        frameInicio.after_cancel(idPopAfter)
                    
                    popUp.destroy()
                
                if not self._ruta.get():
                    messagebox.showerror("Error", "La ruta del repositorio no puede estar vacía")
                    return
                
                if not isFolderInPath(".git", self._ruta.get()):
                    messagebox.showerror("Error", "La ruta seleccionada no es un repositorio de Git")
                    return
                
                resultado_remotos = queue.Queue()
                popUp = ttk.Toplevel()
                popUp.title("Administrar remotos")
                popUp.resizable(False, False)
                popUp.transient(self)
                popUp.protocol("WM_DELETE_WINDOW", onCloseRemotos)
                popUp.grab_set()
                
                ttk.Label(popUp, text="Repositorios remotos:", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                comboRemotos = ttk.Combobox(popUp, width=50, state="readonly")
                comboRemotos.config(values=("Cargando remotos ...",))
                comboRemotos.current(0)
                comboRemotos.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
                
                lbladdRemoto = ttk.Label(popUp, image=self._imagenes["Edit"], anchor="center", cursor="hand2")
                lbladdRemoto.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
                tooltipAddRemoto = ToolTip(lbladdRemoto, text="Administrar remotos")
                lbladdRemoto.bind("<Enter>", lambda e: tooltipAddRemoto.showtip("w"))
                lbladdRemoto.bind("<Leave>", lambda e: tooltipAddRemoto.hidetip())
                lbladdRemoto.bind("<Button-1>", lambda e: onClickManageRemotes())
                
                btn_seleccion = ttk.Button(popUp, text="Seleccionar", command=guardar_remoto_seleccionado, bootstyle=(SUCCESS, OUTLINE), state="disabled") # type: ignore
                btn_seleccion.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
                
                threading.Thread(target=obtener_remotos_background).start()
                idPopAfter = popUp.after(100, verificar_remotos)
                
                centerWindow(popUp)
            
            def onClickInitGit():
                archivos_git = [
                    "config",
                    "description",
                    "HEAD",
                    "hooks",
                    "info",
                    "objects",
                    "refs"
                ]
                
                for archivo in archivos_git:
                    if os.path.exists(os.path.join(self._ruta.get(), ".git", archivo)):
                        messagebox.showerror("Error", "La ruta seleccionada ya es un repositorio de Git")
                        return
                
                if not messagebox.askyesno("Informacion", "Se realizará un commit inicial para crear la rama predeterminada y realizar el commits en ella, ¿desea continuar?"):
                    return
                
                resultado = runCommand([self._git_path, "init"], self._ruta.get())
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al iniciar Git: {resultado.stderr}")
                    return

                commit = runCommand([self._git_path, "commit", "--allow-empty", "-m", "Initial commit"], self._ruta.get())
                if isinstance(commit, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al realizar el commit inicial: {commit.stderr}")
                    return
                
                self._sendNotification("Git iniciado", "Se ha iniciado Git en la ruta seleccionada", icon="git")
            
            ttk.Label(frameInicio, text="Ingresa la URL del repositorio:", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            entryURL = ttk.Entry(frameInicio, textvariable=URLrepo, width=50)
            scrollEntryURL = ttk.Scrollbar(frameInicio, orient="horizontal", bootstyle="info-round") # type: ignore
            entryURL.config(xscrollcommand=scrollEntryURL.set)
            scrollEntryURL.config(command=entryURL.xview)
            entryURL.grid(row=1, column=0, padx=5, sticky="nsew")
            scrollEntryURL.grid(row=2, column=0, padx=5, sticky="nsew")
            
            lblRemotos = ttk.Label(frameInicio, image=self._imagenes["Link"], anchor="center")
            lblRemotos.grid(row=1, rowspan=2, column=1, padx=5, pady=5, sticky="nsew")
            tooltipRemotos = ToolTip(lblRemotos, text="Ver los repositorios remotos")
            lblRemotos.bind("<Enter>", lambda e: tooltipRemotos.showtip("w"))
            lblRemotos.bind("<Leave>", lambda e: tooltipRemotos.hidetip())
            lblRemotos.bind("<Button-1>", lambda e: onClickRemotos())
            
            ttk.Label(frameInicio, text="Directorio de destino:", anchor="center").grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
            entryRuta = ttk.Entry(frameInicio, textvariable=self._ruta, width=50)
            scrollEntry = ttk.Scrollbar(frameInicio, orient="horizontal", bootstyle="info-round") # type: ignore
            entryRuta.config(xscrollcommand=scrollEntry.set)
            scrollEntry.config(command=entryRuta.xview)
            entryRuta.grid(row=4, column=0, padx=5, sticky="nsew")
            scrollEntry.grid(row=5, column=0, padx=5, sticky="nsew")
            
            maglbl = ttk.Label(frameInicio, image=self._imagenes["Magnifier"], anchor="center", cursor="hand2")
            maglbl.grid(row=4, rowspan=2, column=1, padx=5, pady=5, sticky="nsew")
            maglbl.bind("<Button-1>", lambda e: ChangePath())
            tooltipMag = ToolTip(maglbl)
            tooltipMag.setText("Seleccionar un directorio distinto")
            maglbl.bind("<Enter>", lambda e: tooltipMag.showtip("w"))
            maglbl.bind("<Leave>", lambda e: tooltipMag.hidetip())
            
            URLrepo.trace_add("write", lambda *args: ValidarEntries())
            self._ruta.trace_add("write", lambda *args: ValidarEntries())
            
            frame_botones = ttk.Frame(frameInicio)
            
            btn_clonacion = ttk.Button(frame_botones, text="Clonar", command=onClonarRepositorio, bootstyle=(INFO, OUTLINE), state="disabled") # type: ignore
            btn_clonacion.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            ttk.Label(frame_botones, text="o", anchor="center").grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            
            btnInitGit = ttk.Button(frame_botones, text="Iniciar Git", command=onClickInitGit, bootstyle=(SUCCESS, OUTLINE), state="disabled") # type: ignore
            btnInitGit.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
            
            columnas = frame_botones.grid_size()[0]
            for columna in range(columnas):
                if columna %2 == 0:
                    frame_botones.grid_columnconfigure(columna, weight=1)
                
            frame_botones.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
            frameInicio.grid_columnconfigure(0, weight=1)
        
        def contentFrameCommit():
            def obtenerRamas():
                def verificarResultado():
                    try:
                        ramas = resultadoRamas.get_nowait()
                        if (self._ruta.get() and ramas) and isFolderInPath(".git", self._ruta.get()):
                            combobranch.config(values=list(ramas.keys()))
                            combobranch.current(list(ramas.values()).index(True))
                            return
                        combobranch.config(values=("Ruta invalida",))
                        combobranch.current(0)
                    except:
                        frameCommit.after(100, verificarResultado)
                    
                    clearQueue(resultadoRamas)
                    
                def obtener_background():
                    if os.path.exists(self._ruta.get()) and isFolderInPath(".git", self._ruta.get()):
                        ramas = getGitBranches(self._ruta.get())
                        resultadoRamas.put(ramas)
                        procesosFrame.put("Ramas, exitoso")
                        return
                    resultadoRamas.put({"Ruta no valida":True})
                    procesosFrame.put("Ramas, fallido")
                    
                btn_commit.config(state="disabled")
                resultadoRamas = queue.Queue()
                combobranch.config(values=("Cargando ramas ...",))
                combobranch.current(0)
                threading.Thread(target=obtener_background).start()
                frameCommit.after(100, verificarResultado)    
            
            def validarEntries():
                textoTooltip = self.toolTip_GitCommit.getText()
                mensajes = 0
                
                if not self._ruta.get():
                    btn_commit.config(state="disabled")
                    mensajes += 1
                    lblCommit.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblCommit.type = "warning"
                    if "-> La ruta del repositorio no puede estar vacía" not in textoTooltip:
                        self.toolTip_GitCommit.setText(f"{textoTooltip}\n-> La ruta del repositorio no puede estar vacía")
                else:
                    if "-> La ruta del repositorio no puede estar vacía" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta del repositorio no puede estar vacía", "").strip()
                        self.toolTip_GitCommit.setText(textoTooltip)
                
                if not os.path.exists(self._ruta.get()) or not isFolderInPath(".git", self._ruta.get()):
                    btn_commit.config(state="disabled")
                    mensajes += 1
                    lblCommit.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblCommit.type = "warning"
                    if "-> La ruta del repositorio no es válida" not in textoTooltip:
                        self.toolTip_GitCommit.setText(f"{textoTooltip}\n-> La ruta del repositorio no es válida")
                else:
                    if "-> La ruta del repositorio no es válida" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta del repositorio no es válida", "").strip()
                        self.toolTip_GitCommit.setText(textoTooltip)
                
                if not entrymsg.get() or (msgCommitVar.get() == "Introduzca aqui el mensaje del commit..." and str(entrymsg["foreground"]) == "gray"):
                    btn_commit.config(state="disabled")
                    mensajes += 1
                    lblCommit.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblCommit.type = "warning"
                    if "-> El mensaje del commit no puede estar vacío" not in textoTooltip:
                        self.toolTip_GitCommit.setText(f"{textoTooltip}\n-> El mensaje del commit no puede estar vacío")
                else:
                    if "-> El mensaje del commit no puede estar vacío" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> El mensaje del commit no puede estar vacío", "").strip()
                        self.toolTip_GitCommit.setText(textoTooltip)
                
                if not cambios:
                    btn_commit.config(state="disabled")
                    mensajes += 1
                    lblCommit.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblCommit.type = "warning"
                    if "-> No hay cambios para realizar commit" not in textoTooltip:
                        self.toolTip_GitCommit.setText(f"{textoTooltip}\n-> No hay cambios para realizar commit")
                else:
                    if "-> No hay cambios para realizar commit" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> No hay cambios para realizar commit", "").strip()
                        self.toolTip_GitCommit.setText(textoTooltip)
                
                if not self._userGit.get() or not self._correoGit.get():
                    btn_commit.config(state="disabled")
                    mensajes += 1
                    lblCommit.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblCommit.type = "warning"
                    if "-> El usuario y el correo no pueden estar vacíos" not in textoTooltip:
                        self.toolTip_GitCommit.setText(f"{textoTooltip}\n-> El usuario y el correo no pueden estar vacíos")
                else:
                    if "-> El usuario y el correo no pueden estar vacíos" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> El usuario y el correo no pueden estar vacíos", "").strip()
                        self.toolTip_GitCommit.setText(textoTooltip)
                
                if mensajes == 0:
                    lblCommit.config(image="", compound="center", style="Selected.TLabel")
                    lblCommit.type = "normal"
                    btn_commit.config(state="normal")
            
            def onChangeBranch():
                ramaActual = getCurrentBrach(getGitBranches(self._ruta.get()))
                if ramaSeleccionada.get() != ramaActual and ramaActual != "No hay ramas":
                    if messagebox.askyesno("Advertencia", f"La rama seleccionada no es la rama actual ({ramaActual}), ¿Desea continuar?"):
                        reultado = runCommand([self._git_path, "checkout", ramaSeleccionada.get()], self._ruta.get())
                        
                        if isinstance(reultado, subprocess.CalledProcessError):
                            messagebox.showerror("Error", f"Error al cambiar de rama: {reultado.stderr}")
                            return
                        
                        messagebox.showinfo("Información", "Se ha cambiado de rama correctamente")
                    else:
                        ramaSeleccionada.set(ramaActual)
            
            def onCreateBranch():
                def createBranch():
                    def backgroundCreateBranch():
                        resultado = runCommand([self._git_path, "branch", ramaNueva.get()], self._ruta.get())
                        if isinstance(resultado, subprocess.CalledProcessError):
                            resultado_createBranch.put((False, resultado.stderr))
                            return
                        
                        if chk_cambioRamaVar.get():
                            resultado = runCommand([self._git_path, "checkout", ramaNueva.get()], self._ruta.get())
                            if isinstance(resultado, subprocess.CalledProcessError):
                                resultado_createBranch.put((False, resultado.stderr))
                                return
                        
                        resultado_createBranch.put((True, "Rama creada correctamente"))
                        obtenerRamas()
                    
                    def verificarCreateBranch():
                        try:
                            exito, mensaje = resultado_createBranch.get_nowait()
                            btn_createBranch.config(state="normal", text="Crar rama")
                            popUp.protocol("WM_DELETE_WINDOW", popUp.destroy)
                            if not exito:
                                messagebox.showerror("Error", f"Error al crear la rama: {mensaje}")
                                return
                            messagebox.showinfo("Información", mensaje)
                        except:
                            popUp.protocol("WM_DELETE_WINDOW", lambda: doNothing())
                            frameCommit.after(100, verificarCreateBranch)
                            return
                        
                        clearQueue(resultado_createBranch)
                        popUp.destroy()
                    
                    if not ramaNueva.get():
                        messagebox.showerror("Error", "El nombre de la rama no puede estar vacío")
                        return
                    
                    resultado_createBranch = queue.Queue()
                    btn_createBranch.config(state="disabled", text="Creando rama ...")
                    threading.Thread(target=backgroundCreateBranch).start()
                    frameCommit.after(100, verificarCreateBranch)
                
                if not self._ruta.get() or not isFolderInPath(".git", self._ruta.get()):
                    messagebox.showerror("Error", "La ruta del repositorio no es válida")
                    return
                
                popUp = ttk.Toplevel()
                popUp.title("Crear rama")
                popUp.resizable(False, False)
                popUp.transient(self)
                
                ramaNueva = tk.StringVar()
                ttk.Label(popUp, text="Nombre de la nueva rama", style="info.TLabel", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                entryRama = ttk.Entry(popUp, textvariable=ramaNueva, width=50)
                entryRama.grid(row=1, column=0, padx=5, sticky="nsew")
                
                chk_cambioRamaVar = tk.BooleanVar()
                chk_cambioRama = ttk.Checkbutton(popUp, text="Cambiar a la nueva rama", variable=chk_cambioRamaVar, style="warning-round-toggle")
                chk_cambioRama.grid(row=2, column=0, padx=5, pady=5)
                
                btn_createBranch = ttk.Button(popUp, text="Crear rama", command=createBranch, bootstyle=(INFO, OUTLINE)) # type: ignore
                btn_createBranch.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
                centerWindow(popUp)
            
            def onDeleteBranch():
                def deleteBranch():
                    def backgroundDeleteBranch():
                        resultado = runCommand([self._git_path, "branch", "-d", combobranch.get()], self._ruta.get())
                        if isinstance(resultado, subprocess.CalledProcessError):
                            resultado_deleteBranch.put((False, resultado.stderr))
                            return
                        
                        resultado_deleteBranch.put((True, "Rama eliminada correctamente"))
                        obtenerRamas()
                    
                    def verificarDeleteBranch():
                        try:
                            exito, mensaje = resultado_deleteBranch.get_nowait()
                            btn_deleteBranch.config(state="normal", text="Eliminar Rama")
                            if not exito:
                                messagebox.showerror("Error", f"Error al eliminar la rama: {mensaje}")
                                return
                            messagebox.showinfo("Información", mensaje)
                        except:
                            frameCommit.after(100, verificarDeleteBranch)
                            return
                        
                        clearQueue(resultado_deleteBranch)
                        popUp.destroy()
                    
                    if combobranch.get() == "master" or combobranch.get() == "main":
                        messagebox.showerror("Error", "No se puede eliminar la rama principal")
                        return
                    
                    if combobranch.get() == "No hay ramas":
                        messagebox.showerror("Error", "No hay ramas para eliminar")
                        return
                                        
                    if messagebox.askyesno("Advertencia", f"¿Está seguro de eliminar la rama {combobranch.get()}?"):
                        resultado_deleteBranch = queue.Queue()
                        btn_deleteBranch.config(state="disabled", text="Eliminando rama ...")
                        threading.Thread(target=backgroundDeleteBranch).start()
                        frameCommit.after(100, verificarDeleteBranch)
                        
                def obtenerramas_background():
                    if os.path.exists(self._ruta.get()) and isFolderInPath(".git", self._ruta.get()):
                        ramas = getGitBranches(self._ruta.get())
                        
                        # Remover de la lista la rama seleccionada actualmente
                        if ramaSeleccionada.get() in ramas:
                            del ramas[ramaSeleccionada.get()]
                        
                        resultadoRamas.put(ramas)
                        return
                    resultadoRamas.put({"Ruta no valida":True})
                
                def verificar_resultado():
                    try:
                        ramas = resultadoRamas.get_nowait()
                        btn_deleteBranch.config(state="normal")

                        if (self._ruta.get() and ramas) and isFolderInPath(".git", self._ruta.get()):
                            combobranch.config(values=list(ramas.keys()))
                            combobranch.current(0)
                            return
                        combobranch.config(values=("No hay ramas",))
                        combobranch.current(0)
                    except:
                        frameCommit.after(100, verificar_resultado)
                        return
                    
                    clearQueue(resultadoRamas)
                
                if not self._ruta.get() or not isFolderInPath(".git", self._ruta.get()):
                    messagebox.showerror("Error", "La ruta del repositorio no es válida")
                    return 
                    
                popUp = ttk.Toplevel()
                popUp.title("Eliminar rama")
                popUp.resizable(False, False)
                popUp.transient(self)
                
                resultadoRamas = queue.Queue()
                ttk.Label(popUp, text="Seleccione la rama a eliminar", style="info.TLabel", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                combobranch = ttk.Combobox(popUp, state="readonly", width=50)
                combobranch.config(values=("Cargando ramas ...",))
                combobranch.current(0)
                combobranch.grid(row=1, column=0, padx=5, sticky="nsew")
                
                threading.Thread(target=obtenerramas_background).start()
                frameCommit.after(100, verificar_resultado)
                
                btn_deleteBranch = ttk.Button(popUp, text="Eliminar rama", command=deleteBranch, bootstyle=(DANGER, OUTLINE)) # type: ignore
                btn_deleteBranch.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
                btn_deleteBranch.config(state="disabled")
                centerWindow(popUp)
                
            
            def onCommit():
                def backgroundCommit():
                    resultado = runCommand([self._git_path, "add", "."], self._ruta.get())
                    if isinstance(resultado, subprocess.CalledProcessError):
                        resultado_commit.put((False, resultado.stderr))
                        return
                    
                    if accion == "Commit":
                        resultado = runCommand([self._git_path, "commit", "-m", msgCommitVar.get()], self._ruta.get())
                        if isinstance(resultado, subprocess.CalledProcessError):
                            resultado_commit.put((False, resultado.stderr))
                            return
                        resultado_commit.put((True, "Commit realizado correctamente"))
                    elif accion == "Commit y Push":
                        resultado = runCommand([self._git_path, "commit", "-m", msgCommitVar.get()], self._ruta.get())
                        if isinstance(resultado, subprocess.CalledProcessError):
                            resultado_commit.put((False, resultado.stderr))
                            return
                        resultado = runCommand([self._git_path, "push", "origin", ramaSeleccionada.get()], self._ruta.get())
                        if isinstance(resultado, subprocess.CalledProcessError):
                            resultado_commit.put((False, resultado.stderr))
                            return
                        resultado_commit.put((True, "Commit y Push realizado correctamente"))
                    
                def verificarCommit():
                    try:
                        exito, mensaje = resultado_commit.get_nowait()
                        btn_commit.config(state="normal", text="Commit")
                        if not exito:
                            messagebox.showerror("Error", f"Error al realizar el commit: {mensaje}")
                            self._sendNotification("Error al realizar el commit", mensaje, icon="git")
                            return
                        messagebox.showinfo("Información", mensaje)
                        self._sendNotification("Commit realizado", mensaje, icon="git")
                    except:
                        frameCommit.after(100, verificarCommit)
                    
                    clearQueue(resultado_commit)
                
                accion = accionSeleccionada.get()
                resultado_commit = queue.Queue()
                btn_commit.config(state="disabled", text="Realizando commit ...")
                threading.Thread(target=backgroundCommit).start()
                frameCommit.after(100, verificarCommit)
            
            def obtenerArchivosModificado():
                def onModifyFiles():
                    cambios.clear()
                    if not self._ruta.get() or not isFolderInPath(".git", self._ruta.get()):
                        resultadoCambios.put((False, "Ruta invalida"))
                        return
                    
                    listaArchivos = getModifiedFilesGit(self._ruta.get())
                    if len(listaArchivos) == 1 and  listaArchivos[0][0] == "Error":
                        resultadoCambios.put((False, listaArchivos[0][1]))
                        return
                    
                    detalleSimbolos = {
                        "??" :{"nombre":"Nuevo", "estiloLBL":INFO},
                        "M"  :{"nombre":"Modificado", "estiloLBL":SUCCESS},
                        "D"  :{"nombre":"Eliminado", "estiloLBL":DANGER},
                        "A"  :{"nombre":"Añadido", "estiloLBL":INFO},
                        "R"  :{"nombre":"Renombrado", "estiloLBL":WARNING},
                        "C"  :{"nombre":"Copiado", "estiloLBL":WARNING},
                        "U"  :{"nombre":"Actualizado", "estiloLBL":INFO},
                    }
                    
                    for archivo in listaArchivos:
                        simbolo, nombre = archivo
                        cambios.append({
                            "estado"  : detalleSimbolos[simbolo]["nombre"],
                            "archivo" : nombre,
                            "estilo"  : detalleSimbolos[simbolo]["estiloLBL"]
                        })
                        
                    resultadoCambios.put((True, "Cambios obtenidos correctamente"))
                
                def actualizarFrameCambios():
                    scrolled_frame.clear_widgets()
                    
                    if not self._ruta.get() or not isFolderInPath(".git", self._ruta.get()):
                        scrolled_frame.add_widget(ttk.Label(scrolled_frame, text="Ruta invalida", style="info.TLabel", anchor="center"), row=0, column=0, padx=5, pady=5, sticky="nsew")
                        return
                    
                    if not cambios:
                        scrolled_frame.add_widget(ttk.Label(scrolled_frame, text="No hay cambios", style="info.TLabel", anchor="center"), row=0, column=0, padx=5, pady=5, sticky="nsew")
                    
                    for i, cambio in enumerate(cambios):
                        detallesFrame = ttk.LabelFrame(scrolled_frame, text="Detalles de los cambios", bootstyle=cambio["estilo"]) # type: ignore
                        
                        ttk.Label(detallesFrame, text=f"Estado: {cambio['estado']}", style="info.TLabel", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                        ttk.Label(detallesFrame, text=f"Archivo: {cambio['archivo']}", style="info.TLabel", anchor="center").grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
                        
                        detallesFrame.grid_columnconfigure(0, weight=1)
                        scrolled_frame.add_widget(detallesFrame, row=i, column=0, padx=5, pady=5, sticky="nsew")
                    
                    scrolled_frame.grid_columnconfigure(0, weight=1)
                        
                
                def verificarResultado():
                    try:
                        resultadoCambios.get_nowait()
                        actualizarFrameCambios()
                    except queue.Empty:
                        frameCommit.after(100, verificarResultado)
                        return
                    
                    clearQueue(resultadoCambios)
                
                resultadoCambios = queue.Queue()
                threading.Thread(target=onModifyFiles).start()
                frameCommit.after(100, verificarResultado)
            
            cambios = []
            procesosFrame = queue.Queue()
            
            ttk.Label(frameCommit, text="Directorio del repositorio", style="info.TLabel", anchor="center").grid(row=0, column=0, padx=5, sticky="nsew")
            entryRuta = ttk.Entry(frameCommit, textvariable=self._ruta, width=50)
            entryRuta.grid(row=1, column=0, padx=5, sticky="nsew")
            scrollRuta = ttk.Scrollbar(frameCommit, orient="horizontal", bootstyle="info-round") # type: ignore
            entryRuta.config(xscrollcommand=scrollRuta.set)
            scrollRuta.config(command=entryRuta.xview)
            scrollRuta.grid(row=2, column=0, padx=5, sticky="nsew")
            lblmagCommit = ttk.Label(frameCommit, image=self._imagenes["Magnifier"], anchor="center", cursor="hand2")
            lblmagCommit.grid(row=1, rowspan=2, column=1, padx=5, sticky="nsew")
            lblmagCommit.bind("<Button-1>", lambda e: ChangePath())
            
            tooltiplblmag = ToolTip(lblmagCommit)
            tooltiplblmag.setText("Seleccionar un directorio distinto")
            lblmagCommit.bind("<Enter>", lambda e: tooltiplblmag.showtip("w"))
            lblmagCommit.bind("<Leave>", lambda e: tooltiplblmag.hidetip())
            
            msgCommitVar = tk.StringVar()
            ttk.Label(frameCommit, text="Mensaje de la confirmacion", style="info.TLabel", anchor="center").grid(row=3, column=0, padx=5, sticky="nsew")
            entrymsg = ttk.Entry(frameCommit, textvariable=msgCommitVar, width=50)
            entrymsg.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
            lblinfoCommit = ttk.Label(frameCommit, image=self._imagenes["Info"], style="info.TLabel", anchor="center", cursor="arrow")
            tooltipLblCommit = ToolTip(lblinfoCommit, "Introduzca el mensaje del commit en el campo de entrada")
            lblinfoCommit.bind("<Enter>", lambda e: tooltipLblCommit.showtip("w"))
            lblinfoCommit.bind("<Leave>", lambda e: tooltipLblCommit.hidetip())
            lblinfoCommit.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
            
            ramaSeleccionada = tk.StringVar()
            ttk.Label(frameCommit, text="Rama", style="info.TLabel", anchor="center").grid(row=5, column=0, padx=5, sticky="nsew")
            combobranch = ttk.Combobox(frameCommit, width=50, state="readonly", textvariable=ramaSeleccionada)
            combobranch.grid(row=6, column=0, padx=5, pady=5, sticky="nsew")
            combobranch.bind("<<ComboboxSelected>>", lambda e: onChangeBranch())
            
            framebotonesBranch = ttk.Frame(frameCommit)
            
            lblAddBranch = ttk.Label(framebotonesBranch, image=self._imagenes["Add"], style="info.TLabel", cursor="hand2")
            tooltipAddBranch = ToolTip(lblAddBranch, "Crear una nueva rama")
            lblAddBranch.bind("<Enter>", lambda e: tooltipAddBranch.showtip("w"))
            lblAddBranch.bind("<Leave>", lambda e: tooltipAddBranch.hidetip())
            lblAddBranch.bind("<Button-1>", lambda e: onCreateBranch())
            lblAddBranch.grid(row=0, column=1, padx=5, sticky="nsew")
            
            lblDeleteBranch = ttk.Label(framebotonesBranch, image=self._imagenes["Trash"], style="info.TLabel", cursor="hand2")
            tooltipDeleteBranch = ToolTip(lblDeleteBranch, "Eliminar la rama seleccionada")
            lblDeleteBranch.bind("<Enter>", lambda e: tooltipDeleteBranch.showtip("w"))
            lblDeleteBranch.bind("<Leave>", lambda e: tooltipDeleteBranch.hidetip())
            lblDeleteBranch.bind("<Button-1>", lambda e: onDeleteBranch())
            lblDeleteBranch.grid(row=0, column=2, padx=5, sticky="nsew")
            
            framebotonesBranch.grid(row=6, column=1, padx=5, pady=5, sticky="nsew")
            
            accionSeleccionada = tk.StringVar()
            ttk.Label(frameCommit, text="Acciones", style="info.TLabel", anchor="center").grid(row=7, column=0, padx=5, sticky="nsew")
            comboAcciones = ttk.Combobox(frameCommit, values=("Commit", "Commit y Push"), state="readonly", textvariable=accionSeleccionada)
            comboAcciones.current(0)
            comboAcciones.grid(row=8, column=0, padx=5, pady=5, sticky="nsew")
            
            framemostrarCambios = ttk.LabelFrame(frameCommit, text="Cambios", style="warning.TLabelFrame") # type: ignore
            scrolled_frame = ScrolledFrame(framemostrarCambios, "warning-rounded")
            scrolled_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            ttk.Label(scrolled_frame, text="Seleccione una ruta!", style="warning.TLabel", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            scrolled_frame.grid_columnconfigure(0, weight=1)
            framemostrarCambios.grid_columnconfigure(0, weight=1)
            framemostrarCambios.grid_rowconfigure(0, weight=1)
            framemostrarCambios.grid(row=9, column=0, columnspan=2, padx=5, sticky="nsew")
            
            btn_commit = ttk.Button(frameCommit, text="Commit", command=onCommit, bootstyle=(INFO, OUTLINE)) # type: ignore
            btn_commit.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            
            obtenerRamas()
            msgCommitVar.trace_add("write", lambda *args: validarEntries())
            self._ruta.trace_add("write", lambda *args: validarEntries())
            self._ruta.trace_add("write", lambda *args: obtenerRamas())
            self._ruta.trace_add("write", lambda *args: obtenerArchivosModificado())
            
            frameCommit.grid_columnconfigure(0, weight=1)
            frameCommit.grid_rowconfigure(9, weight=1)
            
        def contentFrameLogs():
            def validarRuta():
                textoTooltip = self.toolTip_GitLogs.getText()
                mensajes = 0
                if not self._ruta.get():
                    btnLogs.config(state="disabled")
                    lblLogs.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblLogs.type = "warning"
                    mensajes += 1
                    if "-> La ruta del repositorio no puede estar vacía" not in textoTooltip:
                        self.toolTip_GitLogs.setText(f"{textoTooltip}\n-> La ruta del repositorio no puede estar vacía")
                else:
                    if "-> La ruta del repositorio no puede estar vacía" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta del repositorio no puede estar vacía", "").strip()
                        self.toolTip_GitLogs.setText(textoTooltip)
                
                if not ValidateOnlyPath(self._ruta.get()):
                    btnLogs.config(state="disabled")
                    lblLogs.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblLogs.type = "warning"
                    mensajes += 1
                    if "-> La ruta del repositorio no es válida" not in textoTooltip:
                        self.toolTip_GitLogs.setText(f"{textoTooltip}\n-> La ruta del repositorio no es válida")
                else:
                    if "-> La ruta del repositorio no es válida" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta del repositorio no es válida", "").strip()
                        self.toolTip_GitLogs.setText(textoTooltip)
                
                if not isFolderInPath(".git", self._ruta.get()):
                    btnLogs.config(state="disabled")
                    lblLogs.config(image=self._imagenes["Warning"], compound="left", style="Warning.TLabel")
                    lblLogs.type = "warning"
                    mensajes += 1
                    if "-> La ruta del repositorio no es un repositorio de Git" not in textoTooltip:
                        self.toolTip_GitLogs.setText(f"{textoTooltip}\n-> La ruta del repositorio no es un repositorio de Git")
                else:
                    if "-> La ruta del repositorio no es un repositorio de Git" in textoTooltip:
                        textoTooltip = textoTooltip.replace("-> La ruta del repositorio no es un repositorio de Git", "").strip()
                        self.toolTip_GitLogs.setText(textoTooltip)
                
                if mensajes == 0:
                    lblLogs.config(image="", compound="center", style="Selected.TLabel")
                    lblLogs.type = "normal"
                    btnLogs.config(state="normal")
            
            def obtenerLogs():
                def verificarResultado():
                    try:
                        logs = resultadoLogs.get_nowait()
                        if logs:
                            txtLogs.config(state="normal")
                            txtLogs.delete("1.0", "end")
                            txtLogs.insert("1.0", logs)
                            txtLogs.config(state="disabled")
                            return
                        txtLogs.config(state="normal")
                        txtLogs.delete("1.0", "end")
                        txtLogs.insert("1.0", "No hay logs disponibles")
                        txtLogs.config(state="disabled")
                    except:
                        frameLogs.after(100, verificarResultado)
                    
                    clearQueue(resultadoLogs)
                
                def obtener_background():
                    logs = runCommand([self._git_path, "log"], self._ruta.get(), retornarEn='bytes')
                    if isinstance(logs, subprocess.CalledProcessError):
                        resultadoLogs.put("")
                        return
                    resultadoLogs.put(logs.stdout.decode("utf-8"))
                
                resultadoLogs = queue.Queue()
                threading.Thread(target=obtener_background).start()
                frameLogs.after(100, verificarResultado)
            
            ttk.Label(frameLogs, text="Directorio del repositorio", style="info.TLabel", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            entryRuta = ttk.Entry(frameLogs, textvariable=self._ruta, style="info.TEntry", width=50)
            entryRuta.grid(row=1, column=0, padx=5, sticky="nsew")
            lblmagRuta = ttk.Label(frameLogs, image=self._imagenes["Magnifier"], anchor="center", cursor="hand2")
            lblmagRuta.grid(row=1, rowspan=2, column=1, padx=5, pady=5, sticky="nsew")
            lblmagRuta.bind("<Button-1>", lambda e: ChangePath())
            scrollEntry = ttk.Scrollbar(frameLogs, orient="horizontal", bootstyle="info-round") # type: ignore
            entryRuta.config(xscrollcommand=scrollEntry.set)
            scrollEntry.config(command=entryRuta.xview)
            scrollEntry.grid(row=2, column=0, padx=5, sticky="nsew")
            
            tooltiplblmag = ToolTip(lblmagRuta)
            tooltiplblmag.setText("Seleccionar un directorio distinto")
            lblmagRuta.bind("<Enter>", lambda e: tooltiplblmag.showtip("w"))
            lblmagRuta.bind("<Leave>", lambda e: tooltiplblmag.hidetip())
            
            txtLogs = scrolledtext.ScrolledText(frameLogs, width=50, height=20, state="disabled")
            txtLogs.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            btnLogs = ttk.Button(frameLogs, text="Obtener logs", command=obtenerLogs, bootstyle=(INFO, OUTLINE), state="disabled") # type: ignore
            btnLogs.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            
            self._ruta.trace_add("write", lambda *args: validarRuta())
            frameLogs.grid_columnconfigure(0, weight=1)
            frameLogs.grid_rowconfigure(3, weight=1)
        
        frameInformacion = ttk.LabelFrame(self.frameGit, text="Informacion", style="info.TLabelframe", name="git_info")
        ttk.Label(frameInformacion, text="Version de Git:", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        entryGitV = ttk.Entry(frameInformacion)
        entryGitV.insert(0, self._versionGit if self._versionGit else "No disponible")
        entryGitV.config(state="readonly")
        entryGitV.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        
        lblEdit = ttk.Label(frameInformacion, image=self._imagenes["Edit"], cursor="hand2")
        lblEdit.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        toolTipEdit = ToolTip(lblEdit, "Editar usuario y correo de Git")
        lblEdit.bind("<Enter>", lambda e: toolTipEdit.showtip("w"))
        lblEdit.bind("<Leave>", lambda e: toolTipEdit.hidetip())
        lblEdit.bind("<Button-1>", lambda e: self._funcCambiarIDGit())
        
        frameInformacion.grid_columnconfigure(0, weight=1)
        
        frameInformacion.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        frameInicio = ttk.Frame(self.frameGit)
        frameCommit = ttk.Frame(self.frameGit)
        frameLogs = ttk.Frame(self.frameGit)
        
        URLrepo = ttk.StringVar()
        
        lbl_frame = ttk.Frame(self.frameGit, style="Custom.TFrame", name="git_selector")
        lblInicio = SelectionLabel(lbl_frame, text="Inicio", style="Custom.TLabel", anchor="center")
        lblInicio.grid(row=0, column=0, sticky="nsew", ipady=6)
        lblInicio.onClick(callback=onClickFrame)
        
        self.toolTip_GitInicio = ToolTip(lblInicio)
        lblInicio.bind("<Enter>", lambda e: self.toolTip_GitInicio.showtip("n"))
        lblInicio.bind("<Leave>", lambda e: self.toolTip_GitInicio.hidetip())
        
        lblCommit = SelectionLabel(lbl_frame, text="Commit", style="Custom.TLabel", anchor="center")
        lblCommit.grid(row=0, column=1, sticky="nsew", ipady=6)
        lblCommit.onClick(callback=onClickFrame)
        
        self.toolTip_GitCommit = ToolTip(lblCommit)
        lblCommit.bind("<Enter>", lambda e: self.toolTip_GitCommit.showtip("n"))
        lblCommit.bind("<Leave>", lambda e: self.toolTip_GitCommit.hidetip())
        
        lblLogs = SelectionLabel(lbl_frame, text="Logs", style="Custom.TLabel", anchor="center")
        lblLogs.grid(row=0, column=2, sticky="nsew", ipady=6)
        lblLogs.onClick(callback=onClickFrame)
        
        self.toolTip_GitLogs = ToolTip(lblLogs)
        lblLogs.bind("<Enter>", lambda e: self.toolTip_GitLogs.showtip("n"))
        lblLogs.bind("<Leave>", lambda e: self.toolTip_GitLogs.hidetip())
        
        columnas, filas = lbl_frame.grid_size()
        for columna in range(columnas):
            lbl_frame.grid_columnconfigure(columna, weight=1)
        
        for fila in range(filas):
            lbl_frame.grid_rowconfigure(fila, weight=1)
        lbl_frame.grid(row=2, column=0, padx=5, sticky="nsew")
        
        self.frameGit.grid_columnconfigure(0, weight=1)
        self.frameGit.grid_rowconfigure(1, weight=1)
        
        contentFrameInicio()
        contentFrameCommit()
        setGitTooltipText()
        contentFrameLogs()
        goToGitFrame("Inicio")
    
    def _tareasFrame(self):
        def conteo_tareas():
            total_pasos = 1
            self._tareas.clear()
            self._taskWidgets.clear()
            taskWidgets.clear()
            scrolled_frame.clear_widgets()
            if self.CrearRutaVar.get():
                tarea = {
                    "accion": "Crear ruta",
                    "estado": "Pendiente",
                    "info": None
                }
                self._tareas.append(tarea.copy())
                total_pasos += 1
            
            if self.EliminarContenidoVar.get():
                tarea = {
                    "accion": "Eliminar contenido de la carpeta",
                    "estado": "Pendiente",
                    "info": None
                }
                self._tareas.append(tarea.copy())
                total_pasos += 1
            
            tarea = {
                "accion": "Inicializar proyecto Node",
                "estado": "Pendiente",
                "info": None
            }
            self._tareas.append(tarea.copy())
            
            for dic in self._modulosNPM:
                if dic["usar"] is not None and dic["usar"].get():
                    tarea = {
                        "accion": f"Instalar modulo {dic['nombre']} - {dic['version'].get()}",
                        "estado": "Pendiente",
                        "info": dic
                    }
                    self._tareas.append(tarea.copy())
                    total_pasos += 1
            
            for dic in self._checkVars:
                dic = dict(dic)
                for clave, var in dic.items():
                    if var.get() and clave == "Crear directorios adicionales":
                        tarea = {
                            "accion": "Crear directorios adicionales",
                            "estado": "Pendiente",
                            "info": None
                        }
                        self._tareas.append(tarea.copy())
                        total_pasos += 1
                    elif var.get() and clave == "Abrir en VS Code al finalizar":
                        tareas = {
                            "accion": "Abrir en VS Code",
                            "estado": "Pendiente",
                            "info": None
                        }
                        self._tareas.append(tareas.copy())
                        total_pasos += 1
            
            return total_pasos
        
        def borrarContenidoDirectorio():
            archivos, carpetas = lista_archivos_directorios(self._ruta.get())
            ruta = self._ruta.get()
            for archivo in archivos:
                ruta_completa = os.path.join(ruta, archivo)
                os.remove(ruta_completa)
            
            for carpeta in carpetas:
                ruta_completa = os.path.join(ruta, carpeta)
                shutil.rmtree(ruta_completa)
        
        def crearDirectorios():
            ruta = self._ruta.get() + "/src"
            if not os.path.exists(ruta):
                os.makedirs(ruta)
            
            for archivo in archivos:
                with open(f"{ruta}/{archivo}", "w") as f:
                    pass
                time.sleep(2)
            
            for carpeta in carpetas:
                if not os.path.exists(f"{ruta}/{carpeta}"):
                    os.makedirs(f"{ruta}/{carpeta}")
                    
            for archivo, contenido in archivos_p:
                with open(f"{self._ruta.get()}/{archivo}", "w") as f:
                    f.write(contenido)
                time.sleep(2)
        
        def crearRuta():
            if not os.path.exists(self._ruta.get()):
                os.makedirs(self._ruta.get())
        
        def InicializarNode():
            try:
                # Ejecutar `npm init -y` para inicializar el proyecto
                estado = runCommand([self._npm_path, "init", "-y"], self._ruta.get())
                
                if isinstance(estado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al inicializar el proyecto Node: {estado}")
                    try:
                        borrarContenidoDirectorio()
                        return int(-1)
                    except:
                        return int(-1)
                
                return int(0)
            except Exception as ex:
                messagebox.showerror("Error", f"Error al inicializar el proyecto Node: {ex}")
                try:
                    borrarContenidoDirectorio()
                    return int(-1)
                except:
                    return int(-1)
        
        def actualizarEventsFrame():
            for i, tarea in enumerate(self._tareas, 1):
                if tarea["estado"] == "Pendiente":
                    style = WARNING
                    icon = self._imagenes["Pending"]
                elif tarea["estado"] == "En progreso":
                    style = INFO
                    icon = self._imagenes["Running"]
                elif tarea["estado"] == "Completado":
                    style = SUCCESS
                    icon = self._imagenes["Check"]
                else:
                    style = DANGER
                    icon = self._imagenes["Error"]
                
                if i not in taskWidgets:
                    subFrame = ttk.LabelFrame(scrolled_frame, text=f"Tarea {i} de {len(self._tareas)}", bootstyle=style) # type: ignore
                    ttk.Label(subFrame, image=icon).grid(row=0, column=0, sticky="nsew", padx=3)
                    ttk.Label(subFrame, text=tarea["accion"]).grid(row=0, column=1, sticky="nsew", padx=9)
                    ttk.Label(subFrame, text=tarea["estado"]).grid(row=0, column=2, sticky="nsew", padx=3)
                    
                    columnas = subFrame.grid_size()[0]
                    for columna in range(columnas):
                        subFrame.grid_columnconfigure(columna, weight=1)

                    #subFrame.grid(row=i-1, column=0, sticky="nsew", padx=5, pady=5)
                    scrolled_frame.add_widget(subFrame, row=i-1, column=0, padx=5, pady=5, sticky="nsew")
                    taskWidgets[i] = subFrame
                else:
                    subFrame = taskWidgets[i]
                    subFrame.config(text=f"Tarea {i} de {len(self._tareas)}", bootstyle=style)  # type: ignore
                    subFrame.grid_slaves(row=0, column=0)[0].config(image=icon)
                    subFrame.grid_slaves(row=0, column=1)[0].config(text=tarea["accion"])
                    subFrame.grid_slaves(row=0, column=2)[0].config(text=tarea["estado"])

            columnas = scrolled_frame.grid_size()[0]
            for columna in range(columnas):
                scrolled_frame.grid_columnconfigure(columna, weight=1)
            
            # Eliminar los frames que no se han actualizado
            for key in list(taskWidgets.keys()):
                if key not in range(1, len(self._tareas)+1):
                    frame = taskWidgets.pop(key)
                    frame.destroy()
        
        def actualizarFrameDetalles(detalles:str):
            tareasCompletadas = 0
            for tarea in self._tareas:
                if tarea["estado"] == "Completado":
                    tareasCompletadas += 1
            
            tareasPendientes = len(self._tareas) - tareasCompletadas
            tareasCompletadaslbl.config(text=tareasCompletadas)
            tareasPendienteslbl.config(text=tareasPendientes)
            entryDescripcion.config(state="normal")
            entryDescripcion.delete(0, "end")
            entryDescripcion.insert(0, detalles)
            entryDescripcion.config(state="readonly")
            progreso["value"] = (tareasCompletadas/len(self._tareas)) * 100
        
        def verificar_avanceTareas():
            try:
                continuar, valores = resultado.get_nowait()
                actualizarFrameDetalles(str(valores))
                actualizarEventsFrame()
                if not continuar:
                    self._funcGoToFrame("Principal")
                    self.Tareas.config(state="disabled")
                    self._funcOnUpdateFrames()
                    self.protocol("WM_DELETE_WINDOW", self._cerrarVentana)
                    self._sendNotification("Informacion", f"{valores}", icon="tareas")
                    return
                self.frameTareas.after(100, verificar_avanceTareas)
            except queue.Empty:
                self.frameTareas.after(100, verificar_avanceTareas)
        
        def InicioTareas():
            for tarea in self._tareas:
                if tarea["accion"] == "Crear ruta":
                    try:
                        tarea["estado"] = "En progreso"
                        resultado.put((True, "Creando ruta"))
                        crearRuta()
                        tarea["estado"] = "Completado"
                        resultado.put((True, "Ruta creada correctamente"))
                    except NotADirectoryError as de:
                        tarea["estado"] = "Error"
                        resultado.put((False, f"Error en la ruta: {de}"))
                        messagebox.showerror("Ruta invalida", f"Error en la ruta: {de}")
                        return
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al crear la ruta: {e}")
                        tarea["estado"] = "Error"
                        resultado.put((False, f"Error al crear la ruta: {e}"))
                        return
                
                if tarea["accion"] == "Eliminar contenido de la carpeta":
                    if messagebox.askyesno("Advertencia", f"Se eliminara todo el contenido de la carteta actual\n {self._ruta.get()},\n ¿Desea contunuar?"):
                        try:
                            tarea["estado"] = "En progreso"
                            resultado.put((True, "Eliminando contenido de la carpeta"))
                            borrarContenidoDirectorio()
                            tarea["estado"] = "Completado"
                            resultado.put((True, "Contenido eliminado correctamente"))
                        except Exception as e:
                            messagebox.showerror("Error", f"Error al eliminar contenido de la carpeta: {e}")
                            tarea["estado"] = "Error"
                            resultado.put((False, f"Error al eliminar contenido de la carpeta: {e}"))
                            return
                    else:
                        tarea["estado"] = "Error"
                        resultado.put((False, "Operacion cancelada"))
                        return
                
                if tarea["accion"] == "Inicializar proyecto Node":
                    tarea["estado"] = "En progreso"
                    resultado.put((True, "Inicializando proyecto Node"))
                    
                    if InicializarNode() != 0:
                        tarea["estado"] = "Error"
                        resultado.put((False, "Error al inicializar el proyecto Node"))
                        return
                    
                    tarea["estado"] = "Completado"
                    resultado.put((True, "Proyecto Node inicializado correctamente"))
                
                if tarea["accion"].startswith("Instalar modulo"):
                    modulo = tarea["info"]
                    if modulo["usar"] is not None and modulo["usar"].get():
                        tarea["estado"] = "En progreso"
                        resultado.put((True, f"Instalando {modulo['nombre']}-{modulo['version'].get()}"))
                        # Construir los argumentos del comando
                        comando = [
                            self._npm_path,
                            "i"
                        ]
                        
                        if modulo["argumento"].get():
                            #Ejemplo del valor de argumento.get() -> "-S, -D, -O, --no-save, --production, --only=dev, --only=prod"
                            argumentos = " ".join(modulo["argumento"].get().split(", "))
                            comando.append(argumentos)
                        
                        comando.append(f"{modulo['nombre'].lower()}@{modulo['version'].get()}")  # Agregar el nombre del modulo y la version
                        
                        # Ejecutar el comando
                        estado = runCommand(comando, self._ruta.get())
                        if isinstance(estado, subprocess.CalledProcessError):
                            messagebox.showerror("Error", f"Error instalando {modulo['nombre']}: {estado}")
                            tarea["estado"] = "Error"
                            if self.PararEnFalloVar.get():
                                if self.EliminarEnFalloVar.get():
                                    try:
                                        borrarContenidoDirectorio()
                                    except:
                                        pass
                                resultado.put((False, f"Error al instalar {modulo['nombre']}"))
                                return
                            resultado.put((True, f"Error al instalar {modulo['nombre']}"))
                        else:
                            tarea["estado"] = "Completado"
                            resultado.put((True, f"{modulo['nombre']} instalado correctamente"))
                
                if tarea["accion"] == "Crear directorios adicionales":
                    tarea["estado"] = "En progreso"
                    resultado.put((True, "Creando archivos adicionales"))
                    crearDirectorios()
                    tarea["estado"] = "Completado"
                    resultado.put((True, "Archivos adicionales creados correctamente"))
                
                if tarea["accion"] == "Abrir en VS Code":
                    tarea["estado"] = "En progreso"
                    resultado.put((True, "Abriendo en VS Code"))
                    try:
                        runCommand([self._code_path, self._ruta.get()], self._ruta.get())
                        tarea["estado"] = "Completado"
                        resultado.put((True, "Abierto en VS Code correctamente"))
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al abrir en VS Code: {e}")
                        tarea["estado"] = "Error"
                        resultado.put((False, f"Error al abrir en VS Code: {e}"))
                        return
            
            resultado.put((False, "Tareas completadas"))
        
        def Iniciar():
            nonlocal totalTareas
            
            totalTareas = conteo_tareas()
            tareasTotaleslbl.config(text=totalTareas)
            
            self.protocol("WM_DELETE_WINDOW", doNothing)
            threading.Thread(target=InicioTareas).start()
            self.frameTareas.after(100, verificar_avanceTareas)
        
        totalTareas = 0
        taskWidgets = {}
        resultado = queue.Queue()
        
        frameDetalles = ttk.LabelFrame(self.frameTareas, text="Detalles de las tareas", style="info.TLabelframe")
        ttk.Label(frameDetalles, text="Total de tareas a realizar:").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        tareasTotaleslbl = ttk.Label(frameDetalles, text=totalTareas, style="warning.TLabel")
        tareasTotaleslbl.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(frameDetalles, text="Tareas completadas:").grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        tareasCompletadaslbl = ttk.Label(frameDetalles, text="0", style="warning.TLabel")
        tareasCompletadaslbl.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(frameDetalles, text="Tareas pendientes:").grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        tareasPendienteslbl = ttk.Label(frameDetalles, text=totalTareas, style="warning.TLabel")
        tareasPendienteslbl.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(frameDetalles, text="Progreso").grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        progreso = ttk.Progressbar(frameDetalles, length=200, mode="determinate", style="success.Horizontal.TProgressbar")
        progreso.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(frameDetalles, text="Descripcion de la tarea").grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
        entryDescripcion = ttk.Entry(frameDetalles, style="info.TEntry", width=50)
        entryDescripcion.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
        
        frameDetalles.grid_columnconfigure(1, weight=1)
        frameDetalles.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        frameDetalles.update_idletasks()
        
        scrolled_frame = ScrolledFrame(self.frameTareas, "success-rounded")
        scrolled_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        
        self._funcConteoTareas = conteo_tareas
        self._funcInicioTareas = Iniciar
        self.frameTareas.grid_columnconfigure(0, weight=1)
        self.frameTareas.grid_rowconfigure(1, weight=1)
    
    def _configuracionFrame(self):
        def cambiarIdentificacionGit():
            def guardarCambios():
                nonlocal modificado
                if not entryUsuario.get():
                    messagebox.showerror("Error", "El usuario no puede estar vacío")
                    return
                
                if not entryCorreo.get():
                    messagebox.showerror("Error", "El correo no puede estar vacío")
                    return
                
                if edicionGlobal.get():
                    resultado = runCommand([self._git_path, "config", "--global", "user.name", entryUsuario.get()], retornarEn='bytes')
                    if isinstance(resultado, subprocess.CalledProcessError):
                        messagebox.showerror("Error", f"Error al cambiar el usuario de Git: {resultado}")
                        return
                    
                    resultado = runCommand([self._git_path, "config", "--global", "user.email", entryCorreo.get()], retornarEn='bytes')
                    if isinstance(resultado, subprocess.CalledProcessError):
                        messagebox.showerror("Error", f"Error al cambiar el correo de Git: {resultado}")
                        return
                    
                    modificado = True
                    messagebox.showinfo("Información", "Cambios guardados correctamente")
                    onClose()
                    return

                if not self._ruta.get():
                    messagebox.showerror("Error", "La ruta del repositorio no puede estar vacía")
                    return
                
                if not isFolderInPath(".git", self._ruta.get()):
                    messagebox.showerror("Error", "La ruta del repositorio no es un repositorio de Git")
                    return
                
                resultado = runCommand([self._git_path, "config", "user.name", entryUsuario.get()], self._ruta.get(), retornarEn='bytes')
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al cambiar el usuario de Git: {resultado}")
                    return
                
                resultado = runCommand([self._git_path, "config", "user.email", entryCorreo.get()], self._ruta.get(), retornarEn='bytes')
                if isinstance(resultado, subprocess.CalledProcessError):
                    messagebox.showerror("Error", f"Error al cambiar el correo de Git: {resultado}")
                    return
                
                modificado = True
                messagebox.showinfo("Información", "Cambios guardados correctamente")
                onClose()
            
            def validarEntradas():
                if not self._userGit.get() or not self._correoGit.get():
                    btnGuardar.config(state="disabled")
                    return
                
                if self._userGit.get() == userGitTemp and self._correoGit.get() == emailGitTemp:
                    btnGuardar.config(state="disabled")
                    return
                
                if validarEntryRuta:
                    if not self._ruta.get():
                        btnGuardar.config(state="disabled")
                        return
                    
                    if not isFolderInPath(".git", self._ruta.get()):
                        btnGuardar.config(state="disabled")
                        return
                
                btnGuardar.config(state="normal")
                
            def mostrarOcultarFrameRuta():
                nonlocal validarEntryRuta
                if not edicionGlobal.get():
                    validarEntryRuta = True
                    frameRuta.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
                else:
                    validarEntryRuta = False
                    frameRuta.grid_remove()

                validarEntradas()
                centerWindow(popUp, True)
            
            def ChangePath():
                if ruta := filedialog.askdirectory():
                    self._ruta.set(ruta)
                    entryRuta.config(state="normal")
                    entryRuta.delete(0, "end")
                    entryRuta.insert(0, ruta)
                    entryRuta.config(state="readonly")
                    validarEntradas()
            
            def onClose():
                if not modificado:
                    self._userGit.set(userGitTemp)
                    self._correoGit.set(emailGitTemp)
                else:
                    actualizarEntry(entryUserGit, self._userGit.get())
                    actualizarEntry(entryCorreoGit, self._correoGit.get())
                
                popUp.destroy()
            
            popUp = ttk.Toplevel()
            popUp.title("Editar usuario y correo de Git")
            popUp.resizable(False, False)
            popUp.transient(self)
            popUp.protocol("WM_DELETE_WINDOW", onClose)
            
            modificado = False
            userGitTemp = self._userGit.get()
            ttk.Label(popUp, text="Usuario", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            entryUsuario = ttk.Entry(popUp, width=50, textvariable=self._userGit)
            entryUsuario.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            entryUsuario.bind("<FocusOut>", lambda e: validarEntradas())
            
            emailGitTemp = self._correoGit.get()
            ttk.Label(popUp, text="Correo", anchor="center").grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
            entryCorreo = ttk.Entry(popUp, width=50, textvariable=self._correoGit)
            entryCorreo.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
            entryCorreo.bind("<FocusOut>", lambda e: validarEntradas())
            
            frameRuta = ttk.Frame(popUp)
            ttk.Label(frameRuta, text="Ruta del repositorio", anchor="center").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            entryRuta = ttk.Entry(frameRuta, width=50, textvariable=self._ruta)
            entryRuta.config(state="readonly")
            entryRuta.grid(row=1, column=0, padx=5, sticky="nsew")
            
            scrollEntryRuta = ttk.Scrollbar(frameRuta, orient="horizontal", bootstyle="success-round") # type: ignore
            entryRuta.config(xscrollcommand=scrollEntryRuta.set)
            scrollEntryRuta.config(command=entryRuta.xview)
            
            lblmagEntry = ttk.Label(frameRuta, image=self._imagenes["Magnifier"], anchor="center", cursor="hand2")
            tooltipRuta = ToolTip(lblmagEntry, "Seleccionar un directorio distinto")
            lblmagEntry.bind("<Enter>", lambda e: tooltipRuta.showtip("w"))
            lblmagEntry.bind("<Leave>", lambda e: tooltipRuta.hidetip())
            lblmagEntry.bind("<Button-1>", lambda e: ChangePath())
            scrollEntryRuta.grid(row=2, column=0, padx=5, sticky="nsew")
            lblmagEntry.grid(row=1, rowspan=2, column=1, padx=5, pady=5, sticky="nsew")
            
            edicionGlobal = tk.BooleanVar(value=False)
            validarEntryRuta = not edicionGlobal.get()
            chkGlobal = ttk.Checkbutton(popUp, text="Editar globalmente", variable=edicionGlobal, bootstyle="success-round-toggle", command=mostrarOcultarFrameRuta) # type: ignore
            chkGlobal.grid(row=5, column=0, padx=5, pady=5)
            
            btnGuardar = ttk.Button(popUp, text="Guardar cambios", command=guardarCambios, bootstyle=(SUCCESS, OUTLINE)) # type: ignore
            btnGuardar.grid(row=6, column=0, padx=5, pady=5, sticky="nsew")
            
            mostrarOcultarFrameRuta()
            validarEntradas()
            centerWindow(popUp)
        
        def actualizarEntry(entry, valor):
                entry.config(state="normal")
                entry.delete(0, "end")
                entry.insert(0, valor)
                entry.config(state="readonly")
        
        def verArchivos():
            def onClosePopup():
                if modificado:
                    if not messagebox.askyesno("Advertencia", "Hay cambios sin guardar, ¿Desea salir sin guardar?"):
                        return
                
                for widget in scrolled_frame.winfo_children():
                    widget.destroy()
                
                popUp_archivos.destroy()
            
            def onChangeText(nombre_archivo):
                nonlocal modificado
                
                modificado = False
                for archivo, contenido in archivos_p:
                    if archivo == nombre_archivo:
                        contenidoTXT = temporal[archivo].get("1.0", "end").strip() 
                        if contenidoTXT != contenido:
                            modificado = True
                            break
                
                btn_guardarCambios.config(state="normal" if modificado else "disabled")
            
            def guardarCambios():
                nonlocal modificado
                for i in range(len(archivos_p)):
                    nombre_archivo = archivos_p[i][0]
                    contenido_archivo = temporal[nombre_archivo].get("1.0", "end").strip()
                    
                    if contenido_archivo != archivos_p[i][1]:
                        archivos_p[i] = (nombre_archivo, contenido_archivo)
                
                modificado = False
                btn_guardarCambios.config(state="disabled")
            
            popUp_archivos = ttk.Toplevel()
            popUp_archivos.title("Archivos del proyecto")
            popUp_archivos.resizable(False, False)
            popUp_archivos.transient(self)
            popUp_archivos.protocol("WM_DELETE_WINDOW", onClosePopup)
            popUp_archivos.grab_set()
            
            modificado = False
            
            scrolled_frame = ScrolledFrame(popUp_archivos, "success-rounded")
            
            ttk.Label(scrolled_frame, text="Nombre del archivo", anchor="center").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            ttk.Label(scrolled_frame, text="Contenido del archivo", anchor="center").grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            ttk.Separator(scrolled_frame, orient="horizontal", bootstyle="success").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew") # type: ignore
            
            temporal = {}
            for i, (nombre_archivo, contenido_archivo) in enumerate(archivos_p, 2):
                ttk.Label(scrolled_frame, text=nombre_archivo, anchor="center").grid(row=i, column=0, padx=5, sticky="n")
                txt = scrolledtext.ScrolledText(scrolled_frame, height=10)
                txt.insert("1.0", contenido_archivo)
                txt.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
                txt.bind("<KeyRelease>", lambda e, nombre=nombre_archivo: onChangeText(nombre))
                
                temporal[nombre_archivo] = txt
            
            scrolled_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            btn_guardarCambios = ttk.Button(popUp_archivos, text="Guardar cambios", command=guardarCambios, bootstyle=(SUCCESS, OUTLINE)) # type: ignore
            btn_guardarCambios.config(state="disabled")
            btn_guardarCambios.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            
            scrolled_frame.update_idletasks()
            ancho_canvas = scrolled_frame.winfo_reqwidth()
            
            popUp_archivos.geometry(f"{ancho_canvas + 25}x300")
            popUp_archivos.grid_columnconfigure(0, weight=1)
            popUp_archivos.grid_rowconfigure(0, weight=1)
            
            centerWindow(popUp_archivos)
        
        masAccionesFrame = ttk.LabelFrame(self.frameConfiguracion, text="Acciones adicionales para el proyecto", style="info.TLabelframe")
        
        self._checkVars = []
        self._userGit = tk.StringVar()
        self._correoGit = tk.StringVar()
        
        self._funcCambiarIDGit = cambiarIdentificacionGit
        
        if self._git_path:
            self._userGit.set(getGitUser())
            self._correoGit.set(getGitEmail())
        
        mensajesChkBox = [
            ("Crear directorios adicionales", True),
            ("Abrir en VS Code al finalizar", False)
        ]
        
        for i, (mensaje, check) in enumerate(mensajesChkBox):
            var = tk.BooleanVar(value=check)
            chk = ttk.Checkbutton(masAccionesFrame, text=mensaje, variable=var, style="success.TCheckbutton")
            chk.grid(row=i, column=0, padx=5, pady=5, sticky="nsew")
            self._checkVars.append({mensaje: var})
            
        btn_verArchivos = ttk.Button(masAccionesFrame, text="Ver archivos", command=verArchivos, bootstyle=(INFO, OUTLINE)) # type: ignore
        btn_verArchivos.grid(row=i+1, column=0, padx=5, pady=5, sticky="nsew")
        
        self._checkVars[0]["Crear directorios adicionales"].trace_add(
            "write",
            lambda *args: btn_verArchivos.config(state="normal" if self._checkVars[0]["Crear directorios adicionales"].get() else "disabled")
        )
        
        masAccionesFrame.grid_columnconfigure(0, weight=1)
        
        masAccionesFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        pathsFrame = ttk.LabelFrame(self.frameConfiguracion, text="Rutas a ejecutables", style="info.TLabelframe")
        
        ttk.Label(pathsFrame, text="Ruta de Git", style="info.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        entryGitPath = ttk.Entry(pathsFrame, style="info.TEntry", width=50)
        entryGitPath.insert(0, self._git_path if self._git_path else "No disponible")
        entryGitPath.config(state="readonly")
        entryGitPath.grid(row=1, column=0, padx=5, sticky="nsew")
        scrollEntryGit = ttk.Scrollbar(pathsFrame, orient="horizontal", bootstyle="info-round") # type: ignore
        entryGitPath.config(xscrollcommand=scrollEntryGit.set)
        scrollEntryGit.config(command=entryGitPath.xview)
        scrollEntryGit.grid(row=2, column=0, padx=5, sticky="nsew")
        
        lblInfoEntryGit = ttk.Label(pathsFrame, image=self._imagenes["Info"], style="info.TLabel")
        tooltipGit = ToolTip(lblInfoEntryGit, "La ruta de Git es necesaria para realizar las acciones de Git")
        lblInfoEntryGit.bind("<Enter>", lambda e: tooltipGit.showtip("w"))
        lblInfoEntryGit.bind("<Leave>", lambda e: tooltipGit.hidetip())
        lblInfoEntryGit.grid(row=1, rowspan=2, column=1, padx=5, sticky="nsew")
        
        ttk.Label(pathsFrame, text="Ruta de Node", style="info.TLabel").grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        entryNodePath = ttk.Entry(pathsFrame, style="info.TEntry", width=50)
        entryNodePath.insert(0, self._node_path if self._node_path else "No disponible")
        entryNodePath.config(state="readonly")
        entryNodePath.grid(row=4, column=0, padx=5, sticky="nsew")
        scrollEntryNode = ttk.Scrollbar(pathsFrame, orient="horizontal", bootstyle="info-round") # type: ignore
        entryNodePath.config(xscrollcommand=scrollEntryNode.set)
        scrollEntryNode.config(command=entryNodePath.xview)
        scrollEntryNode.grid(row=5, column=0, padx=5, sticky="nsew")
        
        lblInfoEntryNode = ttk.Label(pathsFrame, image=self._imagenes["Info"], style="info.TLabel")
        tooltipNode = ToolTip(lblInfoEntryNode, "La ruta de Node es necesaria para comprobar la version de Node")
        lblInfoEntryNode.bind("<Enter>", lambda e: tooltipNode.showtip("w"))
        lblInfoEntryNode.bind("<Leave>", lambda e: tooltipNode.hidetip())
        lblInfoEntryNode.grid(row=4, rowspan=2, column=1, padx=5, sticky="nsew")
        
        ttk.Label(pathsFrame, text="Ruta de NPM", style="info.TLabel").grid(row=6, column=0, padx=5, pady=5, sticky="nsew")
        entryNPMPath = ttk.Entry(pathsFrame, style="info.TEntry", width=50)
        entryNPMPath.insert(0, self._npm_path if self._npm_path else "No disponible")
        entryNPMPath.config(state="readonly")
        entryNPMPath.grid(row=7, column=0, padx=5, sticky="nsew")
        scrollEntryNPM = ttk.Scrollbar(pathsFrame, orient="horizontal", bootstyle="info-round") # type: ignore
        entryNPMPath.config(xscrollcommand=scrollEntryNPM.set)
        scrollEntryNPM.config(command=entryNPMPath.xview)
        scrollEntryNPM.grid(row=8, column=0, padx=5, sticky="nsew")
        
        lblInfoEntryNPM = ttk.Label(pathsFrame, image=self._imagenes["Info"], style="info.TLabel")
        tooltipNPM = ToolTip(lblInfoEntryNPM, "La ruta de NPM es necesaria para la instalacion de modulos de Node")
        lblInfoEntryNPM.bind("<Enter>", lambda e: tooltipNPM.showtip("w"))
        lblInfoEntryNPM.bind("<Leave>", lambda e: tooltipNPM.hidetip())
        lblInfoEntryNPM.grid(row=7, rowspan=2, column=1, padx=5, sticky="nsew")
        
        ttk.Label(pathsFrame, text="Ruta de VS Code", style="info.TLabel").grid(row=9, column=0, padx=5, pady=5, sticky="nsew")
        entryVSCodePath = ttk.Entry(pathsFrame, style="info.TEntry", width=50)
        entryVSCodePath.insert(0, self._code_path if self._code_path else "No disponible")
        entryVSCodePath.config(state="readonly")
        entryVSCodePath.grid(row=10, column=0, padx=5, sticky="nsew")
        scrollEntryVSCode = ttk.Scrollbar(pathsFrame, orient="horizontal", bootstyle="info-round") # type: ignore
        entryVSCodePath.config(xscrollcommand=scrollEntryVSCode.set)
        scrollEntryVSCode.config(command=entryVSCodePath.xview)
        scrollEntryVSCode.grid(row=11, column=0, padx=5, sticky="nsew")
        
        lblInfoEntryVSCode = ttk.Label(pathsFrame, image=self._imagenes["Info"], style="info.TLabel")
        tooltipVSCode = ToolTip(lblInfoEntryVSCode, "La ruta de VS Code es necesaria para abrir el proyecto en VS Code cuando se acabe de crear")
        lblInfoEntryVSCode.bind("<Enter>", lambda e: tooltipVSCode.showtip("w"))
        lblInfoEntryVSCode.bind("<Leave>", lambda e: tooltipVSCode.hidetip())
        lblInfoEntryVSCode.grid(row=10, rowspan=2, column=1, padx=5, sticky="nsew")
        
        pathsFrame.grid_columnconfigure(0, weight=1)
        
        pathsFrame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        optionsFrame = ttk.LabelFrame(self.frameConfiguracion, text="Opciones", style="info.TLabelframe")
        
        self._recargaModulos = ttk.BooleanVar(value=False)
        chkRecargarModulos = ttk.Checkbutton(optionsFrame, text="Obtener modulos instalados", variable=self._recargaModulos, style="success.TCheckbutton")
        chkRecargarModulos.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        lblInfoRecargaM = ttk.Label(optionsFrame, image=self._imagenes["Info"], anchor="center")
        tooltipRecargaM = ToolTip(lblInfoRecargaM, "Obtener modulos intalados: Recarga los modulos de Node al cambiar de directorio y selecciona aquellos que esten instalados")
        lblInfoRecargaM.bind("<Enter>", lambda e: tooltipRecargaM.showtip("w"))
        lblInfoRecargaM.bind("<Leave>", lambda e: tooltipRecargaM.hidetip())
        lblInfoRecargaM.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        optionsFrame.grid_columnconfigure(0, weight=1)
        optionsFrame.grid(row=1, column=0, columnspan=2 if not self._git_path else 1, padx=5, pady=5, sticky="nsew")
        
        if self._git_path:
            gitConfigFrame = ttk.LabelFrame(self.frameConfiguracion, text="Configuracion de Git", style="info.TLabelframe")
            ttk.Label(gitConfigFrame, text="Usuario de Git", style="info.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            entryUserGit = ttk.Entry(gitConfigFrame, style="info.TEntry", width=50)
            entryUserGit.insert(0, self._userGit.get())
            entryUserGit.config(state="readonly")
            entryUserGit.grid(row=1, column=0, padx=5, sticky="nsew")
            
            lblinfoUserEntry = ttk.Label(gitConfigFrame, image=self._imagenes["User"], style="info.TLabel")
            tooltipUser = ToolTip(lblinfoUserEntry, "El usuario de Git con el que se realizaran las acciones de Git")
            lblinfoUserEntry.bind("<Enter>", lambda e: tooltipUser.showtip("w"))
            lblinfoUserEntry.bind("<Leave>", lambda e: tooltipUser.hidetip())
            lblinfoUserEntry.grid(row=1, column=1, padx=5, sticky="nsew")
            
            ttk.Label(gitConfigFrame, text="Correo de Git", style="info.TLabel").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
            entryCorreoGit = ttk.Entry(gitConfigFrame, style="info.TEntry", width=50)
            entryCorreoGit.insert(0, self._correoGit.get())
            entryCorreoGit.config(state="readonly")
            entryCorreoGit.grid(row=3, column=0, padx=5, sticky="nsew")
            
            lblinfoCorreoEntry = ttk.Label(gitConfigFrame, image=self._imagenes["Mail"], style="info.TLabel")
            tooltipCorreo = ToolTip(lblinfoCorreoEntry, "El correo de Git con el que se realizaran las acciones de Git")
            lblinfoCorreoEntry.bind("<Enter>", lambda e: tooltipCorreo.showtip("w"))
            lblinfoCorreoEntry.bind("<Leave>", lambda e: tooltipCorreo.hidetip())
            lblinfoCorreoEntry.grid(row=3, column=1, padx=5, sticky="nsew")
            
            btnGuardar = ttk.Button(gitConfigFrame, text="Cambiar", command=cambiarIdentificacionGit, bootstyle=(WARNING, OUTLINE)) # type: ignore
            btnGuardar.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
            gitConfigFrame.grid_columnconfigure(0, weight=1)
            gitConfigFrame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    
        columnas, filas = self.frameConfiguracion.grid_size()
        for columna in range(columnas):
            self.frameConfiguracion.grid_columnconfigure(columna, weight=1)
        
        for fila in range(filas):
            self.frameConfiguracion.grid_rowconfigure(fila, weight=1)
    
    def _cerrarVentana(self, ventana:tk.Tk | tk.Toplevel | None = None):
        if not ventana:
            ventana = self
            
        #? Aqui se cancela cuanquier After programado en la ventana principal
        
        for widget in ventana.winfo_children():
            widget.destroy()
        
        ventana.destroy()
    
    def _loadImages(self):
        # Iconos para Frames
        self._imagenes["principal"] = loadImageTk((os.path.join(ruta_assets, "homeIcon.png")), 50, 50)
        self._imagenes["modulos"] = loadImageTk((os.path.join(ruta_assets, "downloadsIcon.png")), 50, 50)
        self._imagenes["git"] = loadImageTk((os.path.join(ruta_assets, "codeForkIcon.png")), 50, 50)
        self._imagenes["tareas"] = loadImageTk((os.path.join(ruta_assets, "checkboxIcon.png")), 50, 50)
        self._imagenes["configuracion"] = loadImageTk((os.path.join(ruta_assets, "cogIcon.png")), 50, 50)
        
        # Iconos para tareas
        self._imagenes["Pending"] = loadImageTk((os.path.join(ruta_assets, "timerIcon.png")), 20, 20)
        self._imagenes["Running"] = loadImageTk((os.path.join(ruta_assets, "playIcon.png")), 20, 20)
        self._imagenes["Check"] = loadImageTk((os.path.join(ruta_assets, "checkIcon.png")), 20, 20)
        self._imagenes["Error"] = loadImageTk((os.path.join(ruta_assets, "errorIcon.png")), 20, 20)
        
        # Iconos adicionales
        self._imagenes["Magnifier"] = loadImageTk((os.path.join(ruta_assets, "magnifierIcon.png")), 20, 20)
        self._imagenes["Warning"] = loadImageTk((os.path.join(ruta_assets, "warningIcon.png")), 20, 20)
        self._imagenes["Info"] = loadImageTk((os.path.join(ruta_assets, "infoIcon.png")), 20, 20)
        self._imagenes["Add"] = loadImageTk((os.path.join(ruta_assets, "addIcon.png")), 20, 20)
        self._imagenes["Minus"] = loadImageTk((os.path.join(ruta_assets, "minusIcon.png")), 20, 20)
        self._imagenes["Trash"] = loadImageTk((os.path.join(ruta_assets, "trashIcon.png")), 20, 20)
        self._imagenes["User"] = loadImageTk((os.path.join(ruta_assets, "userIcon.png")), 20, 20)
        self._imagenes["Mail"] = loadImageTk((os.path.join(ruta_assets, "mailIcon.png")), 20, 20)
        self._imagenes["Edit"] = loadImageTk((os.path.join(ruta_assets, "editIcon.png")), 20, 20)
        self._imagenes["Link"] = loadImageTk((os.path.join(ruta_assets, "linkIcon.png")), 20, 20)
        self._imagenes["Prompt"] = loadImageTk((os.path.join(ruta_assets, "promptIcon.png")), 20, 20)
    
    def mostrar_imagenes(self):
        self.Principal.config(image=self._imagenes["principal"], anchor="center", compound="top")
        self.Modulos.config(image=self._imagenes["modulos"], anchor="center", compound="top")
        self.Git.config(image=self._imagenes["git"], anchor="center", compound="top")
        self.Tareas.config(image=self._imagenes["tareas"], anchor="center", compound="top")
        self.Configuracion.config(image=self._imagenes["configuracion"], anchor="center", compound="top")
    
    def _centrar_ventana(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
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

def dividir_lista(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

if __name__ == "__main__":
    #app = NodeSetupApp()
    app = NodeSetupAppNew()
    app.mostrar_imagenes()
    app._centrar_ventana()
    app.Iniciar()