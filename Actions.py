import os
from PIL import Image, ImageTk
from tkinter import messagebox as mssg
import subprocess
from typing import Any, List, Literal, overload
from Vars import ruta, Registro_eventos, respuestas

def setEvent(tipoEvento:Literal["INFO", "ERROR"], evento:dict[str, Any]):
    """Regsitar un evento (detalles de un comando) ejecutado por el programa.

    Args:
        tipoEvento (Literal['INFO', 'ERROR']): _Tipo del evento que se va a registrar_
        evento (dict[str, Any]): _Diccionario con los datalles del evento como comando ejecutado, resultados, etc._ 
    """
    
    Registro_eventos.append({
        "Tipo": tipoEvento,
        "Evento": evento
    })

def getEvents():
    """Obtiene todos los eventos registrados en el programa.

    Returns:
        [List[dict[str, Any]]]: _Lista de eventos registrados_
    """
    copia_eventos = []
    dicEvento = {
        "Tipo": None,
        "Comando": None,
        "Salida": None,
        "Error": None,
        "CodigoRetorno": 0,
        "Funcion": None
    }
    for evento in Registro_eventos:
        # Extraer los datos del evento
        dicEvento["Tipo"] = evento["Tipo"]
        dicEvento["Comando"] = evento["Evento"]["Comando"]
        dicEvento["Funcion"] = evento["Evento"]["Funcion"]
        
        respuesta = evento["Evento"]["Resultado"] # Obtener el resultado del evento (resultado de la ejecucion del comando)
        if isinstance(respuesta, subprocess.CompletedProcess): # Verificar si el resultado es de tipo CompletedProcess
            dicEvento["Salida"] = respuesta.stdout
            dicEvento["Error"] = respuesta.stderr
            dicEvento["CodigoRetorno"] = respuesta.returncode
        
        elif isinstance(respuesta, subprocess.CalledProcessError): # Verificar si el resultado es de tipo CalledProcessError
            dicEvento["Salida"] = respuesta.output
            dicEvento["Error"] = respuesta.stderr
            dicEvento["CodigoRetorno"] = respuesta.returncode
        
        copia_eventos.append(dicEvento.copy()) # Agregar una copia del evento a la lista de eventos
    
    return copia_eventos # Devolver la lista de eventos

def writeLog(typeLog:Literal["INFO", "ERROR"], message:str, inFunction:str):
    """Escribe un mensaje en el archivo de registro de eventos.

    Args:
        typeLog (Literal["INFO", "ERROR"]): _Tipo de log que se va a registrar_
        message (str): _Mensaje que se va a registrar_
        inFunction (str): _Funcion en la que se registro el evento_
    """
    try:
        with open(ruta, "a") as archivo:
            archivo.write(f"{typeLog} - {message} - {inFunction}\n")
    except Exception as e:
        print("Error al escribir el log:", e)

def showLogInConsole(typeLog:Literal["INFO", "ERROR"]):
    """Muestra los eventos registrados en el archivo de registros.

    Args:
        typeLog (Literal["INFO", "ERROR"]): _Tipo de log que se va a mostrar_
    """
    try:
        with open(ruta, "r") as archivo:
            for linea in archivo:
                if typeLog in linea:
                    print(linea)
    except Exception as e:
        print("Error al mostrar el log:", e)

def doNothing():
    """Esta función no ejecuta ninguna accion.
    """
    pass

def preventCloseWindow(titulo:str, mensaje:str, tipo:Literal["INFO", "WARNING", "ERROR"]):
    """Evita que la ventana se cierre y muestra un mensaje.
    """
    if tipo == "INFO":
        mssg.showinfo(titulo, mensaje)
    elif tipo == "WARNING":
        mssg.showwarning(titulo, mensaje)
    elif tipo == "ERROR":
        mssg.showerror(titulo, mensaje)

@overload
def runCommand(comando:List[str], directorio:str = os.getcwd()) -> subprocess.CompletedProcess[str]:
    pass

@overload
def runCommand(comando:List[str], directorio:str = os.getcwd(), retornarEn:Literal["bytes"] = "bytes") -> subprocess.CompletedProcess[bytes]:
    """Ejecuta un comando en la terminal y devuelve el resultado de la ejecucion.

    Args:
        comando (List[str]): _Lista de comandos a ejecutar, por ejemplo ["python", "-m", "main.py"]_
        directorio (str, optional): _Ruta desde a cual se ejecutara el comando_. Defaults to os.getcwd().
        retornarEn (Literal["bytes"], optional): _Indica si se debe retornar la salida en bytes o no_. Defaults to "text".

    Returns:
        [subprocess.CompletedProcess]: _Resultado de la ejecucion del comando_.
    """
    pass

