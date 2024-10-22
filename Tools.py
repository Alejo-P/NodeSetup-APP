from typing import Literal
import ttkbootstrap as ttk
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        styles = ttk.Style()
        styles.configure("dark.TLabel", background="#3E556A", foreground="white")

    def setText(self, text):
        self.text = text

    def showtip(self, direction: Literal["n", "s", "e", "w"] = "n"):
        "Display text in tooltip window"
        if self.tipwindow or not self.text:
            return
        
        # Obtener posición y dimensiones del widget
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()

        # Calcular la posición del tooltip según la dirección
        if direction == "n":  # Arriba
            x = (widget_x + widget_width // 2) + 30  # Centrar horizontalmente
            y = widget_y - 30  # Ajustar un poco arriba
        elif direction == "s":  # Abajo
            x = widget_x + widget_width // 2
            y = widget_y + widget_height + 10  # Ajustar un poco abajo
        elif direction == "e":  # Derecha
            x = widget_x + widget_width + 10  # Ajustar a la derecha
            y = widget_y + widget_height // 2 - 20  # Centrar verticalmente
        elif direction == "w":  # Izquierda
            x = widget_x - 10  # Ajustar a la izquierda
            y = widget_y + widget_height // 2 - 20  # Centrar verticalmente

        # Crear la ventana emergente para el tooltip
        self.tipwindow = tw = ttk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Crear el contenido del tooltip
        label = ttk.Label(
            tw, text=self.text, anchor=tk.CENTER, relief=tk.SOLID, borderwidth=1, style="dark.TLabel"
        )
        label.pack(ipadx=7, ipady=7)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
