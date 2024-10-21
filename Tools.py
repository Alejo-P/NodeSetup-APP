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

    def showtip(self):
        "Display text in tooltip window"
        if self.tipwindow or not self.text:
            return
        
        # Obtener posición y dimensiones del widget
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_height = self.widget.winfo_height()

        # Calcular posición para centrar el tooltip verticalmente respecto al widget
        x = widget_x + self.widget.winfo_width() + 10  # Posicionar tooltip a la derecha
        y = (widget_y + widget_height // 2) - 20 # Centrar verticalmente

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
