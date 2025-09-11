from tkinter import ttk
import tkinter as tk
from utils.icons import Icons

# Ventana principal
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Treeview con Checkboxes")
        
        # Cargar los íconos una vez
        Icons.load_icons()
        
        # Crear referencias a las imágenes en la instancia de la ventana
        self.check_icon = Icons.check_icon
        self.uncheck_icon = Icons.uncheck_icon
        
        # Crear el Treeview
        columns = ("ID", "Name", "Description")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings", height=10)  # Activa la columna #0
        
        # Configurar encabezados
        self.tree.heading("#0", text="Check")  # Columna implícita para los checkboxes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        
        # Ajustar tamaños de columnas
        self.tree.column("#0", width=50, anchor="center")  # Para mostrar checkboxes
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=100, anchor="center")
        self.tree.column("Description", width=150, anchor="w")
        
        # Diccionario para almacenar estados de los checkboxes
        self.checked_states = {}
        
        # Agregar filas al Treeview
        data = [
            [1, "Apple", "This is an apple", False],
            [2, "Banana", "This is a banana", True],
            [3, "Cherry", "This is a cherry", False],
            [4, "Date", "This is a date", True],
        ]
        
        for row in data:
            item_id = self.tree.insert("", "end", text="", image=self.check_icon if row[3] else self.uncheck_icon, values=row[:3])
            self.checked_states[item_id] = row[3]
        
        # Evento para cambiar estado del checkbox
        self.tree.bind("<Button-1>", self.toggle_check)
        
        # Empaquetar el Treeview
        self.tree.pack(expand=True, fill="both")
        
        ttk.Label(self, text="Haz clic en la columna 'Check' para cambiar el estado del checkbox").pack()
        
        #Prueba de las imagenes
        check_label = tk.Label(self, image=Icons.check_icon)
        check_label.pack()
        
        uncheck_label = tk.Label(self, image=Icons.uncheck_icon)
        uncheck_label.pack()
        
    def toggle_check(self, event):
        # Obtener el item seleccionado
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item_id or column != "#0":  # Verifica que sea la columna #0
            return
        
        # Cambiar el estado del checkbox
        current_state = self.checked_states[item_id]
        new_state = not current_state
        self.checked_states[item_id] = new_state
        self.tree.item(item_id, image=self.check_icon if new_state else self.uncheck_icon)
        print(f"Item {item_id} checked: {new_state} image: {self.tree.item(item_id, 'image')}")
        

if __name__ == "__main__":
    app = App()
    app.mainloop()
