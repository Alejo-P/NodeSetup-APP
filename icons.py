import tkinter as tk
import os
from PIL import Image, ImageTk

from Vars import ruta_assets
from Actions import loadImageTk

class Icons:
    # Almacenamiento de imágenes
    check_icon = None
    uncheck_icon = None

    @classmethod
    def load_icons(cls):
        # Cargar y redimensionar las imágenes
        cls.check_icon = loadImageTk(os.path.join(ruta_assets, "checkIcon.png"), 16, 16, resample=Image.Resampling.LANCZOS)
        cls.uncheck_icon = loadImageTk(os.path.join(ruta_assets, "errorIcon.png"), 16, 16, resample=Image.Resampling.LANCZOS)
        
if __name__ == "__main__":
    # Crear una ventana de prueba
    root = tk.Tk()
    root.title("Prueba de íconos")
    
    # Cargar los íconos una vez
    Icons.load_icons()
    
    # Mostrar los íconos
    check_label = tk.Label(root, image=Icons.check_icon)
    check_label.pack()
    
    uncheck_label = tk.Label(root, image=Icons.uncheck_icon)
    uncheck_label.pack()
    
    root.mainloop()
        
