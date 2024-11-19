import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 3000))
server.listen(1)
print("Esperando conexión...")
conn, addr = server.accept()
print(f"Conexión desde {addr}")

while True:
    data = conn.recv(1024)
    print(f"Recibido: {data.decode("utf-8")}")
    if not data or data.decode("utf-8") == "exit":
        break
    
    entrada = input("Ingrese mensaje: ")
    conn.sendall(entrada.encode("utf-8"))  
    
conn.sendall(b"Respuesta desde el servidor")
conn.close()
