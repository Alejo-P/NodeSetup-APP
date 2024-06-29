import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import subprocess
import time
import ast

from typing import List, Literal
from VarSettings import listaArgumentos, carpetas, archivos, archivos_p, lista_modulosNPM
from version import __version__ as appVersion

class ConfigurarEntornoNode(tk.Tk):
    
    def __init__(self):
        self._version = Verificar_version("node")
        self._veri_code = Obtener_ruta_de("code")
        self._npm_path = Obtener_ruta_de("npm")
        self._version_NPM = None
        
        if self._version is None:
            messagebox.showerror("Error", "Node.js no está instalado en el sistema")
            quit()
            
        super().__init__()
        
        def Cerrar_ventana():
            if self._idAfterBar:
                self.after_cancel(self._idAfterBar)
                self._idAfterBar = None
            
            self.cerrar_ventana()

        self.title("NodeSetup")
        self.resizable(0, 0)  # type: ignore
        self.protocol("WM_DELETE_WINDOW", lambda: Cerrar_ventana())
        
        style = ttk.Style(self)
        style.theme_use('clam')
        self.configure(bg="lightgray")
       
        # Personalizar la barra de progreso
        style.configure("TProgressbar",
            troughcolor='#D3D3D3',  # Color del fondo del canal
            background='#4CAF50',  # Color del progreso
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
        
        self._idAfterBar = "Temporal"
        self._idAfterBar2 = None
        self.frameInfo = ttk.LabelFrame(self, width=100, text="Informacion:")
        self.lbl_titulo = ttk.Label(self)
        self.lbl_versionApp = ttk.Label(self.frameInfo)
        self.lbl_version = ttk.Label(self.frameInfo)
        self.lbl_versionNPM = ttk.Label(self.frameInfo)
        self._lbl_ruta = ttk.Label(self, text="Ruta", width=50)
        self.entry_ruta = ttk.Entry(self)
        self.entry_ruta.bind(
            "<Return>",
            lambda event: self.iniciar_creacion_proyecto()
        )
        self.boton_ruta = ttk.Button(self, text="Explorar", command=self.abrir_ruta, width=50)
        self.frm_check = ttk.Labelframe(self, width=50, text="Opciones")
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
        
        self.crear_widgets()
        self._centrar_ventana()
    
    def crear_widgets(self):
        def cargarinfo_versionNPM():
            self.lbl_versionNPM.config(text="Version de NPM: Cargando...")
            
            versionNPM = Ejecutar_comando([self._npm_path, "-v"])
            if isinstance(versionNPM, subprocess.CalledProcessError):
                messagebox.showerror("Error", f"Error al obtener la version de NPM: {versionNPM}")
                self.lbl_versionNPM.config(text="Version de NPM: Error")
            else:
                self.lbl_versionNPM.config(text=f"Version de NPM: {versionNPM.stdout.strip()}")
            
            versiones_paquetesNPM = Ejecutar_comando([self._npm_path, "show", "npm", "versions", "--depth=0"])
            lista_versionesNPM = list(ast.literal_eval(f"{versiones_paquetesNPM.stdout.strip()}"))
            
            if versionNPM.stdout.strip() < lista_versionesNPM[-1]:
                messagebox.showinfo("Debe actualizar NPM", f"Se encontro una nueva version de NPM:\nTiene la version: {versionNPM.stdout.strip()}\nSe encontro la version: {lista_versionesNPM[-1]}")
            self.update_idletasks()
        
        def ventana_seleccionModulos():
            def incrementar_progreso(progreso:ttk.Progressbar, incremento:int | float, objetivo:int | float, delay:int=30):
                if self._idAfterBar2:
                    if progreso['value'] < objetivo:
                        progreso['value'] += incremento
                        self._idAfterBar2 = modulos.after(delay, incrementar_progreso, progreso, incremento, objetivo, delay)
                    else:
                        progreso['value'] = objetivo
            
            def actualizar_progreso_subbarra(progreso:ttk.Progressbar ,pasos_completados:int | float):
                objetivo = pasos_completados / (len(lista_modulosNPM)-1) * 100
                incremento = 1
                incrementar_progreso(progreso, incremento, objetivo, 80)
                self.update_idletasks()
            
            def restablecer_seleccion():
                for dic in lista_modulosNPM:
                    dic["usar"].set(False)
                    dic["global"].set(False)
                    dic["argumento"].set("")
                    dic["version"].set(dic["versiones"][-1] if dic["versiones"] else "Ocurrio un Error")
            
            def update_modulos_ui(lista_modulosNPM, npm_path, msg_estado, progress_bar, modulos:tk.Toplevel):
                lista_widgets= []

                for i, dic in enumerate(lista_modulosNPM, 1):
                        msg_estado.config(text=f"Cargando info del modulo {dic["nombre"]}")
                        if not dic["versiones"]:
                            versionesPaquetes = Ejecutar_comando([npm_path, "show", dic["nombre"].lower(), "versions", "--depth=0"])
                            if isinstance(versionesPaquetes, subprocess.CalledProcessError):
                                messagebox.showerror("Error", f"Error al obtener versiones de {dic['nombre']}: {versionesPaquetes}")
                                if modulos.winfo_exists():
                                    lista_widgets.clear()
                                    break
                            dic["versiones"] = list(ast.literal_eval(f"{versionesPaquetes.stdout.strip()}"))
                        
                        if not dic["usar"]:
                            dic["usar"] = tk.BooleanVar(value=False)
                        if not dic["global"]:
                            dic["global"] = tk.BooleanVar(value=False)
                        if not dic["argumento"]:
                            dic["argumento"] = tk.StringVar(value=listaArgumentos[0])
                        if not dic["version"]:
                            dic["version"] = tk.StringVar(value= dic["versiones"][-1] if dic["versiones"] else "Ocurrio un Error")
                        if modulos.winfo_exists():
                            lista_widgets.append([ttk.Checkbutton(modulos, variable=dic["usar"]),
                                                ttk.Label(modulos, text=dic["nombre"]),
                                                ttk.Combobox(modulos, textvariable=dic["argumento"], values=tuple(listaArgumentos), state="readonly"),
                                                ttk.Combobox(modulos, textvariable=dic["version"], values=dic["versiones"], state="readonly"),
                                                ttk.Checkbutton(modulos, variable=dic["global"])])
                        else:
                            lista_widgets.clear()
                            break
                        # Actualizar la barra de progreso
                        if self._idAfterBar:
                            actualizar_progreso_subbarra(progress_bar, i)
                if progress_bar.winfo_exists() and msg_estado.winfo_exists():  
                    # Ocultar la barra y el mensaje de estado cuando termine
                    progress_bar.grid_forget()
                    msg_estado.grid_forget()
                
                for i, widget_list in enumerate(lista_widgets, 2):
                    for j, widget in enumerate(widget_list):
                        if isinstance(widget, (ttk.Checkbutton, ttk.Entry, ttk.Combobox)):
                            widget.grid(row=i, column=j%len(encabezado_tabla), padx=5, pady=2)
                        elif isinstance(widget, ttk.Label):
                            widget.grid(row=i, column=j%len(encabezado_tabla), padx=5, pady=2, sticky="w")
                
                if modulos.winfo_exists():
                    frame_botones = ttk.Frame(modulos, width=100)
                    frame_botones.grid(row=i+1, column=0, columnspan=len(encabezado_tabla), pady=5, sticky="nsew")
                    
                    frame_botones.grid_columnconfigure(0, weight=1)
                    frame_botones.grid_columnconfigure(1, weight=1)
                        
                    ttk.Button(frame_botones, text="Guardar", command=lambda: self.cerrar_ventana(modulos)).grid(row=0, column=0, padx=10, sticky="nsew")
                    ttk.Button(frame_botones, text="Restablecer", command=restablecer_seleccion).grid(row=0, column=1, padx=10, sticky="nsew")
                    
                    self._centrar_ventana(modulos, True)
                del lista_widgets, msg_estado
            
            def Cerrar_ventana():
                if self._idAfterBar2:
                    modulos.after_cancel(self._idAfterBar2)
                    self._idAfterBar2 = None
                
                self.cerrar_ventana(modulos)
            
            modulos = tk.Toplevel(self)
            modulos.title("Escoje los modulos a instalar")
            modulos.resizable(0, 0) #type:ignore
            modulos.protocol("WM_DELETE_WINDOW", lambda: Cerrar_ventana())
            modulos.transient(self)
            self._idAfterBar2 = "temporal"
            
            encabezado_tabla = [
                "Seleccionar",
                "Nombre del modulo",
                "Argumento",
                "Versión",
                "Inst. Global"
            ]
            
            for i, texto in enumerate(encabezado_tabla):
                ttk.Label(modulos, text=texto).grid(row=0, column=i, padx=5, pady=2)
            
            # Añadir un separador horizontal a la ventana
            ttk.Separator(modulos, orient="horizontal").grid(row=1, column=0, columnspan=len(encabezado_tabla), sticky="ew")
            
            # Añadir una barra de progreso
            progress_bar = ttk.Progressbar(modulos, orient='horizontal', mode='determinate', length=280, style="TProgressbar")
            progress_bar.grid(row=2, column=0, columnspan=len(encabezado_tabla), padx=5, pady=10)
            msg_estado = ttk.Label(modulos)
            msg_estado.grid(row=3, column=0, columnspan=len(encabezado_tabla), padx=5, pady=2)
            
            self._centrar_ventana(modulos)
            
            threading.Thread(target=update_modulos_ui, args=(lista_modulosNPM, self._npm_path, msg_estado, progress_bar, modulos)).start()
        
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
        
        for i, item in enumerate(opciones, 1):
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
                return
        
        self.progreso['value'] = 0
        
        def Iniciar_npm():
            try:
                actualizar_progreso("Inicializando proyecto Node")
                # Ejecutar `npm init -y` para inicializar el proyecto
                estado = Ejecutar_comando([self._npm_path, "init", "-y"], self.entry_ruta.get())
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
                return int(-1)
                
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
                    estado = Ejecutar_comando(comando, self.entry_ruta.get())
                    
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
                    pass
            
            self.lock_unlock_widgets(estado="normal")
            actualizar_progreso("Completado", True)
            messagebox.showinfo("Informacion", "Proyecto creado con éxito")
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
            ventana = self
        
        for item in ventana.winfo_children():
            item.destroy()
        ventana.destroy()

    def Iniciar(self):
        self.mainloop()

def Verificar_version(de:str):
    comando = [de, "-v"]
    estado = Ejecutar_comando(comando)
    if isinstance(estado, subprocess.CalledProcessError):
        return None
    return estado.stdout.strip()

def obtener_version_paquete_npm(ruta_a_npm: str, paquete: str | None = None):
    comando = [ruta_a_npm,"list"]
    if paquete:
        comando.append(paquete)
    
    comando.append("--depth=0") # Solo mostrar los paquetes de primer nivel
    resultado = Ejecutar_comando(comando)
    if isinstance(resultado, subprocess.CalledProcessError):
        return None
    lineas = resultado.stdout.splitlines()
    for linea in lineas:
        ce = linea.find(' ')
        if ce != -1:
            paqueteB = linea[ce+1:]
        else:
            paqueteB = linea
        
        if '@' in paqueteB:
            version = paqueteB.split('@')[1].strip()
            return version
    return None

def Obtener_ruta_de(elemento_ejecutable:str):
    try:
        resultado = subprocess.run(
            ["where", elemento_ejecutable],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0   # Evita que se abra una ventana de consola
            )
        ruta_code = resultado.stdout.strip().split('\n')[1]
        return ruta_code
    except subprocess.CalledProcessError:
        return ""

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

def Ejecutar_comando(comando:List[str], directorio:str = os.getcwd()):
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            cwd=directorio,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0   # Evita que se abra una ventana de consola
            )
        return resultado
    except subprocess.CalledProcessError as e:
        return e

if __name__ == "__main__":
    app = ConfigurarEntornoNode()
    app.Iniciar()