import subprocess
import os
import json

from Actions import getPathOf

# Servicio para ejecutar comandos de npm
class NpmService:
    npm_path = getPathOf('npm')
    
    def __init__(self, path: str = os.getcwd()):
        self._path = path  # Inicializamos el atributo privado
     
    @property
    def path(self):
        return self._path  # Método getter para acceder a la propiedad 'path'
    
    @path.setter
    def path(self, value: str):
        # Verificación para asegurarse de que el valor sea una ruta válida
        if not os.path.exists(value):
            raise ValueError(f"La ruta {value} no existe.")
        self._path = value  # Asignamos el valor solo si es válido
    
    # Ejecuta un comando de npm
    def _run(self, command: list[str], newWindow: bool = False, in_bytes: bool = False, allow_input: bool = False):
        try:
            if not command:
                raise ValueError("No se ha proporcionado un comando para ejecutar")
            
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"No se ha encontrado la ruta {self.path}")
            
            if not self.npm_path:
                raise FileNotFoundError("No se ha encontrado la ruta de npm")
            
            # Asegura que el comando contiene 'npm' o 'npx'
            if "npm" not in command[0] and "npx" not in command[0]:
                command.insert(0, self.npm_path)
            else:
                command[0] = command[0].replace("npm", self.npm_path)
            
            # Ejecuta el comando
            resultado = subprocess.run(
                command,
                check=True,
                cwd=self.path,
                stdin=None if allow_input else subprocess.DEVNULL,  # Permite entrada interactiva
                stdout=None if allow_input else subprocess.PIPE,   # Salida directa a consola
                stderr=None if allow_input else subprocess.PIPE,   # Error directo a consola
                text=not in_bytes,
                creationflags=0 if allow_input else subprocess.CREATE_NO_WINDOW  # Permite entrada en Windows
            )
            return resultado.stdout if resultado.stdout else "Comando ejecutado correctamente"
        except subprocess.CalledProcessError as error:
            return f"Error en el comando: {error.stderr}"
        except Exception as e:
            error = subprocess.CalledProcessError(-1, command, stderr=str(e))
            return f"Error desconocido: {error.stderr}"

    
    # Instala un paquete de npm
    def install(self, package: str, newWindow: bool = False):
        response = self._run(["install", package], newWindow, in_bytes=True)
        if isinstance(response, subprocess.CalledProcessError):
            return response.stderr
        
        # Trata de decodificar la salida como JSON
        try:
            response = response.decode("utf-8") if isinstance(response, bytes) else response
            return json.loads(response) if response.startswith('{') else response
        except json.JSONDecodeError:
            return response
    
    # Desinstala un paquete de npm
    def uninstall(self, package: str, newWindow: bool = False):
        response = self._run(["uninstall", package], newWindow, in_bytes=True)
        if isinstance(response, subprocess.CalledProcessError):
            return response.stderr
        
        # Trata de decodificar la salida como JSON
        try:
            response = response.decode("utf-8") if isinstance(response, bytes) else response
            return json.loads(response) if response.startswith('{') else response
        except json.JSONDecodeError:
            return response
    
    # Lista los paquetes instalados en un proyecto
    def list_packages(self, newWindow: bool = False):
        command = ["list", "--depth=0"]
        if not self.path or not os.path.exists(self.path):
            command.insert(1, "-g")
        
        response = self._run(command, newWindow, in_bytes=True)
        if isinstance(response, subprocess.CalledProcessError):
            return response.stderr
        
        # Trata de decodificar la salida como JSON
        try:
            response = response.decode("utf-8") if isinstance(response, bytes) else response
            return json.loads(response) if response.startswith('{') else response
        except json.JSONDecodeError:
            return response
    
    # Ejecuta un script de npm
    def run_script(self, script: str, newWindow: bool = False):
        response = self._run(["run", script], newWindow, in_bytes=True)
        if isinstance(response, subprocess.CalledProcessError):
            return response.stderr
        
        # Trata de decodificar la salida como JSON
        try:
            response = response.decode("utf-8") if isinstance(response, bytes) else response
            return json.loads(response) if response.startswith('{') else response
        except json.JSONDecodeError:
            return response

if __name__ == "__main__":
    service = NpmService("/ruta/al/proyecto")
    output = service._run(["npm","init"], allow_input=True)
    print(output)
