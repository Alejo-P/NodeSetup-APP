import subprocess
import os
import json

from Actions import getPathOf

# Servicio para ejecutar comandos de npm
class NpmService:
    npm_path = getPathOf('npm')
    def __init__(self, path:str = os.getcwd()):
        self.path = path
    
    def run(self, command:list[str], newWindow:bool = False, in_bytes:bool = False):
        try:
            resultado = subprocess.run(
                command,
                check=True,
                cwd=self.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=not in_bytes,
                creationflags=subprocess.CREATE_NO_WINDOW if not newWindow else 0   # Evita que se abra una ventana de consola
            )
            return resultado.stdout
        except subprocess.CalledProcessError as error:
            return error.stderr
        