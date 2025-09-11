from utils.functions import get_npm_modules, get_package_details, split_list
import threading
import tkinter as tk

class ModulesController:
    def __init__(self, view, app_state):
        self.view = view
        self.app_state = app_state
        self._is_loaded = False
        self._npm_modules = get_npm_modules()
        self._n_lists = 6
        self._threads = []

        self.view._action_btn.config(command=lambda: threading.Thread(target=self._load_modules, daemon=True).start())
        self.view.npm_path = self.app_state.get_value('npm_path')
        self.app_state.add_observer('npm_path', self._on_npm_path_change)
        self.view.show_commands_without_selecting_modules = self.app_state.get_value('show_commands_without_selecting_modules')
        self.app_state.add_observer('show_commands_without_selecting_modules', self.on_change_show_commands_without_selecting_modules)

    def _load_modules(self):
        if self._is_loaded and self._check_modify():
            if not self.view.ask_user_confirmation("Confirmar", "Los módulos han sido modificados. ¿Desea continuar?"):
                self.view.stop_loading()
                self.app_state.set_value('can_close_app', True)
                return

        self.app_state.set_value('can_close_app', False)
        self.view.start_loading()
        for sublistas in split_list(self._npm_modules, self._n_lists):
            hilo = threading.Thread(
                target=self._load_package_info,
                args=(sublistas,),
                daemon=True
            )
            self._threads.append(hilo)

        for hilo in self._threads:
            hilo.start()

        for hilo in self._threads:
            hilo.join()

        self._threads.clear()
        self._is_loaded = True
        
        self.view.stop_loading()
        self.view.populate_modules(self._npm_modules)
        self.view.show_widgets()
        self.view._action_btn.config(command=self.reset_all)
        self.app_state.set_value('can_close_app', True)
        
    def _check_modify(self):
        is_modified = False
        list_selected = []
        for dic in self._npm_modules:
            if dic["usar"].get():
                list_selected.append({
                    "nombre": dic["nombre"].lower(),
                    "argumento": dic["argumento"].get(),
                    "version": dic["version"].get()
                })
            
            if dic["usar"].get() or dic["argumento"].get() or dic["version"].get() != dic["versiones"][-1]:
                is_modified = True
                
        self.app_state.set_value('selected_modules', list_selected)
        return is_modified
    
    def _on_modify_modules(self, *args):
        is_modified = self._check_modify()
        if is_modified:
            self.view._action_btn.config(state="normal")
        else:
            self.view._action_btn.config(state="disabled")

    def reset_all(self):
        for dic in self._npm_modules:
            dic["usar"].set(False)
            dic["argumento"].set("")
            dic["version"].set(dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")

    def _load_package_info(self, packages):
        for dic in packages:
            if not dic["versiones"]:
                packages_versions = get_package_details(dic["nombre"], self.app_state.get_value('npm_path'))
                dic["versiones"] = packages_versions["versiones"] if packages_versions else ["Ocurrió un error"]

            if not dic["usar"]:
                dic["usar"] = tk.BooleanVar(value=False)
                dic["usar"].trace_add("write", self._on_modify_modules)
            if not dic["argumento"]:
                dic["argumento"] = tk.StringVar(value="")
                dic["argumento"].trace_add("write", self._on_modify_modules)
            if not dic["version"]:
                dic["version"] = tk.StringVar(value=dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")
                dic["version"].trace_add("write", self._on_modify_modules)

    def _on_npm_path_change(self, new_path):
        self.view.npm_path = new_path
        if self._is_loaded:
            self.reset_all()
            self.view._action_btn.config(state="disabled")
            self._is_loaded = False

    def on_change_show_commands_without_selecting_modules(self):
        current_value = self.app_state.get_value('show_commands_without_selecting_modules')
        self.app_state.set_value('show_commands_without_selecting_modules', not current_value)
        self.view.show_commands_without_selecting_modules = not current_value