from typing import Literal
from Vars import ruta

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