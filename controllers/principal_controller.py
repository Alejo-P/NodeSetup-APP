import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from models.app_state import AppState

class PrincipalController:
    def __init__(self, view, app_state:AppState):
        self.view = view
        
        self.project_path = tk.StringVar()
        self.create_path_var = tk.BooleanVar()
        self.delete_content_var = tk.BooleanVar()
        self.delete_on_fail_var = tk.BooleanVar()
        self.stop_on_error_var = tk.BooleanVar()
        
        self.project_path.trace_add("write", lambda *args: self.on_update_ruta(None))
        self.create_path_var.trace_add("write", lambda *args: self.on_update_crear_ruta())
        self.delete_content_var.trace_add("write", lambda *args: self.on_update_eliminar_contenido())
        self.delete_on_fail_var.trace_add("write", lambda *args: self.on_update_eliminar_en_fallo())
        self.stop_on_error_var.trace_add("write", lambda *args: self.on_update_parar_en_fallo())

        self.app_state = app_state
        self.app_state.add_observer(
            ['npm_version', 'node_version'],
            self._update_versions
        )

        # Conectar eventos
        self.view.btnSeleccionar.bind("<Button-1>", lambda e: self.abrir_ruta())
        self.view.btnProceder.config(command=self.crear_proyecto)
        self.view.entryRuta.config(textvariable=self.project_path)
        self.view.entryRuta.bind("<Return>", self.on_update_ruta)
        self.view.entryRuta.bind("<FocusOut>", self.on_update_ruta)

        self.view.check_delete_content.config(variable=self.delete_content_var)
        self.view.check_create_path.config(variable=self.create_path_var)
        self.view.check_delete_on_fail.config(variable=self.delete_on_fail_var)
        self.view._check_stop_on_fail.config(variable=self.stop_on_error_var)

    def abrir_ruta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.app_state.set_value('project_path', ruta)
            self.project_path.set(ruta)

    def on_update_ruta(self, event):
        valido, mensaje = self._check_valid_path()

        if not valido:
            if mensaje:
                self.view.show_error(mensaje)
                
            self.view.check_create_path.config(state="normal")
            self.view.btnIrModulos.config(state="disabled")
            self.view.btnProceder.config(state="disabled")
        else:
            if not self.create_path_var.get():
                self.create_path_var.set(False)
                self.view.check_create_path.config(state="disabled")
            self.view.btnIrModulos.config(state="normal")
            self.view.btnProceder.config(state="normal")

    def on_update_crear_ruta(self):
        self.app_state.set_value('create_path_if_not_exists', self.create_path_var.get())
        self.on_update_ruta(None)

    def on_update_eliminar_contenido(self):
        self.app_state.set_value('delete_content_if_exists', self.delete_content_var.get())
        
    def on_update_eliminar_en_fallo(self):
        self.app_state.set_value('delete_on_fail', self.delete_on_fail_var.get())

    def on_update_parar_en_fallo(self):
        self.app_state.set_value('stop_on_error', self.stop_on_error_var.get())

    def crear_proyecto(self):
        # Aquí va la lógica de creación de proyecto
        print("Creando proyecto en:", self.project_path.get())

    def _check_valid_path(self):
        path = self.project_path.get()
        crear_ruta = self.create_path_var.get()
        node_path = self.app_state.get_value('node_path')
        npm_path = self.app_state.get_value('npm_path')

        if not path:
            return False, ""

        if not Path(path).exists() and not crear_ruta:
            return False, "La ruta no existe"

        if (not Path(path).is_dir() or self._check_extension(path)) and not crear_ruta:
            return False, "La ruta no es un directorio"

        if not node_path or not npm_path:
            return False, "Node o NPM no encontrados"

        return True, ""
    
    def _check_extension(self, ruta):
        return os.path.splitext(ruta)[1] != ""
    
    def _update_versions(self, _):
        self.view.set_version_npm(self.app_state.get_value('npm_version'))
        self.view.set_version_node(self.app_state.get_value('node_version'))
        
