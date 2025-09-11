from pathlib import Path
from PIL import Image, ImageTk, ImageOps
from typing import List, Literal, overload
import os, subprocess
from config.vars import npm_modules
import copy

@overload
def run_command(comando:List[str], directorio:str = os.getcwd(), *, nuevaVentana:bool=False) -> (subprocess.CompletedProcess[str] | subprocess.CalledProcessError):
    """Ejecuta un comando en la terminal y devuelve el resultado de la ejecucion.

    Args:
        comando (List[str]): _Lista de comandos a ejecutar, por ejemplo ["python", "-m", "main.py"]_
        directorio (str, optional): _Ruta desde a cual se ejecutara el comando_. Defaults to os.getcwd().
        nuevaVentana (bool, optional): _Indica si se debe abrir una nueva ventana de consola_. Defaults to False.
        
    Returns:
        [subprocess.CompletedProcess]: _Resultado de la ejecucion del comando_.
    """
    pass

@overload
def run_command(comando:List[str], directorio:str = os.getcwd(), retornarEn:Literal["bytes"] = "bytes", nuevaVentana:bool=False) -> (subprocess.CompletedProcess[bytes] | subprocess.CalledProcessError):
    """Ejecuta un comando en la terminal y devuelve el resultado de la ejecucion.

    Args:
        comando (List[str]): _Lista de comandos a ejecutar, por ejemplo ["python", "-m", "main.py"]_
        directorio (str, optional): _Ruta desde a cual se ejecutara el comando_. Defaults to os.getcwd().
        nuevaVentana (bool, optional): _Indica si se debe abrir una nueva ventana de consola_. Defaults to False.
        retornarEn (Literal["bytes"], optional): _Indica si se debe retornar la salida en bytes o no_. Defaults to "text".

    Returns:
        [subprocess.CompletedProcess]: _Resultado de la ejecucion del comando_.
    """
    pass

def run_command(comando:List[str], directorio:str = os.getcwd(), retornarEn="text", nuevaVentana=False):
    if retornarEn != "text":
        return handleRunCommandBytes(comando, directorio, nuevaVentana)
    
    return handleRunCommandText(comando, directorio, nuevaVentana)

def handleRunCommandBytes(comando:List[str], directorio:str = os.getcwd(), nuevaVentana=False):
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            cwd=directorio,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            creationflags=subprocess.CREATE_NO_WINDOW if not nuevaVentana else 0   # Evita que se abra una ventana de consola
            )
        return resultado
    except subprocess.CalledProcessError as e:
        return e
    except Exception as ex:
        error = subprocess.CalledProcessError(-1, comando, stderr=str(ex))
        return error

def handleRunCommandText(comando:List[str], directorio:str = os.getcwd(), nuevaVentana=False):
    try:
        resultado = subprocess.run(
            comando,
            check=True,
            cwd=directorio,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if not nuevaVentana else 0   # Evita que se abra una ventana de consola
            )
        return resultado
    except subprocess.CalledProcessError as e:
        return e
    except Exception as ex:
        error = subprocess.CalledProcessError(-1, comando, stderr=str(ex))
        return error

def get_version_of(executable:str):
    """Obtiene la version de un elemento ejecutable en el sistema.

    Args:
        executable (str): _Comando ejecutable del sistema_

    Returns:
        _str_: _Version del comando proporcionado_
    """
    resultado = run_command([executable, "-v"])

    if isinstance(resultado, subprocess.CalledProcessError):
        return ""
    
    return resultado.stdout.strip()

def get_path_of(executable:str):
    """Obtiene la ruta de un elemento ejecutable en el sistema.

    Args:
        executable (str): _Comando ejecutable del sistema_

    Returns:
        _str_: _Ruta de ejecucion del comando proporcionado_
    """
    resultado = run_command(["where", executable])

    if isinstance(resultado, subprocess.CalledProcessError):
        return ""
    
    return resultado.stdout.strip().split('\n')[-1]

def get_npm_modules(excluirClaves:List[str] = [], excluirModulos:List[str] = []):
    """Detalla los modulos de NPM que se van a instalar.

    Args:
        excluirClaves (List[str], optional): _Claves a excluir del diccionario de modulos_. Defaults to []
        excluirModulos (List[str], optional): _Modulos a excluir de la lista de modulos_. Defaults to []
    
    Returns:
        list[dict]: _Lista de modulos de NPM_
    """
    
    detalleMoodulos = []
    for nombreModulo in npm_modules:
        if nombreModulo in excluirModulos:
            continue
        
        dic_base = {
            "usar": None,
            "nombre": nombreModulo,
            "argumento": "",
            "version": None,
            "versiones": None,
        }
        
        for clave in excluirClaves:
            dic_base.pop(clave, None)
        
        dic = copy.deepcopy(dic_base)
        detalleMoodulos.append(dic)
    return detalleMoodulos

def split_list(lista: List, n: int):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

def get_package_details(package_name: str, npm_path: str):
    """Obtiene los detalles de un paquete NPM.

    Args:
        package_name (str): _Nombre del paquete_
        npm_path (str): _Ruta del ejecutable de NPM_

    Returns:
        dict: _Diccionario con los detalles del paquete_
    """
    detalles = {
        "nombre": package_name,
        "versiones": [],
    }

    versionesPaquetes = run_command([npm_path, "show", package_name.lower(), "versions", "--depth=0"])
    if isinstance(versionesPaquetes, subprocess.CalledProcessError):
        return detalles

    try:
        detalles["versiones"] = list(eval(f"{versionesPaquetes.stdout.strip()}"))
    except Exception:
        detalles["versiones"] = []

    return detalles

def load_image_tk(path: Path | str, size: tuple[int, int] = (50, 50), *, resample=Image.Resampling.LANCZOS, invert=False):
    """
    Carga una imagen y la adapta según el tema (oscuro/claro),
    manteniendo transparencia si la tiene.
    """
    try:
        imagen = Image.open(path).convert("RGBA")  # asegurar canal alfa
        imagen = imagen.resize(size, resample)

        if invert:
            # Separar canales
            r, g, b, a = imagen.split()
            # Invertir solo RGB
            rgb_invertido = ImageOps.invert(Image.merge("RGB", (r, g, b)))
            # Volver a unir con el alfa original
            imagen = Image.merge("RGBA", (*rgb_invertido.split(), a))

        return ImageTk.PhotoImage(imagen)

    except Exception as e:
        print("Error al cargar la imagen:", e)
        return ImageTk.PhotoImage(Image.new("RGBA", size, (255, 255, 255, 0)))  # transparente
