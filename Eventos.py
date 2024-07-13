import threading
import queue
import tkinter as tk
from tkinter import ttk

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._lista_widgets = []
        self._npm_path = "/path/to/npm"  # Reemplaza con tu ruta de npm
        self._idAfterBar2 = None

        modulos_button = ttk.Button(self, text="Abrir Ventana de Módulos", command=self.abrir_ventana_modulos)
        modulos_button.pack(pady=10)

    def abrir_ventana_modulos(self):
        modulos = tk.Toplevel(self)
        modulos.title("Escoge los módulos a instalar")
        modulos.resizable(0, 0)  # No redimensionable
        modulos.transient(self)

        encabezado_tabla = [
            "Seleccionar",
            "Nombre del módulo",
            "Argumento",
            "Versión",
            "Inst. Global"
        ]

        for i, texto in enumerate(encabezado_tabla):
            ttk.Label(modulos, text=texto).grid(row=0, column=i, padx=5, pady=2)

        ttk.Separator(modulos, orient="horizontal").grid(row=1, column=0, columnspan=len(encabezado_tabla), sticky="ew")

        progress_bar = ttk.Progressbar(modulos, orient='horizontal', mode='indeterminate', length=280, style="TProgressbar")
        progress_bar.grid(row=2, column=0, columnspan=len(encabezado_tabla), padx=5, pady=10)
        msg_estado = ttk.Label(modulos)
        msg_estado.grid(row=3, column=0, columnspan=len(encabezado_tabla), padx=5, pady=2)

        self._centrar_ventana(modulos)

        # Llamar a la función de actualización de módulos
        threading.Thread(target=self.update_modulos_ui, args=(msg_estado, progress_bar, modulos)).start()

    def update_modulos_ui(self, msg_estado, progress_bar, modulos):
        def CargarInfoModulos(listaModulos):
            for i, dic in enumerate(listaModulos, 1):
                if not dic["versiones"]:
                    versionesPaquetes = Ejecutar_comando([self._npm_path, "show", dic["nombre"].lower(), "versions", "--depth=0"])
                    if isinstance(versionesPaquetes, subprocess.CalledProcessError):
                        writeLog("ERROR", f"Error al obtener versiones de {dic['nombre']}: {versionesPaquetes}", CargarInfoModulos.__name__)
                        return
                    dic["versiones"] = list(ast.literal_eval(f"{versionesPaquetes.stdout.strip()}"))

                if not dic["usar"]:
                    dic["usar"] = tk.BooleanVar(value=False)
                if not dic["global"]:
                    dic["global"] = tk.BooleanVar(value=False)
                if not dic["argumento"]:
                    dic["argumento"] = tk.StringVar(value=listaArgumentos[0])
                if not dic["version"]:
                    dic["version"] = tk.StringVar(value=dic["versiones"][-1] if dic["versiones"] else "Ocurrió un error")

        def CrearWidgets(listaModulos):
            for i, dic in enumerate(listaModulos, 1):
                # Crear los widgets para cada módulo
                check_usar = ttk.Checkbutton(modulos, variable=dic["usar"], style="Custom.TCheckbutton")
                label_nombre = ttk.Label(modulos, text=dic["nombre"])
                entry_argumento = ttk.Combobox(modulos, values=listaArgumentos, textvariable=dic["argumento"])
                combo_version = ttk.Combobox(modulos, values=dic["versiones"], textvariable=dic["version"])
                check_global = ttk.Checkbutton(modulos, variable=dic["global"], style="Custom.TCheckbutton")

                self._lista_widgets.append([check_usar, label_nombre, entry_argumento, combo_version, check_global])

        def iniciar_carga():
            n_listas = 6
            progress_bar.start()
            msg_estado.config(text="Cargando módulos de NPM... No cierre la ventana!")

            Registro_hilos = []
            for sublistas in dividir_lista(lista_modulosNPM, n_listas):
                hilo = threading.Thread(target=CargarInfoModulos, args=(sublistas,))
                Registro_hilos.append(hilo)

            for hilo in Registro_hilos:
                hilo.start()

            for hilo in Registro_hilos:
                hilo.join()

            if progress_bar.winfo_exists() and msg_estado.winfo_exists():
                progress_bar.stop()
                progress_bar.grid_forget()
                msg_estado.grid_forget()

            CrearWidgets(lista_modulosNPM)
            self._centrar_ventana(modulos)

        # Llamar a iniciar_carga para empezar el proceso
        iniciar_carga()

    def _centrar_ventana(self, ventana):
        ventana.update_idletasks()
        ancho = ventana.winfo_width()
        alto = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# Función para dividir la lista en sublistas
def dividir_lista(lista, n):
    k, m = divmod(len(lista), n)
    return [lista[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

# Función de ejemplo para ejecutar un comando
def Ejecutar_comando(comando):
    pass  # Aquí iría la implementación real

# Función de ejemplo para escribir en un archivo de registro
def writeLog(level, message, func_name):
    print(f"[{level}] {func_name}: {message}")

# Ejemplo de lista de argumentos
listaArgumentos = ["arg1", "arg2", "arg3"]

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
