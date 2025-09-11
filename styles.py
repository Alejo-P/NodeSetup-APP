from ttkbootstrap import Style
from tkinter.font import Font

def load_custom_styles():
    styles = Style()
    styles.configure(
        "Custom.TFrame",
        background="#3E556A"
    )

    styles.configure(
        "Response.TLabel",
        background="#526170"
    )
    
    styles.configure(
        "Custom.TLabel",
        background="#3E556A",
        foreground="white"
    )
    
    styles.configure(
        "Disabled.TLabel",
        background="#3E556A",
        foreground="gray"
    )
    
    styles.configure(
        "Selected.TLabel",
        background="#2B3E50",
        foreground="white"
    )
    
    styles.configure(
        "Warning.TLabel",
        background="#FFC107",
        foreground="black"
    )
    
    styles.configure(
        "Error.TLabel",
        background="#DC3545",
        foreground="white"
    )
    
    styles.configure(
        "Success.TLabel",
        background="#28A745",
        foreground="white"
    )
    
    styles.configure(
        "Info.TLabel",
        background="#17A2B8",
        foreground="white"
    )
    
    styles.configure(
        "Custom.TEntry",
        fieldbackground="#526170",   # fondo donde escribes
        foreground="white",          # color del texto
        bordercolor="#3E556A",       # borde por defecto
        lightcolor="#3E556A",        # borde claro (3D)
        darkcolor="#3E556A",         # borde oscuro (3D)
    )

    styles.map(
        "Custom.TEntry",
        bordercolor=[("focus", "#8ED46E")],  # azul cuando recibe foco
        lightcolor=[("focus", "#1E90FF")],
        darkcolor=[("focus", "#1E90FF")]
    )

    return styles