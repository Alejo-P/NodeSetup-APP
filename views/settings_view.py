import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, OUTLINE, CENTER, W, NSEW, LIGHT, SECONDARY, WARNING, EW, LEFT
from pathlib import Path
from CustomWidgets import ScrolledFrame
from Tools import ToolTip
from utils.icons import Icons

class SettingsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self._setup_view()
        self._create_widgets()
        
        for columna in range(self.grid_size()[0]):
            self.grid_columnconfigure(columna, weight=1)

    def _setup_view(self):
        self.npm_path = tk.StringVar()
        self.node_path = tk.StringVar()
        self.git_path = tk.StringVar()
        self.code_path = tk.StringVar()
        self.show_commands_without_selecting_modules = tk.BooleanVar(value=False)

    def _create_widgets(self):
        # Frame Configuracion de Rutas
        self.frame_paths = ttk.LabelFrame(self, text="Configuración de rutas")
        ttk.Label(self.frame_paths, text="Ruta del ejecutable de NPM:", anchor=W).grid(row=0, column=0, padx=5, pady=2, sticky=W)

        entryNpmPath = ttk.Entry(self.frame_paths, textvariable=self.npm_path, style="Custom.TEntry")
        entryNpmPath.config(state="readonly", justify=LEFT)
        entryNpmPath.grid(row=1, column=0, padx=5, pady=5, sticky=EW)
        ToolTip(entryNpmPath, "Ruta completa del ejecutable de NPM.\nEjemplo: C:\\Program Files\\nodejs\\npm.cmd")

        btn_browse = ttk.Button(
            self.frame_paths,
            text="Examinar",
            bootstyle=OUTLINE, # type: ignore
            image=Icons.magnifier_icon,
            compound=LEFT,
            command=self._on_browse_npm
        )
        btn_browse.grid(row=1, column=1, padx=5, pady=5, sticky=EW)
        ToolTip(btn_browse, "Buscar el ejecutable de NPM en el sistema.")

        ttk.Label(self.frame_paths, text="Ruta del ejecutable de Node.js:", anchor=W).grid(row=2, column=0, padx=5, pady=2, sticky=W)

        entryNodePath = ttk.Entry(self.frame_paths, textvariable=self.node_path, style="Custom.TEntry")
        entryNodePath.config(state="readonly", justify=LEFT)
        entryNodePath.grid(row=3, column=0, padx=5, pady=5, sticky=EW)
        ToolTip(entryNodePath, "Ruta completa del ejecutable de Node.js.\nEjemplo: C:\\Program Files\\nodejs\\node.exe")

        btn_browse_node = ttk.Button(
            self.frame_paths,
            text="Examinar",
            bootstyle=OUTLINE,  # type: ignore
            image=Icons.magnifier_icon,
            compound=LEFT,
            command=self._on_browse_node
        )
        btn_browse_node.grid(row=3, column=1, padx=5, pady=5, sticky=EW)
        ToolTip(btn_browse_node, "Buscar el ejecutable de Node.js en el sistema.")

        ttk.Label(self.frame_paths, text="Ruta del ejecutable de Git:", anchor=W).grid(row=4, column=0, padx=5, pady=2, sticky=W)

        entryGitPath = ttk.Entry(self.frame_paths, textvariable=self.git_path, style="Custom.TEntry")
        entryGitPath.config(state="readonly", justify=LEFT)
        entryGitPath.grid(row=5, column=0, padx=5, pady=5, sticky=EW)
        ToolTip(entryGitPath, "Ruta completa del ejecutable de Git.\nEjemplo: C:\\Program Files\\Git\\cmd\\git.exe")
        
        btn_browse_git = ttk.Button(
            self.frame_paths,
            text="Examinar",
            bootstyle=OUTLINE,  # type: ignore
            image=Icons.magnifier_icon,
            compound=LEFT,
            command=self._on_browse_git
        )
        btn_browse_git.grid(row=5, column=1, padx=5, pady=5, sticky=EW)
        ToolTip(btn_browse_git, "Buscar el ejecutable de Git en el sistema.")

        ttk.Label(self.frame_paths, text="Ruta del ejecutable de Visual Studio Code:", anchor=W).grid(row=6, column=0, padx=5, pady=2, sticky=W)

        entryVSCPath = ttk.Entry(self.frame_paths, textvariable=self.code_path, style="Custom.TEntry")
        entryVSCPath.config(state="readonly", justify=LEFT)
        entryVSCPath.grid(row=7, column=0, padx=5, pady=5, sticky=EW)
        ToolTip(entryVSCPath, "Ruta completa del ejecutable de Visual Studio Code.\nEjemplo: C:\\Program Files\\Microsoft VS Code\\Code.exe")
        
        btn_browse_vsc = ttk.Button(
            self.frame_paths,
            text="Examinar",
            bootstyle=OUTLINE,  # type: ignore
            image=Icons.magnifier_icon,
            compound=LEFT,
            command=self._on_browse_vsc
        )
        btn_browse_vsc.grid(row=7, column=1, padx=5, pady=5, sticky=EW)
        ToolTip(btn_browse_vsc, "Buscar el ejecutable de Visual Studio Code en el sistema.")

        columnas, filas = self.frame_paths.grid_size()
        for columna in range(columnas):
            self.frame_paths.grid_columnconfigure(columna, weight=1)
        
        for fila in range(filas):
            self.frame_paths.grid_rowconfigure(fila, weight=1)

        self.frame_paths.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)

        # Frame Otras Configuraciones
        self.frame_other_settings = ttk.LabelFrame(self, text="Otras Configuraciones")
        
        self.chk_show_commands = ttk.Checkbutton(
            self.frame_other_settings,
            text="Mostrar comandos aunque no se hayan seleccionado módulos",
            variable=self.show_commands_without_selecting_modules,
            bootstyle="info-round-toggle", # type: ignore
        )
        self.chk_show_commands.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        ToolTip(self.chk_show_commands, "Si está activado, los comandos de instalación se mostrarán aunque no se haya seleccionado ningún módulo.", position="s", delay_hide=6000)
        columnas, filas = self.frame_other_settings.grid_size()
        for columna in range(columnas):
            self.frame_other_settings.grid_columnconfigure(columna, weight=1)

        for fila in range(filas):
            self.frame_other_settings.grid_rowconfigure(fila, weight=1)

        self.frame_other_settings.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        
    def _on_browse_npm(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de NPM",
            filetypes=[
                ("Archivos ejecutables", "*.exe;*.cmd;*.bat"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            self.npm_path.set(ruta)
            
    def _on_browse_node(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de Node.js",
            filetypes=[
                ("Archivos ejecutables", "*.exe;*.cmd;*.bat"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            self.node_path.set(ruta)
            
    def _on_browse_git(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de Git",
            filetypes=[
                ("Archivos ejecutables", "*.exe;*.cmd;*.bat"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            self.git_path.set(ruta)
            
    def _on_browse_vsc(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de Visual Studio Code",
            filetypes=[
                ("Archivos ejecutables", "*.exe;*.cmd;*.bat"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            self.code_path.set(ruta)
        
    def ask_user_confirmation(self, title, message):
        return messagebox.askyesno(title, message, parent=self)