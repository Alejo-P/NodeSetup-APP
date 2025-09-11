import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, SUCCESS, DANGER, OUTLINE, CENTER, LEFT, EW, NSEW
from Tools import ToolTip
from config.constants import APP_VERSION
from utils.icons import Icons

class PrincipalView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self._setup_view()
        self._create_widgets()
        
        for columna in range(self.grid_size()[0]):
            self.grid_columnconfigure(columna, weight=1)

    def _setup_view(self):
        self._versionNPM = tk.StringVar()
        self._versionNode = tk.StringVar()
        self._after_id = None

    def _create_widgets(self):
        # Frame Informacion
        self.frame_info = ttk.LabelFrame(self, text="Información")
        ttk.Label(self.frame_info, text="Version de la app:", anchor=CENTER).grid(row=0, column=0, padx=5, pady=5, sticky=EW)
        entryAppV = ttk.Entry(self.frame_info)
        entryAppV.insert(0, APP_VERSION)
        entryAppV.config(state="readonly", justify=CENTER)
        entryAppV.grid(row=1, column=0, pady=5, padx=5, sticky=EW)

        ttk.Label(self.frame_info, text="Version de Node.js:", anchor=CENTER).grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        entryNodeV = ttk.Entry(self.frame_info, textvariable=self._versionNode)
        entryNodeV.config(state="readonly", justify=CENTER)
        entryNodeV.grid(row=1, column=1, pady=5, padx=5, sticky=EW)

        ttk.Label(self.frame_info, text="Version de NPM:", anchor=CENTER).grid(row=0, column=2, padx=5, pady=5, sticky=EW)
        entryNpmV = ttk.Entry(self.frame_info, textvariable=self._versionNPM)
        entryNpmV.config(state="readonly", justify=CENTER)
        entryNpmV.grid(row=1, column=2, pady=5, padx=5, sticky=EW)

        columnas, filas = self.frame_info.grid_size()
        for columna in range(columnas):
            self.frame_info.grid_columnconfigure(columna, weight=1)

        for fila in range(filas):
            self.frame_info.grid_rowconfigure(fila, weight=1)

        self.frame_info.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)


        self.frame_directorio = ttk.Frame(self)
        self.frame_directorio.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)
        
        ttk.Label(self.frame_directorio, text="Directorio del proyecto", anchor=CENTER).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # Entry ruta con scroll
        self.entryRuta = ttk.Entry(self.frame_directorio, style="Custom.TEntry", width=50)
        self.entryRuta.config(font=Font(family="Consolas", size=10))
        scroll = ttk.Scrollbar(self.frame_directorio, orient="horizontal", command=self.entryRuta.xview, bootstyle="info-round") # type: ignore
        self.entryRuta.config(xscrollcommand=scroll.set)

        self.entryRuta.grid(row=1, column=0, padx=5, sticky=NSEW)
        scroll.grid(row=2, column=0, padx=5, sticky=NSEW)

        # Botón seleccionar
        self.btnSeleccionar = ttk.Label(self.frame_directorio, image=Icons.magnifier_icon, anchor=CENTER, cursor="hand2") # type: ignore
        self.btnSeleccionar.grid(row=1, rowspan=2, column=1, padx=5, sticky=NSEW, pady=5)
        self.tooltipSeleccionar = ToolTip(self.btnSeleccionar, text="Seleccionar directorio", position="w", delay_hide=6000)

        self.frame_directorio.grid_columnconfigure(0, weight=1)
        for fila in range(self.frame_directorio.grid_size()[1]):
            self.frame_directorio.grid_rowconfigure(fila, weight=1)

        self.frame_opciones = ttk.LabelFrame(self, text="Opciones")
        self.frame_opciones.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)

        self.check_delete_content = ttk.Checkbutton(self.frame_opciones, text="Eliminar contenido del directorio", bootstyle="warning-round-toggle") # type: ignore
        self.check_delete_content.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._tooltipDeleteContent = ToolTip(self.check_delete_content, text="Si el directorio ya existe, eliminará todo su contenido antes de crear el proyecto", position="s", delay_hide=6000)

        self.check_create_path = ttk.Checkbutton(self.frame_opciones, text="Crear directorio si no existe", bootstyle="warning-round-toggle") # type: ignore
        self.check_create_path.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._tooltipCreatePath = ToolTip(self.check_create_path, text="Si el directorio no existe, lo creará automáticamente", position="s", delay_hide=6000)

        self.check_delete_on_fail = ttk.Checkbutton(self.frame_opciones, text="Eliminar progreso en caso de fallo", bootstyle="warning-round-toggle") # type: ignore
        self.check_delete_on_fail.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._tooltipDeleteOnFail = ToolTip(self.check_delete_on_fail, text="Si ocurre un error durante la creación del proyecto, eliminará todo lo que se haya creado", position="s", delay_hide=6000)

        self._check_stop_on_fail = ttk.Checkbutton(self.frame_opciones, text="Parar en caso de fallo", bootstyle="warning-round-toggle") # type: ignore
        self._check_stop_on_fail.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self._tooltipStopOnFail = ToolTip(self._check_stop_on_fail, text="Si ocurre un error durante la creación del proyecto, detendrá el proceso inmediatamente", position="s", delay_hide=6000)
        
        for columna in range(self.frame_opciones.grid_size()[0]):
            self.frame_opciones.grid_columnconfigure(columna, weight=1)

        # Botones inferiores
        self.frameBotones = ttk.Frame(self)
        self.frameBotones.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)

        self.btnIrModulos = ttk.Button(self.frameBotones, text="Selección de módulos", state="disabled", bootstyle=(INFO, OUTLINE)) # type: ignore
        self.btnProceder = ttk.Button(self.frameBotones, text="Crear el proyecto", state="disabled", bootstyle=(SUCCESS, OUTLINE)) # type: ignore
        self.btnSalir = ttk.Button(self.frameBotones, text="Salir", bootstyle=(DANGER, OUTLINE)) # type: ignore

        self.btnIrModulos.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.btnProceder.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        self.btnSalir.grid(row=1, column=1, padx=5, pady=5, sticky=NSEW)

        columnas, filas = self.frameBotones.grid_size()
        for columna in range(columnas):
            self.frameBotones.grid_columnconfigure(columna, weight=1)

        for fila in range(filas):
            self.frameBotones.grid_rowconfigure(fila, weight=1)
            
        self.label_mensaje = ttk.Label(self, text="", anchor=CENTER, foreground="red")
        self.label_mensaje.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)

        columnas = self.frame_info.grid_size()[0]
        for columna in range(columnas):
            self.frame_info.grid_columnconfigure(columna, weight=1)
        
    # Métodos de utilidad
    def get_version_npm(self):
        return self._versionNPM.get() or "N/A"

    def get_version_node(self):
        return self._versionNode.get() or "N/A"

    def set_version_npm(self, version):
        self._versionNPM.set(version)

    def set_version_node(self, version):
        self._versionNode.set(version)

    def show_error(self, msg):
        if self._after_id:
            self.label_mensaje.after_cancel(self._after_id)
            self._after_id = None

        self.label_mensaje.config(text=msg, foreground="#E37E6B", anchor=CENTER, image=Icons.error_icon, compound=LEFT, font=Font(family="Arial", size=8, weight="bold")) # type: ignore
        self._after_id = self.label_mensaje.after(5000, lambda: self.label_mensaje.config(text="", image="", compound="")) # type: ignore
