import socket
import threading, queue
import ttkbootstrap as ttk

from CustomWidgets import ScrolledFrame

def send_message():
    message = entry.get()
    client.sendall(message.encode("utf-8"))
    entry.delete(0, "end")
    
    contenedor = ttk.LabelFrame(scrolled_frame, text="Cliente")
    ttk.Label(contenedor, text=message).pack(side="right", fill="x")
    scrolled_frame.add_widget(contenedor, column=1)
    
def check_messages_background():
    while True:
        response = client.recv(1024)
        mensajes_servidor.put(response.decode())
        if not response or response.decode() == "exit":
            break
        
def verificar_mensajes():
    try:
        mensaje = mensajes_servidor.get_nowait()
        contenedor = ttk.LabelFrame(scrolled_frame, text="Servidor")
        ttk.Label(contenedor, text=mensaje).pack(side="left", fill="x")
        scrolled_frame.add_widget(contenedor, column=0)
        scrolled_frame._canvas.yview_moveto(1) # Mover el scrollbar al final
        if not mensaje or mensaje == "exit":
            on_closing()
            return
        root.after(100, verificar_mensajes)
    except:
        root.after(100, verificar_mensajes)
        return

def on_closing():
    client.sendall(b"exit")
    client.close()
    root.destroy()


root = ttk.Window(
    title="Cliente",
    themename="minty",
)

# Establecer un tamaño inicial para la ventana y que no se redimencione
root.geometry("800x600")
root.resizable(False, False)


mensajes_servidor = queue.Queue()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 3000))
client.sendall(b"Hola desde el cliente")

scrolled_frame = ScrolledFrame(root)
scrolled_frame.pack(expand=True, fill="both")

# Establecer 2 columnas para el scrolled frame
scrolled_frame.columnconfigure(0, weight=1)
scrolled_frame.columnconfigure(1, weight=1)

entry = ttk.Entry(root)
entry.pack(side="left", expand=True, fill="x")
entry.bind("<Return>", lambda event: send_message())

button = ttk.Button(root, text="Enviar", command=send_message)
button.pack(side="right")

print("Conectado al servidor\n",
        f" - Dirección: {client.getpeername()}\n",
        f" - Dirección local: {client.getsockname()}")

root.protocol("WM_DELETE_WINDOW", on_closing)
threading.Thread(target=check_messages_background, daemon=True).start()
root.after(100, verificar_mensajes)

root.mainloop()

# while True:
#     response = client.recv(1024)
#     print(f"Respuesta: {response.decode()}")
#     if not response or response.decode() == "exit":
#         break
#     entrada = input("Ingrese mensaje: ")
#     client.sendall(entrada.encode("utf-8"))

#client.close()
