import os
import subprocess
from typing import List, Literal
from Vars import ruta

class ActionsForNPM:
    def __init__(self):
        self._prefijo = getPathOf("npm")
        self._modulos = []
    
    def getVersionOf(self):
        resultado = runCommand([self._prefijo, "-v"])
        
        if isinstance(resultado, subprocess.CalledProcessError):
            return None
        
        return resultado.stdout.strip()
    
    def getModulos(self, global_:bool = False):
        comando = [self._prefijo, "list"]
        if global_:
            comando.append("-g")
        resultado = runCommand(comando)
        return resultado.stdout.strip()
    
    def getInfoPackage(self, nombre:str):
        resultado = runCommand([self._prefijo, "info", nombre])
        return resultado.stdout.strip()
    
    def getVersionsOfPackage(self, nombre:str):
        comando = [self._prefijo,"list", nombre]
        
        comando.append("--depth=0") # Solo mostrar los paquetes de primer nivel
        resultado = runCommand(comando)
        
        if isinstance(resultado, subprocess.CalledProcessError):
            return None
        
        lineas = resultado.stdout.splitlines()
        for linea in lineas:
            ce = linea.find(' ')
            if ce != -1:
                paqueteB = linea[ce+1:]
            else:
                paqueteB = linea
            
            if '@' in paqueteB:
                version = paqueteB.split('@')[1].strip()
                return version
        return None

def writeLog(typeLog:Literal["INFO", "ERROR"], message:str, inFunction:str):
    with open(f"{ruta}/logs.txt", "a") as file:
        file.write(f"{typeLog} - {message} - {inFunction}\n")
    return True

def showLog(typeLog:Literal["INFO", "ERROR"]):
    with open(f"{ruta}/logs.txt", "r") as file:
        logs = file.readlines()
        for log in logs:
            if typeLog in log:
                print(log)
    return True

def doNothing():
    """Esta función no ejecuta ninguna accion.
    """
    pass

def runCommand(comando:List[str], directorio:str = os.getcwd()):
    """Ejecuta un comando en la terminal y devuelve el resultado de la ejecucion.

    Args:
        comando (List[str]): _Lista de comandos a ejecutar, por ejemplo ["python", "-m", "main.py"]_
        directorio (str, optional): _Ruta desde a cual se ejecutara el comando_. Defaults to os.getcwd().

    Returns:
        [subprocess.CompletedProcess]: _Resultado de la ejecucion del comando_.
    """
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            cwd=directorio,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0   # Evita que se abra una ventana de consola
            )
        return resultado
    except subprocess.CalledProcessError as e:
        return e

def getPathOf(elemento_ejecutable:str):
    """Obtiene la ruta de un elemento ejecutable en el sistema.

    Args:
        elemento_ejecutable (str): _Comando ejecutable del sistema_

    Returns:
        _str_: _Ruta de ejecucion del comando proporcionado_
    """
    resultado = runCommand(["where", elemento_ejecutable])
    
    if isinstance(resultado, subprocess.CalledProcessError):
        return ""
    
    return resultado.stdout.strip().split('\n')[1]

def getVersionOf(elemento_ejecutable:str):
    """Obtiene la version de un elemento ejecutable en el sistema.

    Args:
        elemento_ejecutable (str): _Comando ejecutable del sistema_

    Returns:
        _str_: _Version del comando proporcionado_
    """
    resultado = runCommand([elemento_ejecutable, "-v"])
    
    if isinstance(resultado, subprocess.CalledProcessError):
        return None
    
    return resultado.stdout.strip()