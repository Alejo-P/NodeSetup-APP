class SettingsController:
    def __init__(self, view, app_state):
        self.app_state = app_state
        self.view = view
        self.view.npm_path.set(self.app_state.get_value('npm_path'))
        self.view.node_path.set(self.app_state.get_value('node_path'))
        self.view.git_path.set(self.app_state.get_value('git_path'))
        self.view.code_path.set(self.app_state.get_value('code_path'))
        self.app_state.add_observer('npm_path', self._on_npm_path_change)
        self.app_state.add_observer('node_path', self._on_node_path_change)
        self.app_state.add_observer('git_path', self._on_git_path_change)
        self.app_state.add_observer('code_path', self._on_code_path_change)

    def _on_npm_path_change(self, *args):
        self.view.npm_path.set(self.app_state.get_value('npm_path'))

    def _on_node_path_change(self, *args):
        self.view.node_path.set(self.app_state.get_value('node_path'))

    def _on_git_path_change(self, *args):
        self.view.git_path.set(self.app_state.get_value('git_path'))

    def _on_code_path_change(self, *args):
        self.view.code_path.set(self.app_state.get_value('code_path'))

    def update_npm_path(self, new_path):
        self.app_state.set_value('npm_path', new_path)