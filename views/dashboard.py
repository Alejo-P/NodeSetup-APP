import tkinter as tk, threading, queue
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, RIGHT, TOP, CENTER, BOTH, Y

from Tools import ToolTip
from config.constants import APP_NAME, APP_SIZE, APP_THEME, RESIZABLE, APP_GEOMETRY
from CustomWidgets import SelectionLabel
from utils.icons import Icons
from utils.functions import get_path_of, get_version_of
from styles import load_custom_styles

from models.app_state import AppState
from views.modules_view import ModulesView
from controllers.modules_controller import ModulesController
from views.principal_view import PrincipalView
from controllers.principal_controller import PrincipalController

from views.settings_view import SettingsView
from controllers.settings_controller import SettingsController

class DashboardWindow(ttk.Window):
    def __init__(self):
        super().__init__(
            themename=APP_THEME,
            title=APP_NAME,
            size=APP_SIZE,
            resizable=RESIZABLE,
        )

        self._setup()
        self._create_widgets()
        self._on_update_frames()
        self._go_to_frame("Principal")
        
        self.app_state.add_observer(
            ['git_path', 'npm_path', 'node_path'],
            lambda _: self._update_frames()
        )
        self.app_state.add_observer(
            'can_close_app',
            lambda _: self._on_update_close()
        )

        self._load_paths_and_versions()
        
    def _setup(self):
        #self.iconbitmap(APP_ICON)
        self.geometry(APP_GEOMETRY)
        load_custom_styles()
        
        self.app_state = AppState()
        self.queue = queue.Queue()
        Icons.load_icons()
    
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_close())

    def _create_widgets(self):
        self.frameSeleccion = ttk.Frame(self, name="selector", style="Custom.TFrame")
        self.frameSeleccion.pack(fill=Y, side=LEFT, ipadx=5)
        
        self.Principal = SelectionLabel(self.frameSeleccion, text="Principal", style="Custom.TLabel", anchor=CENTER, compound=TOP, image=Icons.home_icon)
        self.Principal.pack(fill=BOTH, expand=True)
        
        self.Modulos = SelectionLabel(self.frameSeleccion, text="Modulos", style="Disabled.TLabel", state="disabled", anchor=CENTER, compound=TOP, image=Icons.download_icon)
        self.Modulos.pack(fill=BOTH, expand=True)
        
        self.Git = SelectionLabel(self.frameSeleccion, text="Git", style="Disabled.TLabel", state="disabled", anchor=CENTER, compound=TOP, image=Icons.code_fork_icon)
        self.Git.pack(fill=BOTH, expand=True)
        
        self.Tareas = SelectionLabel(self.frameSeleccion, text="Tareas", style="Disabled.TLabel", state="disabled", anchor=CENTER, compound=TOP, image=Icons.checkbox_icon)
        self.Tareas.pack(fill=BOTH, expand=True)
        
        self.Configuracion = SelectionLabel(self.frameSeleccion, text="Configuracion", style="Custom.TLabel", anchor=CENTER, compound=TOP, image=Icons.cog_icon)
        self.Configuracion.pack(fill=BOTH, expand=True)
        
        # Creacion de Tooltips
        self.tooltip_principal = ToolTip(self.Principal, "Vista principal de la aplicación", "e", delay_hide=5000)
        self.tooltip_modulos = ToolTip(self.Modulos, "Seleccionar y descargar módulos NPM", "e", delay_hide=5000)
        self.tooltip_git = ToolTip(self.Git, "Configuración de Git", "e", delay_hide=5000)
        self.tooltip_tareas = ToolTip(self.Tareas, "Gestión de tareas", "e", delay_hide=5000)
        self.tooltip_configuracion = ToolTip(self.Configuracion, "Configuración de la aplicación", "e", delay_hide=5000)

        # Creacion de contenedores para cada ventana
        self.principal_view = PrincipalView(self)
        self.principal_controller = PrincipalController(
            self.principal_view,
            self.app_state,
        )

        self.modules_view = ModulesView(self)
        self.modules_controller = ModulesController(
            self.modules_view,
            self.app_state,
        )
        
        # Otros frames (Git, Tareas, Configuracion)
        
        self.settings_view = SettingsView(self)
        self.settings_controller = SettingsController(
            self.settings_view,
            self.app_state,
        )

    def _load_paths_and_versions(self):
        def collect_paths_and_versions():
            try:
                data = {
                    "npm_path": get_path_of("npm"),
                    "node_path": get_path_of("node"),
                    "git_path": get_path_of("git"),
                    "code_path": get_path_of("code"),
                }

                data.update({
                    "npm_version": get_version_of(data["npm_path"]),
                    "node_version": get_version_of(data["node_path"]),
                    "git_version": get_version_of(data["git_path"]),
                })

                self.queue.put({"ok": True, "data": data})

            except Exception as e:
                self.queue.put({"ok": False, "error": str(e)})

        def check_progress(worker: threading.Thread):
            try:
                result = self.queue.get_nowait()

                if result["ok"]:
                    for key, value in result["data"].items():
                        self.app_state.set_value(key, value)
                else:
                    messagebox.showerror("Error", f"No se pudieron cargar las rutas: {result['error']}")

            except queue.Empty:
                # Mientras el hilo siga vivo, seguimos esperando
                if worker.is_alive():
                    self.after(100, lambda: check_progress(worker))
            
        init_state = "Cargando..."

        for path in ['npm_path', 'node_path', 'git_path', 'code_path']:
            self.app_state.set_value(path, init_state)

        for version in ['npm_version', 'node_version', 'git_version']:
            self.app_state.set_value(version, init_state)

        worker = threading.Thread(target=collect_paths_and_versions, daemon=True)
        worker.start()
        self.after(100, check_progress, worker)

    def _update_frames(self):
        self.Modulos.config(
            state="normal" if self.app_state.get_value('git_path') != "Cargando..." else "disabled",
            style="Custom.TLabel" if self.app_state.get_value('git_path') else "Disabled.TLabel"
        )
        self.Git.config(
            state="normal" if self.app_state.get_value('git_path') != "Cargando..." else "disabled",
            style="Custom.TLabel" if self.app_state.get_value('git_path') else "Disabled.TLabel"
        )
        
        self._on_update_frames()

    def _show_selected_frame(self, frameName:str):
        for frame in self.winfo_children():
            if frame.winfo_class() == "TFrame" and frame.winfo_name() != "selector":
                frame.pack_forget()
        
        if frameName == "Principal":
            self.principal_view.pack(side=RIGHT, fill=BOTH, expand=True)
        elif frameName == "Modulos":
            self.modules_view.pack(side=RIGHT, fill=BOTH, expand=True)
        elif frameName == "Git":
            pass
        elif frameName == "Tareas":
            pass
        elif frameName == "Configuracion":
            self.settings_view.pack(side=RIGHT, fill=BOTH, expand=True)

    def _on_update_frames(self):
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
                    frame.on_click(callback=self._on_frame_click)
                    continue
                
                if frame.type == "selected":
                    frame.config( # type: ignore
                        style="Selected.TLabel",
                        cursor="arrow"
                    )
                    frame.delete_bind("<Button-1>")
                    continue
                    
                frame.type = "normal"
                frame.config( # type: ignore
                    style="Custom.TLabel",
                    cursor="hand2",
                )
                frame.on_click(callback=self._on_frame_click)

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

        # setToolTipText()

    def _on_frame_click(self, event:tk.Event):
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
                    widget.on_click(callback=self._on_frame_click)
                    continue
                
                widget.type = "normal"
                widget.config( # type: ignore
                    style="Custom.TLabel",
                    cursor="hand2",
                )
                widget.on_click(callback=self._on_frame_click)

        event.widget.config(style="Selected.TLabel", cursor="arrow") # type: ignore
        event.widget.delete_bind("<Button-1>") # type: ignore
        event.widget.type = "selected" # type: ignore
        self._show_selected_frame(event.widget.cget("text"))

    def _go_to_frame(self, frameName:str):
        for frame in self.frameSeleccion.winfo_children():
            if frame.cget("text") == frameName:
                frame.event_generate("<Button-1>")
                break
        else:
            messagebox.showerror("Error", f"El frame {frameName} no existe")
            
    def _on_update_close(self):
        state = self.app_state.get_value('can_close_app')
        if state:
            self.protocol("WM_DELETE_WINDOW", lambda: self._on_close())
        else:
            self.protocol("WM_DELETE_WINDOW", lambda: messagebox.showwarning("Atención", "No se puede cerrar la aplicación en este momento."))

    def _on_close(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")