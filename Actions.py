import ast, copy
from collections.abc import Callable
import os, queue, re, subprocess, tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from tkinter import messagebox as mssg
from typing import Any, List, Literal, overload, Union
from Vars import ruta, Registro_eventos, keywordsPY, keywordsJS, keywordsHTML, keywordsCSS, modulosNPM

def getDetailedModules(excluirClaves:List[str] = [], excluirModulos:List[str] = []):
    """Detalla los modulos de NPM que se van a instalar.

    Args:
        excluirClaves (List[str], optional): _Claves a excluir del diccionario de modulos_. Defaults to []
        excluirModulos (List[str], optional): _Modulos a excluir de la lista de modulos_. Defaults to []
    
    Returns:
        list[dict]: _Lista de modulos de NPM_
    """
    
    detalleMoodulos = []
    for nombreModulo in modulosNPM:
        if nombreModulo in excluirModulos:
            continue
        
        dic_base = {
            "usar": None,
            "nombre": nombreModulo,
            "argumento": "",
            "version": None,
            "versiones": None,
            "global": None
        }
        
        for clave in excluirClaves:
            dic_base.pop(clave, None)
        
        dic = copy.deepcopy(dic_base)
        detalleMoodulos.append(dic)
    return detalleMoodulos

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
def runCommand(comando:List[str], directorio:str = os.getcwd(), *, nuevaVentana:bool=False) -> (subprocess.CompletedProcess[str] | subprocess.CalledProcessError):
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
def runCommand(comando:List[str], directorio:str = os.getcwd(), retornarEn:Literal["bytes"] = "bytes", nuevaVentana:bool=False) -> (subprocess.CompletedProcess[bytes] | subprocess.CalledProcessError):
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

def runCommand(comando:List[str], directorio:str = os.getcwd(), retornarEn="text", nuevaVentana=False):
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

def getBranchCommitsLog(ruta:str) -> List[dict[str, Any]]:
    """Obtiene los commits de un repositorio Git.

    Args:
        ruta (str): _Ruta del repositorio Git_
    
    Returns:
        _List[dict[str, Any]]_: _Lista de commits del repositorio_
    """
    comando = [getPathOf("git"), "log", "--oneline", "--decorate", "--all"]
    
    resultado = runCommand(comando, ruta, "bytes")
    listaDetalles:list[dict[str, Any]] = []
    nombreRama = ""
    
    if isinstance(resultado, subprocess.CalledProcessError):
        return [{
            "id": "0",
            "rama": "Error",
            "mensaje": resultado.stderr.decode("utf-8")
        }]
    
    for item in resultado.stdout.decode("utf-8").split("\n")[:-1]:
        commit = item.split(" ", 1)
        
        if commit[1].startswith("("):
            indiceInicio = commit[1].find("(") + 1
            indiceFin = commit[1].find(")")
            if "origin/" in commit[1]:
                nombreRama = commit[1][indiceInicio:indiceFin].split(",")[-1].strip().replace("origin/","")
                commit[1] = commit[1][indiceFin+2:]
            
            if "HEAD -> " in commit[1]:
                nombreRama = commit[1][indiceInicio:indiceFin].split(",")[-1].strip().replace("HEAD -> ","")
                commit[1] = commit[1][indiceFin+2:]
                
        listaDetalles.append({
            "id": commit[0],
            "rama": nombreRama,
            "mensaje": commit[1]
        })
    return listaDetalles

def loadInfoNPMModules(modulosCargar: List[dict[str, Any]]):
    for dic in modulosCargar:
        versionesPaquetes = runCommand([getPathOf("npm"), "show", dic["nombre"].lower(), "versions", "--depth=0"])
        if isinstance(versionesPaquetes, subprocess.CalledProcessError):
            versiones = ["Ocurrió un error"]
        else:
            versiones = list(ast.literal_eval(f"{versionesPaquetes.stdout.strip()}"))
        
        # Verifica si la clave "versiones" existe antes de usarla
        if dic.get("versiones") is not None:
            dic["versiones"] = versiones
        
        # Verifica si la clave "usar" existe antes de usarla
        if dic.get("usar", "") == None:
            dic["usar"] = False
        
        # Verifica si la clave "global" existe antes de usarla
        if dic.get("global", "") == None:
            dic["global"] = False
        
        # Verifica si la clave "argumento" existe antes de usarla
        if dic.get("argumento", "") == None:
            dic["argumento"] = ""
        
        # Verifica si la clave "version" existe y maneja el caso en que "versiones" esté ausente
        if dic.get("version", "") == None:
            dic["version"] = versiones[-1]
    
    return modulosCargar
    
