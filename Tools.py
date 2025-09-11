from typing import Literal
import ttkbootstrap as ttk
import tkinter as tk

class ToolTip:
    def __init__(
        self,
        widget,
        text="",
        position: Literal["n", "s", "e", "w"] = "n",
        autohide: bool = True,
        delay_hide: int = 4000
    ):
        """Tooltip widget for displaying helpful information.

        Args:
            widget (_type_): The widget to attach the tooltip to.
            text (str, optional): The text to display in the tooltip. Defaults to "".
            position (Literal[&quot;n&quot;, &quot;s&quot;, &quot;e&quot;, &quot;w&quot;], optional): The position of the tooltip relative to the widget. Defaults to "n".
            autohide (bool, optional): Whether to automatically hide the tooltip after a delay. Defaults to True.
            delayhide (int, optional): The delay in milliseconds before the tooltip is hidden. Defaults to 4000.
        """
        self._widget = widget
        self._text = text
        self._position = position
        self._autohide = autohide
        self._delayhide = delay_hide
        self._tipwindow = None
        self._id = None
        self.x = self.y = 0
        self._maxwidth = 250

        styles = ttk.Style()
        styles.configure("dark.TLabel", background="#3E556A", foreground="white")

        self._widget.bind("<Enter>", lambda e: self._showtip())
        self._widget.bind("<Leave>", lambda e: self._hidetip())

    def setText(self, text:str):
        self._text = text
        
    def setPosition(self, position: Literal["n", "s", "e", "w"]):
        self._position = position

    def setAutoHide(self, autohide:bool, delay_hide:int=4000):
        self._autohide = autohide
        self._delayhide = delay_hide

    def getPosition(self):
        return self._position

    def getText(self):
        return self._text or ""

    def getWidget(self):
        return self._widget

    def _showtip(self):
        "Display text in tooltip window"
        if self._tipwindow or not self._text:
            return
        
        # Obtener posición y dimensiones del widget
        widget_x = self._widget.winfo_rootx()
        widget_y = self._widget.winfo_rooty()
        widget_width = self._widget.winfo_width()
        widget_height = self._widget.winfo_height()

        # Crear la ventana emergente para el tooltip
        self._tipwindow = tw = ttk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)

        if self._widget.cget("state") == "disabled":
            tw.wm_attributes("-alpha", 0.6)
            if not self._text.endswith("\n(Deshabilitado)"):
                self._text += "\n(Deshabilitado)"
        else:
            tw.wm_attributes("-alpha", 0.9)
            self._text = self._text.replace("\n(Deshabilitado)", "")

        # Crear el contenido del tooltip
        label = ttk.Label(
            tw, text=self._text,
            anchor=tk.CENTER,
            relief=tk.SOLID,
            borderwidth=1,
            style="dark.TLabel",
            wraplength=self._maxwidth
        )
        label.pack(ipadx=7, ipady=7)
        
        # Forzar el cálculo de las dimensiones del tooltip
        tw.update_idletasks()
        tip_width = tw.winfo_reqwidth()
        tip_height = tw.winfo_reqheight()

        # Calcular la posición del tooltip según la dirección
        if self._position == "s":  # Abajo
            x = widget_x + (widget_width // 2) - (tip_width // 2)  # Centrar horizontalmente
            y = widget_y + widget_height + 10  # Ajustar un poco abajo
        elif self._position == "e":  # Derecha
            x = widget_x + widget_width + 10  # Ajustar a la derecha
            y = widget_y + (widget_height // 2) - (tip_height // 2)  # Centrar verticalmente
        elif self._position == "w":  # Izquierda
            x = widget_x - tip_width - 10  # Ajustar a la izquierda
            y = widget_y + (widget_height // 2) - (tip_height // 2)  # Centrar verticalmente
        else:  # Arriba (por defecto)
            x = widget_x + (widget_width // 2) - (tip_width // 2)  # Centrar horizontalmente
            y = widget_y - tip_height - 10  # Ajustar un poco arriba

        # Posicionar la ventana del tooltip
        tw.wm_geometry(f"+{x}+{y}")
        
        if self._autohide:
            self._id = self._widget.after(self._delayhide, self._hidetip)

    def _hidetip(self):
        if self._id:
            self._widget.after_cancel(self._id)
            self._id = None
            
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()
