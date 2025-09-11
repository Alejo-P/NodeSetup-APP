import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import ImageTk

from config.constants import ASSETS_DIR
from utils.functions import load_image_tk

class Icons:
    # Almacenamiento de imágenes
    home_icon = None
    download_icon = None
    code_fork_icon = None
    checkbox_icon = None
    cog_icon = None
    timer_icon = None
    play_icon = None
    check_icon = None
    error_icon = None
    magnifier_icon = None
    warning_icon = None
    info_icon = None
    add_icon = None
    minus_icon = None
    trash_icon = None
    user_icon = None
    mail_icon = None
    edit_icon = None
    link_icon = None
    prompt_icon = None
    table_refresh_icon = None
    table_done_icon = None
    cloud_refresh_icon = None
    cloud_done_icon = None
    question_mark_icon = None

    @classmethod
    def load_icons(cls):
        # Cargar y redimensionar las imágenes
        cls.home_icon = load_image_tk(
            Path(ASSETS_DIR) / "homeIcon.png", 
            (50, 50)
        )
        cls.download_icon = load_image_tk(
            Path(ASSETS_DIR) / "downloadsIcon.png", 
            (50, 50)
        )
        cls.code_fork_icon = load_image_tk(
            Path(ASSETS_DIR) / "codeForkIcon.png", 
            (50, 50)
        )
        cls.checkbox_icon = load_image_tk(
            Path(ASSETS_DIR) / "checkboxIcon.png", 
            (50, 50)
        )
        cls.cog_icon = load_image_tk(
            Path(ASSETS_DIR) / "cogIcon.png", 
            (50, 50)
        )
        cls.timer_icon = load_image_tk(
            Path(ASSETS_DIR) / "timerIcon.png", 
            (20, 20),
            invert=True
        )
        cls.play_icon = load_image_tk(
            Path(ASSETS_DIR) / "playIcon.png", 
            (20, 20),
            invert=True
        )
        cls.check_icon = load_image_tk(
            Path(ASSETS_DIR) / "checkIcon.png", 
            (20, 20),
            invert=True
        )
        cls.error_icon = load_image_tk(
            Path(ASSETS_DIR) / "errorIcon.png", 
            (20, 20),
            invert=True
        )
        cls.magnifier_icon = load_image_tk(
            Path(ASSETS_DIR) / "magnifierIcon.png", 
            (20, 20),
            invert=True
        )
        cls.warning_icon = load_image_tk(
            Path(ASSETS_DIR) / "warningIcon.png", 
            (20, 20),
            invert=True
        )
        cls.info_icon = load_image_tk(
            Path(ASSETS_DIR) / "infoIcon.png", 
            (20, 20),
            invert=True
        )
        cls.add_icon = load_image_tk(
            Path(ASSETS_DIR) / "addIcon.png", 
            (20, 20),
            invert=True
        )
        cls.minus_icon = load_image_tk(
            Path(ASSETS_DIR) / "minusIcon.png", 
            (20, 20),
            invert=True
        )
        cls.trash_icon = load_image_tk(
            Path(ASSETS_DIR) / "trashIcon.png", 
            (20, 20),
            invert=True
        )
        cls.user_icon = load_image_tk(
            Path(ASSETS_DIR) / "userIcon.png", 
            (20, 20),
            invert=True
        )
        cls.mail_icon = load_image_tk(
            Path(ASSETS_DIR) / "mailIcon.png", 
            (20, 20),
            invert=True
        )
        cls.edit_icon = load_image_tk(
            Path(ASSETS_DIR) / "editIcon.png", 
            (20, 20),
            invert=True
        )
        cls.link_icon = load_image_tk(
            Path(ASSETS_DIR) / "linkIcon.png", 
            (20, 20),
            invert=True
        )
        cls.prompt_icon = load_image_tk(
            Path(ASSETS_DIR) / "promptIcon.png", 
            (20, 20),
            invert=True
        )
        cls.table_refresh_icon = load_image_tk(
            Path(ASSETS_DIR) / "tableRefreshIcon.png", 
            (20, 20),
            invert=True
        )
        cls.table_done_icon = load_image_tk(
            Path(ASSETS_DIR) / "tableDoneIcon.png", 
            (20, 20),
            invert=True
        )
        cls.cloud_refresh_icon = load_image_tk(
            Path(ASSETS_DIR) / "cloudRefreshIcon.png", 
            (20, 20),
            invert=True
        )
        cls.cloud_done_icon = load_image_tk(
            Path(ASSETS_DIR) / "cloudDoneIcon.png", 
            (20, 20),
            invert=True
        )
        cls.question_mark_icon = load_image_tk(
            Path(ASSETS_DIR) / "questionmarkIcon.png", 
            (20, 20),
            invert=True
        )

    @classmethod
    def _get_icons(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_') and isinstance(v, ImageTk.PhotoImage)}


if __name__ == "__main__":
    # Crear una ventana de prueba
    root = tk.Tk()
    root.title("Prueba de íconos")
    
    def _on_change_icon(event):
        icon_label.config(image=Icons._get_icons()[selected_icon.get()])

    selected_icon = tk.StringVar()
    
    # Cargar los íconos una vez
    Icons.load_icons()

    list_icons = list(Icons._get_icons().keys())
    
    frame_combobox = ttk.LabelFrame(root, text="Seleccionar ícono")
    frame_combobox.pack(padx=10, pady=10, fill="x", ipadx=5, ipady=5)

    icons_combobox = ttk.Combobox(frame_combobox, values=list_icons, textvariable=selected_icon, state="readonly")
    icons_combobox.set(list_icons[0])
    selected_icon.set(list_icons[0])
    icons_combobox.pack()
    icons_combobox.bind("<<ComboboxSelected>>", _on_change_icon)

    tk.Label(frame_combobox, text="Total de iconos:").pack(side="left", padx=5)
    tk.Label(frame_combobox, text=str(len(list_icons))).pack(side="left")

    # Mostrar los íconos
    ttk.Label(root, text="Seleccione un ícono para ver su representación:").pack(pady=10)
    icon_label = tk.Label(root, text="Ícono aparecerá aquí", image=Icons._get_icons()[selected_icon.get()])
    icon_label.pack()
    
    root.mainloop()