def isQueueEmpty(cola:queue.Queue):
    """Verifica si la cola de ejecucion esta vacia.

    Returns:
        _bool_: _Indica si la cola esta vacia o no_
    """
    
    return cola.empty()

def clearQueue(cola:queue.Queue):
    """Vacia la cola de ejecucion.
    """
    
    while not cola.empty():
        try:
            cola.get_nowait()
        except:
            break

def centerWindow(ventana: Union[ttk.Toplevel, tk.Tk, ttk.Window], restablecer_tamaño=False):
    """Centra una ventana en la pantalla.

    Args:
        ventana (Union[ttk.Toplevel, tk.Tk, ttk.Window]): _Ventana a centrar_
        restablecer_tamaño (bool, optional): _Indica si se debe restablecer el tamaño de la ventana_. Defaults to False.
    """
    if restablecer_tamaño:
            ventana.wm_geometry("")
            
    ventana.update_idletasks()
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f"{width}x{height}+{x}+{y}")

_NoCallback = lambda e: doNothing
def promptUser(ventana:Union[ttk.Window, ttk.Toplevel], titulo:str, mensaje:str, tipo:Literal["info", "warning", "error"], esArchivo:bool = False, esCarpeta:bool = False, opciones:list[str] = [], usarEntrada:bool = True, callback:Callable[[str], Any] = _NoCallback):
    """Muestra un mensaje al usuario y espera una respuesta.
    
    Args:
        ventana (ttk.Window): _Ventana principal_
        mensaje (str): _Mensaje a mostrar_
        titulo (str): _Titulo de la ventana_
        tipo (Literal["info", "warning", "error"]): _Tipo de mensaje_
        esArchivo (bool, optional): _Indica si se espera una ruta de archivo como respuesta_. Defaults to False.
        esCarpeta (bool, optional): _Indica si se espera una ruta de carpeta como respuesta_. Defaults to False.
        opciones (list[str], optional): _Opciones a mostrar en un combobox_. Defaults to [].
        usarEntrada (bool, optional): _Indica si se debe mostrar un campo de entrada para la respuesta_. Defaults to True.
        callback (Callable[[str], Any], optional): _Funcion a ejecutar despues de obtener la respuesta (esta funcion recibira la respuesta como parametro)_. Defaults to _NoCallback.
        
    Returns:
        _str_: _Respuesta del usuario_
    """
    def _valueCombo():
        if _extArch.get() == ".env":
            _nomArch.set("")
            inp.config(state="disabled")
        else:
            inp.config(state="normal")
        _validInput()
    
    def _validInput():
        if _extArch.get() == ".env":
            botonOk.config(state="normal")
            return
        
        if not _nomArch.get() and usarEntrada:
            botonOk.config(state="disabled")
            return
        
        botonOk.config(state="normal")
    
    def _validarSeleccion():
        if not _opcSeleccionada.get() or _opcSeleccionada.get() == "cargando...":
            botonOk.config(state="disabled")
            return
        
        botonOk.config(state="normal")
    
    def _validarEntrada(valor):
        if esCarpeta or esArchivo:
            if not valor:
                return False
            
            if valor.find(".") != -1 or valor.find("/") != -1 or valor.find("\\") != -1:
                return False
        
        return True
        
    def returnInput():
        if esCarpeta:
            res = f"{_nomArch.get()}"
        else:
            res = f"{_nomArch.get()}{_extArch.get()}"
        
        if not usarEntrada and opciones:
            res = _opcSeleccionada.get()
        
        _nomArch.set("")
        _extArch.set("")
        _opcSeleccionada.set("")
        _top.destroy()
        callback(res)
    
    _top = ttk.Toplevel(master=ventana)
    _top.title(titulo)
    _top.resizable(False, False)
    _top.transient(ventana)
    idValid = _top.register(_validarEntrada)
    
    _nomArch = ttk.StringVar()
    _extArch = ttk.StringVar()
    _opcSeleccionada = ttk.StringVar()
    
    ttk.Label(_top, text=mensaje, style=f"{tipo}.TLabel").pack(padx=10, pady=10)
    inp = ttk.Entry(_top, style=f"{tipo}.TEntry", textvariable=_nomArch, validate="key", validatecommand=(idValid, "%P"))
    cmb = ttk.Combobox(_top, values=tuple(opciones), style=f"{tipo}.TCombobox", textvariable=_opcSeleccionada, state="readonly")
    if usarEntrada:
        inp.pack(padx=10, pady=10, expand=True, fill="x")
    
    if opciones:
        _opcSeleccionada.set(opciones[0])
        cmb.pack(padx=10, pady=10, expand=True, fill="x")
    
    if esArchivo:
        extArchivos = [".js", ".env", ".json", ".py", ".html", ".css", ".txt"]
        _combo = ttk.Combobox(_top, values=tuple(extArchivos), style=f"{tipo}.TCombobox", textvariable=_extArch, state="readonly")
        _combo.current(0)
        _combo.pack(padx=10, pady=10, side="right", expand=True, fill="x")
        _extArch.trace_add("write", lambda *args: _valueCombo())
    
    botonOk =ttk.Button(_top, text="Aceptar", style=f"{tipo}.TButton", command=returnInput)
    botonOk.pack(padx=10, pady=10)
    
    _nomArch.trace_add("write", lambda *args: _validInput())
    _opcSeleccionada.trace_add("write", lambda *args: _validarSeleccion())
    _validInput()
    _validarSeleccion()
    centerWindow(_top)

