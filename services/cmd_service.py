import subprocess
import os
import sys
import threading

# Añade el directorio padre al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Actions import getPathOf

current_path = os.getcwd()

# Servicio para ejecutar comandos de la terminal
class CmdService:
    cmd_path = getPathOf('cmd.exe')
    ps1_path = getPathOf('powershell.exe')
    
    @property
    def cwd(self):
        return self._cwd
    
    @cwd.setter
    def cwd(self, value):
        if not os.path.exists(value):
            raise FileNotFoundError(f"No se ha encontrado la ruta {value}")
        self._cwd = value
    
    @property
    def newWindow(self):
        return self._newWindow
    
    @newWindow.setter
    def newWindow(self, value):
        self._newWindow = value
    
    @property
    def in_bytes(self):
        return self._in_bytes
    
    @in_bytes.setter
    def in_bytes(self, value):
        self._in_bytes = value
    
    def __init__(
        self,
        cwd=current_path,
        newWindow=False,
        in_bytes=False
    ) -> None:
        self._cwd = cwd
        self._newWindow = newWindow
        self._in_bytes = in_bytes
    
    # Ejecuta un comando de la terminal
    def run(self, command: list[str], interactive=False):
        def read_stdout(process):
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                print(line, end='')  # Muestra la salida en tiempo real
                output.append(line.decode(errors='replace') if self._in_bytes else line)
        
        try:
            if not command:
                raise ValueError("No se ha proporcionado un comando para ejecutar")
            
            if not os.path.exists(self._cwd):
                raise FileNotFoundError(f"No se ha encontrado la ruta {self._cwd}")
            
            if not self.cmd_path:
                raise FileNotFoundError("No se ha encontrado la ruta de cmd")
            
            # Asegura que el comando contiene 'cmd' o 'powershell'
            if "cmd" not in command[0] and "powershell" not in command[0]:
                command.insert(0, self.cmd_path)
            else:
                command[0] = command[0].replace("cmd", self.cmd_path)
                command[0] = command[0].replace("powershell", self.ps1_path)
            
            # Determinar si se permite entrada interactiva
            stdin_mode = subprocess.PIPE if interactive else subprocess.DEVNULL
            
            # Ejecuta el comando con Popen
            process = subprocess.Popen(
                command,  # Comando a ejecutar
                cwd=self.cwd,  # Directorio de trabajo
                stdin=stdin_mode,  # Entrada estándar
                stdout=subprocess.PIPE,  # Salida estándar
                stderr=subprocess.PIPE,  # Salida de errores
                text=not self.in_bytes,  # Salida en texto o bytes
                creationflags=subprocess.CREATE_NO_WINDOW if not self.newWindow else 0,  # Crear ventana o no
                shell=True  # Ejecutar en la terminal
            )

            output = []
            # Leer salida en tiempo real
            if process.stdout:
                thread = threading.Thread(target=read_stdout, args=(process,), daemon=True)
                thread.start()
            
            # Esperar a que el proceso termine
            process.wait()
            
            return output
        except Exception as e:
            print('An exception occurred:', e)

# Instancia del servicio
if __name__ == '__main__':
    cmd = CmdService()
    # Comando interactivo (ejemplo)
    print(cmd.run(['npm', 'init'], interactive=True))
