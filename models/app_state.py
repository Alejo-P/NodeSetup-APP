class AppState:
    def __init__(self):
        self._state = {
            'git_path': "",
            'npm_path': "",
            'node_path': "",
            'code_path': "",
            'git_version': "",
            'npm_version': "",
            'node_version': "",
            'project_path': "",
            'create_path_if_not_exists': False,
            'delete_content_if_exists': False,
            'delete_on_fail': False,
            'stop_on_error': False,
            'can_close_app' : False,
            'selected_modules': [],
            'show_commands_without_selecting_modules': False
        }
        
        self._observers = {}

    def add_observer(self, key, callback):
        """Registrar un observador para una clave concreta."""
        if isinstance(key, list):
            for k in key:
                self.add_observer(k, callback)
            return
        
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(callback)

    def notify_observers(self, key):
        """Notificar solo a los observadores de esa clave."""
        if key in self._observers:
            for callback in self._observers[key]:
                callback(self._state[key])

    def set_value(self, key, value):
        """Actualizar un valor y notificar."""
        if key in self._state:
            self._state[key] = value
            self.notify_observers(key)
        else:
            raise KeyError(f"Clave desconocida: {key}")

    def get_value(self, key):
        """Obtener un valor."""
        if key in self._state:
            return self._state[key]
        else:
            raise KeyError(f"Clave desconocida: {key}")
        
    def get_all(self):
        """Obtener todo el estado."""
        return self._state.copy()