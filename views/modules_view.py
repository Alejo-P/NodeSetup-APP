import tkinter as tk
import webbrowser
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import INFO, OUTLINE, CENTER, W, NSEW, LIGHT, SECONDARY, WARNING, EW
from CustomWidgets import ScrolledFrame, MultiChoice
from Tools import ToolTip
from utils.icons import Icons
from config.vars import npm_args_list

class ModulesView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self._setup_view()
        self._create_widgets()
        
        for columna in range(self.grid_size()[0]):
            self.grid_columnconfigure(columna, weight=1)
            
        self.grid_rowconfigure(0, weight=1)

    def _setup_view(self):
        self._encabezado = [
            "Seleccionar",
            "Nombre",
            "Argumentos",
            "Version",
            "Acciones"
        ]
        self._widgets = []
        self.npm_path = ""
        self.show_commands_without_selecting_modules = False

    def _create_widgets(self):
        self._scrolledModulos = ScrolledFrame(self, "warning-rounded")

        # Añadir una barra de progreso
        self._progress_bar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=280, bootstyle="warning") # type: ignore
        self._msg_estado = ttk.Label(self, text="Para ver los modulos disponibles, inicie la carga!")
        self._msg_estado.grid(row=0, column=0, padx=5, pady=2)

        self._frame_btn = ttk.Frame(self)
        self._frame_btn.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        self._action_btn = ttk.Button(
            self._frame_btn,
            text="Cargar módulos",
            bootstyle=(INFO, OUTLINE) # type: ignore
        )
        self._action_btn.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW, ipadx=10)
        self._frame_btn.grid_columnconfigure(0, weight=1)
        self._frame_btn.grid_rowconfigure(0, weight=1)
        
    def start_loading(self):
        for widget_list in self._widgets:
            for widget in widget_list:
                widget.grid_forget()
        self._widgets.clear()
        self._scrolledModulos.clear_widgets()
        self._scrolledModulos.update_idletasks()
        self._scrolledModulos.grid_forget()
        
        self._msg_estado.config(text="Cargando módulos de NPM... No cierre la ventana!")
        self._action_btn.config(text="Cargando...", state="disabled")
        self._msg_estado.grid(row=0, column=0, padx=5, pady=2)
        self._progress_bar.grid(row=1, column=0, columnspan=len(self._encabezado), padx=5, pady=10)
        self._progress_bar.start()
        self._frame_btn.grid_forget()

    def stop_loading(self):
        self._progress_bar.stop()
        self._progress_bar.grid_forget()
        self._msg_estado.grid_forget()

        self._action_btn.config(text="Restablecer selección", state="disabled")
        self._frame_btn.grid(row=1, column=0, padx=5, pady=5, sticky=NSEW, ipadx=10)
        
        for columna in range(self._frame_btn.grid_size()[0]):
            self._frame_btn.grid_columnconfigure(columna, weight=1)
        for fila in range(self._frame_btn.grid_size()[1]):
            self._frame_btn.grid_rowconfigure(fila, weight=1)

    def populate_modules(self, modules_widgets):
        if not self._widgets:
            for dic in modules_widgets:
                check_usar = ttk.Checkbutton(self._scrolledModulos, variable=dic["usar"], bootstyle="success-round-toggle", padding=4) # type: ignore
                
                label_nombre = ttk.Label(self._scrolledModulos, text=dic["nombre"], bootstyle=LIGHT, padding=4) # type: ignore

                multiChoice_argumento = MultiChoice(self._scrolledModulos, npm_args_list, dic["argumento"],  border=1, relief="solid") # type: ignore

                combo_version = ttk.Combobox(self._scrolledModulos, values=dic["versiones"], textvariable=dic["version"], state="readonly", bootstyle=SECONDARY, width=25) # type: ignore
                
                frame_actions = ttk.Frame(self._scrolledModulos)
                label_prompt = ttk.Label(frame_actions, image=Icons.info_icon, anchor=CENTER, bootstyle=INFO, padding=4) # type: ignore
                #label_prompt.bind("<Button-1>", lambda e, dic=dic: print(f"npm install {dic['nombre'].lower()}@{dic['version'].get()} {dic['argumento'].get().replace(',', '')}"))
                label_prompt.bind("<Button-1>", lambda e, dic=dic: self._on_copy_command(f"{self.npm_path} install {dic['nombre'].lower()}@{dic['version'].get()} {dic['argumento'].get().replace(',', '')}"))
                ToolTip(label_prompt, text="Ver/copiar comando de instalación", delay_hide=5000)
                label_prompt.grid(row=0, column=0, padx=2)
                
                label_help = ttk.Label(frame_actions, image=Icons.question_mark_icon, anchor=CENTER, bootstyle=INFO, padding=4) # type: ignore
                label_help.bind("<Button-1>", lambda e, dic=dic: webbrowser.open(f"https://www.npmjs.com/package/{dic['nombre'].lower()}"))
                ToolTip(label_help, text=f"Ver documentación (https://www.npmjs.com/package/{dic['nombre'].lower()})", delay_hide=5000)
                label_help.grid(row=0, column=1, padx=2)
                
                frame_actions.grid_columnconfigure(0, weight=1)
                frame_actions.grid_columnconfigure(1, weight=1)
                frame_actions.grid_rowconfigure(0, weight=1)
                
                self._widgets.append([check_usar, label_nombre, multiChoice_argumento, combo_version, frame_actions])

    def show_widgets(self):
        try:
            for i, txt in enumerate(self._encabezado):
                ttk.Label(self._scrolledModulos, text=txt, anchor="center").grid(row=0, column=i, padx=5, pady=5, sticky=NSEW)

            ttk.Separator(self._scrolledModulos, orient="horizontal", bootstyle="warning").grid(row=1, column=0, columnspan=len(self._encabezado), sticky="ew") # type: ignore
            
            for i, widget_list in enumerate(self._widgets, 2):
                for j, widget in enumerate(widget_list):
                    if isinstance(widget, (ttk.Checkbutton, ttk.Combobox, MultiChoice)):
                        widget.grid(row=i, column=j % len(self._encabezado), padx=5, pady=2)
                    elif isinstance(widget, ttk.Label):   
                        widget.grid(
                            row=i, column=j % len(self._encabezado), 
                            padx=5, pady=2, 
                            sticky=W if not str(widget.cget("image")) else ""
                        )
                    else:
                        widget.grid(row=i, column=j % len(self._encabezado), padx=5, pady=2, sticky=NSEW)
            
            self._scrolledModulos.update_idletasks()
            self._scrolledModulos.grid(row=0, column=0, padx=5, pady=5, sticky=NSEW)

            columnas, filas = self._scrolledModulos.grid_size()
            for columna in range(columnas):
                self._scrolledModulos.grid_columnconfigure(columna, weight=1)

            for fila in range(filas):
                self._scrolledModulos.grid_rowconfigure(fila, weight=1)
        except tk.TclError as e:
            print(f"Error al mostrar widgets: {e}")
        
    def on_copy_command(self, command):
        if not self.show_commands_without_selecting_modules:
            self._on_copy_command(command)
            return
        
        if hasattr(self, 'popUp_prompt') and self.popUp_prompt.winfo_exists():
            self.popUp_prompt.lift()  # Traer la ventana al frente
            return
        
        self.popUp_prompt = tk.Toplevel(self)
        self.popUp_prompt.title("Comando copiado")
        self.popUp_prompt.geometry("400x100")
        self.popUp_prompt.resizable(False, False)
        self.popUp_prompt.protocol("WM_DELETE_WINDOW", self.popUp_prompt.destroy)
        self.popUp_prompt.transient(self) # type: ignore  # Mantener la ventana encima de la principal
        self.popUp_prompt.grab_set() # Evita interacción con la ventana principal
        
        entry = ttk.Entry(self.popUp_prompt)
        entry.insert(0, command)
        entry.config(state="readonly", justify=CENTER)
        entry.grid(row=0, column=0, columnspan=2, padx=10, sticky=NSEW)
        entry.focus()
        
        scroll_entry = ttk.Scrollbar(self.popUp_prompt, orient="horizontal", command=entry.xview, bootstyle="info-round") # type: ignore
        entry.config(xscrollcommand=scroll_entry.set)
        scroll_entry.grid(row=1, column=0, columnspan=2, padx=10, sticky=EW)
        
        button = ttk.Button(self.popUp_prompt, text="Cerrar", command=self.popUp_prompt.destroy)
        button.grid(row=2, column=0, pady=(0, 10))
        
        button_copy = ttk.Button(self.popUp_prompt, text="Copiar al portapapeles", command=lambda: self._on_copy_command(command))
        button_copy.grid(row=2, column=1, pady=(0, 10))
        
        for columna in range(self.popUp_prompt.grid_size()[0]):
            self.popUp_prompt.grid_columnconfigure(columna, weight=1)
            
        for fila in range(self.popUp_prompt.grid_size()[1]):
            self.popUp_prompt.grid_rowconfigure(fila, weight=1)
        self._center_window(self.popUp_prompt)
        
    def _on_copy_command(self, command):
        self.clipboard_clear()
        self.clipboard_append(command)
        self.update()
        messagebox.showinfo("Comando copiado", f"El comando ha sido copiado al portapapeles:\n\n{command}", parent=self)
        
    def _center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def show_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def show_info(self, mensaje):
        messagebox.showinfo("Información", mensaje)

    def show_warning(self, mensaje):
        messagebox.showwarning("Advertencia", mensaje)

    def ask_user_confirmation(self, title, message):
        return messagebox.askyesno(title, message)