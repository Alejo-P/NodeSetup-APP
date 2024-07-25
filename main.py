import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import subprocess
import time
import ast
from tkinter.scrolledtext import ScrolledText
from turtle import st
from typing import Literal
from Actions import (
    doNothing,
    preventCloseWindow,
    getEvents,
    getVersionOf,
    setEvent,
    writeLog,
    getPathOf,
    runCommand,
    loadImageTk
)
from Vars import listaArgumentos, carpetas, archivos, archivos_p, lista_modulosNPM, Registro_hilos
from version import __version__ as appVersion

class ConfigurarEntornoNode(tk.Tk):
    def __init__(self):
        self._version = getVersionOf("node")
        self._versionGit = getVersionOf("git")
        self._veri_code = getPathOf("code")
        self._npm_path = getPathOf("npm")
        self._git_path = getPathOf("git")
        self._referencias = {}
        self._lista_widgets= []
        self._version_NPM = None
        
        if self._version is None:
            messagebox.showerror("Error", "Node.js no está instalado en el sistema")
            quit()
        
        super().__init__()

        self.title("NodeSetup")
        self.resizable(0, 0)  # type: ignore
        self.protocol("WM_DELETE_WINDOW", lambda: preventCloseWindow("Accion no permitida", "No puede cerrar esta ventana, hay tareas que requieren usarla", "WARNING"))
        
        style = ttk.Style(self)
       
        # Personalizar la barra de progreso
        style.configure("TProgressbar",
            troughcolor='#5A5A5A',  # Color del fondo del canal
            background='#FA8C75',  # Color del progreso
            bordercolor='#FA8C75',  # Color del borde
            thickness=20,  # Grosor de la barra de progreso
        )
        
        style.configure("Custom.TCheckbutton",
                        font=("Arial", 10),
                        foreground="grey",
                        relief="raised",
                        padding=5,
                        )
        
        style.map("Custom.TCheckbutton",
                  foreground=[('active', 'black'), ('disabled', 'gray')],
                  background=[('active', 'lightgrey')],
                  relief=[('pressed', 'sunken')])
        
        self._checkVars = []
        self._imagenes = {}
        self._ruta = tk.StringVar()
        self._cambiarDirectorio = tk.BooleanVar(value=False)
        
        self._idAfterBar = "Temporal"
        self.frameInfo = ttk.LabelFrame(self, width=100, text="Informacion:")
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
        self.boton_ruta = ttk.Button(self, text="Explorar", command=self.abrir_ruta, width=50)
        self.frm_check = ttk.Labelframe(self, width=50, text="Opciones")
        self.labelGit = ttk.Label(self.frm_check, cursor="hand2")
        self.labelGit.bind(
            "<Button-1>",
            lambda event: self._ventanaOpcionesGit()
        )
        self.sec_botones = ttk.Frame(self)
        self.btn_crear = ttk.Button(self.sec_botones, text="Crear", command=self.iniciar_creacion_proyecto)
        self.btn_salir = ttk.Button(self.sec_botones, text="Salir", command=self.cerrar_ventana)
        
        self._crearRuta = tk.BooleanVar(value=True)
        self._chk_Ruta = ttk.Checkbutton(self, text="Crear ruta si no existe", variable=self._crearRuta, style="Custom.TCheckbutton")
        
        self._eliminarContenido = tk.BooleanVar(value=True)
        self._chk_eliminarPrimero = ttk.Checkbutton(self, text="Eliminar todo el contenido de la carpeta", variable=self._eliminarContenido, style="Custom.TCheckbutton")
        
        self._eliminarDatos = tk.BooleanVar(value=False)
        self._chk_eliminarEnFallo = ttk.Checkbutton(self, text="Eliminar contenido tras un fallo", variable=self._eliminarDatos, style="Custom.TCheckbutton")
        
        self._pararEnFallo = tk.BooleanVar(value=False)
        self._chk_fallo = ttk.Checkbutton(self, text="Detener en caso de fallo", variable=self._pararEnFallo, style="Custom.TCheckbutton")
        
        self.frm_progreso = ttk.Labelframe(self, text="Progreso:", width=100)
        self.lbl_progreso = ttk.Label(self.frm_progreso, text="Descripcion: Ninguna tarea en ejecucion")
        self.frm_progreso.grid_columnconfigure(0, weight=1)
        self.progreso = ttk.Progressbar(self.frm_progreso, orient='horizontal', mode='determinate', style="TProgressbar")
        
        self.completado = tk.BooleanVar(value=False)
        
        self.frm_estadoEv = ttk.LabelFrame(self, text="Registro de eventos", width=100)
        self.textArea = ScrolledText(self.frm_estadoEv, wrap=tk.WORD, width=50, height=15, font=('Arial', 8))
        self.textArea.pack(expand=True, fill=tk.BOTH)
        
        self.repoURL = tk.StringVar()
        
        
        self._almacenar_imagenes()
        self.crear_widgets()
    
    def _almacenar_imagenes(self):
        # Cargar la imagen y guardarla en el diccionario
        self._imagenes["Git"] = loadImageTk("assets/gitIcon.png", 25, 25)
    
    def mostrar_imagenes(self):
        try:
            self.labelGit.config(image=self._imagenes["Git"], text="Git", compound=tk.LEFT)
        except Exception as e:
            print(f"Error al cargar las imagenes: {e}")
    
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
            if os.path.isdir(self._ruta.get()):
                rutacarpetaGIT = os.path.join(self._ruta.get(), ".git")
                if not os.path.isdir(rutacarpetaGIT):
                    mensajeRepo.config(text="No se encontro un repositorio Git", foreground="orange")
                    botonOK.config(state="disabled")
                    ecommit.config(state="disabled")
                    combo.config(state="disabled")
                    return
                
                mensajeRepo.config(text="Repositorio Git encontrado", foreground="green")
                botonOK.config(state="normal")
                ecommit.config(state="normal")
                combo.config(state="readonly")
            else:
                mensajeRepo.config(text="La ruta no es un directorio", foreground="red")
                botonOK.config(state="disabled")
                ecommit.config(state="disabled")
                combo.config(state="disabled")
        
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
        
        frame_version = ttk.LabelFrame(ventana, text="Información de Git")
        ttk.Label(frame_version, text="Version de Git:").grid(row=0, column=0)
        ttk.Label(frame_version, text=self._versionGit if self._versionGit else "").grid(row=0, column=1)
        frame_version.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        notebook = ttk.Notebook(ventana)
        mensajeCommit = tk.StringVar()
        
        frameClonacion = ttk.Frame(notebook)
        frameClonacion.grid_columnconfigure(0, weight=1)
        
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
        
        ttk.Label(frameConfirmacion, text="Ruta del repositorio").grid(row=0, column=0, columnspan=2)
        eruta = ttk.Entry(frameConfirmacion, width=50, textvariable=self._ruta)
        eruta.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        mensajeRepo = ttk.Label(frameConfirmacion)
        mensajeRepo.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Label(frameConfirmacion, text="Mensaje de confirmacion").grid(row=3, column=0, columnspan=2)
        ecommit = ttk.Entry(frameConfirmacion, textvariable=mensajeCommit, width=50)
        ecommit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        opciones = ["Confirmar", "Confirmar y enviar"]
        ttk.Label(frameConfirmacion, text="Opciones").grid(row=5, column=0)
        combo = ttk.Combobox(frameConfirmacion, values=opciones, state="readonly")
        combo.current(0)
        combo.grid(row=5, column=1, padx=5, pady=5)
        
        #TODO: Agregar funcionalidad a los botones y continuar con la implementación
        #! Falta agregar la funcionalidad a los botones
        #! Continuar con la funcion de realizar commits y push
        
        botonOK = ttk.Button(frameConfirmacion, text="OK", command=lambda: doNothing())
        botonOK.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        
        notebook.add(frameClonacion, text="Clonar repositorio")
        notebook.add(frameConfirmacion, text="Confirmar cambios")
        
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
        
        def ventana_seleccionModulos():
            def restablecer_seleccion():
                for dic in lista_modulosNPM:
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
                            check_usar = ttk.Checkbutton(modulos, variable=dic["usar"], style="Custom.TCheckbutton")
                            label_nombre = ttk.Label(modulos, text=dic["nombre"])
                            entry_argumento = ttk.Combobox(modulos, values=listaArgumentos, textvariable=dic["argumento"], state="readonly")
                            combo_version = ttk.Combobox(modulos, values=dic["versiones"], textvariable=dic["version"], state="readonly")
                            check_global = ttk.Checkbutton(modulos, variable=dic["global"], style="Custom.TCheckbutton")

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
                        for sublistas in dividir_lista(lista_modulosNPM, n_listas):
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

                    CrearWidgets(lista_modulosNPM)
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
        
        ttk.Button(self.frm_check, text="Instalar modulos", command=ventana_seleccionModulos).grid(column=0, row=0, sticky="nsew")
        
        start = 1
        if self._versionGit:
            self.labelGit.grid(column=0, row=start)
            start +=1
        
        for i, item in enumerate(opciones, start):
            check_var = tk.BooleanVar(value=False)
            self._checkVars.append({item: check_var})
            if item == "Abrir en VS Code\nal finalizar":
                if self._veri_code:
                    ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="normal").grid(column=0, row=i, sticky="nsew")
                else:
                    ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="disabled").grid(column=0, row=i, sticky="nsew")
            else:   
                ttk.Checkbutton(self.frm_check, text=item, variable=check_var, style="Custom.TCheckbutton", state="normal").grid(column=0, row=i, sticky="nsew")
        
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
            for dic in lista_modulosNPM:
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
        
        threading.Thread(target=ActualizarScrolledText, args=(self.textArea, self, self.completado)).start()
              
        if Iniciar_npm() == 0:
            for modulo in lista_modulosNPM:
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
    app = ConfigurarEntornoNode()
    app.mostrar_imagenes()
    app._centrar_ventana()
    app.Iniciar()