def configureSyntax(textArea:tk.Text):
    """Configura la sintaxis de un area de texto.

    Args:
        textArea (tk.Text): _Area de texto a configurar_
    """
    getFont = str(textArea.cget("font")) if textArea.cget("font") else str("Consolas 10") # Obtener la fuente actual del widget
    getFont = getFont.replace(" ", ",") # Reemplazar los espacios por comas
    getFont = getFont.split(",") # Convertir la fuente en una lista
    
    font = []
    for element in getFont:
        if element.isdigit():
            font.append(int(element))  # Convertir los elementos numéricos a enteros y añadirlos a la lista
        else:
            font.append(element)  # Agregar los elementos no numéricos a la lista
    
    # Crear diferentes estilos
    textArea.tag_configure("tags", foreground="#5650FF", font=(font[0], font[1], "bold"))
    textArea.tag_configure("attributes", foreground="#68CE3E", font=(font[0], font[1], "bold"))
    textArea.tag_configure("selectors", foreground="#FF5656", font=(font[0], font[1], "bold"))
    textArea.tag_configure("properties", foreground="#FF56FF", font=(font[0], font[1], "bold"))
    textArea.tag_configure("values", foreground="#5650FF", font=(font[0], font[1], "bold"))
    textArea.tag_configure("boolean_values", foreground="#4B44FF", font=(font[0], font[1], "bold"))
    textArea.tag_configure("control_flow", foreground="#CE37F8", font=(font[0], font[1], "bold"))
    textArea.tag_configure("logical_operators", foreground="#FCFCFC", font=(font[0], font[1], "bold"))
    textArea.tag_configure("function_class_declarations", foreground="#CE37F8", font=(font[0], font[1], "bold"))
    textArea.tag_configure("exception_handling", foreground="#FCBC5C", font=(font[0], font[1], "bold"))
    textArea.tag_configure("import_statements", foreground="#CE37F8", font=(font[0], font[1], "bold"))
    textArea.tag_configure("context_management", foreground="#B598BD", font=(font[0], font[1], "bold"))
    textArea.tag_configure("scope_declarations", foreground="#875E93", font=(font[0], font[1], "bold"))
    textArea.tag_configure("others", foreground="#A8A4A4", font=(font[0], font[1], "bold"))
    textArea.tag_configure("comment", foreground="#A4FA81", font=(font[0], font[1], "italic"))
    textArea.tag_configure("string", foreground="#DFC57B", font=(font[0], font[1], "bold"))
    textArea.tag_configure("error", foreground="#B72A2B", font=(font[0], font[1], "bold"))
    textArea.tag_configure("info", foreground="#7A77C2", font=(font[0], font[1], "bold"))
    textArea.tag_configure("warning", foreground="#DCA858", font=(font[0], font[1], "bold"))