def runCommand(comando:List[str], directorio:str = os.getcwd(), retornarEn="text"):
    if retornarEn == "text":
        return handleRunCommandText(comando, directorio)
    else:
        return handleRunCommandBytes(comando, directorio)

def handleRunCommandBytes(comando:List[str], directorio:str = os.getcwd()):
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            cwd=directorio,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0   # Evita que se abra una ventana de consola
            )
        return resultado
    except subprocess.CalledProcessError as e:
        return e

def handleRunCommandText(comando:List[str], directorio:str = os.getcwd()):
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
    
    return resultado.stdout.strip().split('\n')[-1]

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

def loadImageTk(path:str, width:int = 50, height:int = 50):
    """Carga una imagen en memoria.

    Args:
        path (str): _Ruta de la imagen a cargar_}
        width (int, optional): _Ancho de la imagen_. Defaults to 50.
        height (int, optional): _Alto de la imagen_. Defaults to 50.
        name (str, optional): _Nombre de la imagen_. Defaults to "".

    Returns:
        _PhotoImage_: _Imagen en formato Tkinter_
    """
    try:
        imagen = Image.open(path).resize((width, height))
        imagenTk = ImageTk.PhotoImage(imagen)
        return imagenTk
    except Exception as e:
        print("Error al cargar la imagen:", e)
        return None

def getGitBranches(ruta:str):
    """Obtiene las ramas de un repositorio Git.

    Args:
        ruta (str): _Ruta del repositorio Git_
    
    Returns:
        _Dict[str, bool]: _Diccionario con las ramas del repositorio y si estan activas o no_
    """
    resultado = runCommand([getPathOf("git"), "branch"], ruta)
    
    if isinstance(resultado, subprocess.CalledProcessError):
        return {"No hay ramas": True}
    
    return {rama.replace("*","").strip():rama.startswith("*") for rama in resultado.stdout.strip().split('\n')}

def getCurrentBrach(ramas:dict[str, bool]):
    """Obtiene la rama actual de un repositorio Git.

    Args:
        ramas (dict[str, bool]): _Diccionario con las ramas del repositorio y si estan activas o no_
        
    Returns:
        _str_: _Nombre de la rama actual_
    """
    
    for rama, estaActiva in ramas.items():
        if estaActiva:
            return rama
        
    return "No hay rama actual"

def getBranchCommitsLog(ruta:str, rama:str = "*") -> List[dict[str, Any]]:
    """Obtiene los commits de un repositorio Git.

    Args:
        ruta (str): _Ruta del repositorio Git_
        rama (str, optional): _Nombre de la rama del repositorio_. Defaults to "*".
    
    Returns:
        _str_: _Log de commits del repositorio_
    """
    comando = [getPathOf("git"), "log", "--oneline", "--decorate"]
    if rama != "*":
        comando.extend(["--first-parent", rama])
    else:
        comando.append("--all")
    resultado = runCommand(comando, ruta, "bytes")
    listaDetalles:list[dict[str, Any]] = []
    nombreRama = ""
    
    if isinstance(resultado, subprocess.CalledProcessError):
        return [{"Error al recuperar el log de commits": resultado.stderr.decode("utf-8")}]
    
    for item in resultado.stdout.decode("utf-8").split("\n")[:-1]:
        commit = item.replace("*", "").split(" ", 1)
        
        if commit[1].startswith("("):
            indiceInicio = commit[1].find("(") + 1
            indiceFin = commit[1].find(")")
            if "origin/" in commit[1]:
                nombreRama = commit[1][indiceInicio:indiceFin].split(",")[-1].strip()
                commit[1] = commit[1][indiceFin+2:]
        listaDetalles.append({
            "id": commit[0],
            "rama": nombreRama,
            "mensaje": commit[1]
        })
    return listaDetalles

def putInQueue(elemento:Any):
    """Pone un elemento en la cola de ejecucion.

    Args:
        elemento (Any): _Elemento a poner en la cola_
    """
    
    respuestas.put(elemento)
    
def getFromQueue(sinEspera:bool = False):
    """Obtiene un elemento de la cola de ejecucion.

    Args:
        sinEspera (bool, optional): _Indica si se debe esperar a que haya un elemento en la cola o no_. Defaults to False.

    Returns:
        _Any_: _Elemento obtenido de la cola_
    """
    
    if sinEspera:
        return respuestas.get_nowait()
    
    return respuestas.get()
    
def isQueueEmpty():
    """Verifica si la cola de ejecucion esta vacia.

    Returns:
        _bool_: _Indica si la cola esta vacia o no_
    """
    
    return respuestas.empty()

def clearQueue():
    """Vacia la cola de ejecucion.
    """
    
    while not respuestas.empty():
        try:
            respuestas.get_nowait()
        except:
            break

if __name__ == "__main__":
    logs = getBranchCommitsLog(os.getcwd())
    for com in logs:
        print(com)