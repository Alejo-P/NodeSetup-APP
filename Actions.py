import os
from PIL import Image, ImageTk
from tkinter import messagebox as mssg
import subprocess
from typing import Any, List, Literal
from Vars import ruta, Registro_eventos

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