def applySintax(textArea:tk.Text, syntax:Literal["python", "javascript", "html", "css", "basic", "disabled"]="python"):
    """Aplica la sintaxis destacada a un area de texto.

    Args:
        textArea (tk.Text): _Area de texto a la que se le aplicara la sintaxis destacada_
        syntax (Literal[&quot;python&quot;, &quot;javascript&quot;], optional): _Tipo de sintaxis a aplicar_. Defaults to "python".
    """
    
    if syntax == "python":
        keywords = keywordsPY
    elif syntax == "javascript":
        keywords = keywordsJS
    elif syntax == "html":
        keywords = keywordsHTML
    elif syntax == "css":
        keywords = keywordsCSS
    elif syntax == "basic":
        keywords = {}
    else:
        return
        
    # Eliminar los resaltados actuales
    for tag in keywords.keys():
        textArea.tag_remove(tag, "1.0", tk.END)
    textArea.tag_remove("comment", "1.0", tk.END)
    textArea.tag_remove("string", "1.0", tk.END)
    
    # Recorrer cada tipo de keyword
    for tag, words in keywords.items():
        for word in words:
            # Obtener todo el texto del widget
            text_content = textArea.get("1.0", tk.END)

            # Utilizar re.finditer() para buscar todas las ocurrencias de la palabra en el texto
            for match in re.finditer(rf'\b{word}\b', text_content):
                start_pos = match.start()  # Posición de inicio de la coincidencia
                end_pos = match.end()  # Posición de final de la coincidencia
                
                # Convertir las posiciones a índices de Tkinter
                start_idx = f"1.0 + {start_pos} chars"
                end_idx = f"1.0 + {end_pos} chars"
                
                # Aplicar el tag correspondiente
                textArea.tag_add(tag, start_idx, end_idx)

    # Resaltar comentarios
    start_idx = "1.0"
    while True:
        # Buscar la posición inicial del comentario
        start_idx = textArea.search(
            r'#.*' if syntax == "python" else r'//.*' if syntax == "javascript" else r'<!--.*-->', 
            start_idx, stopindex=tk.END, regexp=True
        )
        
        if not start_idx:
            break
        
        # Obtener la posición final del comentario (final de la línea)
        end_idx = textArea.index(f"{start_idx} lineend")
        # Aplicar el tag "comment" para resaltar el comentario
        textArea.tag_add("comment", start_idx, end_idx)
        # Mover el índice de inicio hacia adelante para evitar bucle infinito
        start_idx = textArea.index(f"{end_idx} + 1c")

    # Ejemplo de aplicación de tags para resaltar cadenas de texto
    text_content = textArea.get("1.0", tk.END)  # Obtener todo el texto del widget

    # Usar re.finditer() para encontrar todas las cadenas de texto (entre comillas simples o dobles)
    for match in re.finditer(r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'', text_content):
        start_pos = match.start()  # Posición de inicio de la coincidencia
        end_pos = match.end()  # Posición de final de la coincidencia

        # Convertir las posiciones a índices que Tkinter pueda entender
        start_idx = f"1.0 + {start_pos} chars"
        end_idx = f"1.0 + {end_pos} chars"

        # Aplicar el tag "string" al texto encontrado
        textArea.tag_add("string", start_idx, end_idx)

def getFileExtension(file:str):
    """Obtiene la extension de un archivo.

    Args:
        file (str): _Nombre del archivo_

    Returns:
        _str_: _Extension del archivo_
    """
    return os.path.splitext(file)[1]

def getFileName(file:str):
    """Obtiene el nombre de un archivo.

    Args:
        file (str): _Nombre del archivo_

    Returns:
        _str_: _Nombre del archivo_
    """
    return os.path.splitext(file)[0]

def getFileNameAndExtension(file:str):
    """Obtiene el nombre y la extension de un archivo.

    Args:
        file (str): _Nombre del archivo_

    Returns:
        _tuple_: _Nombre y extension del archivo_
    """
    return os.path.splitext(file)