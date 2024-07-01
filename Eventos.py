import re
import threading
import time
from tokenize import group


class Hilos:
    def __init__(self):
        self.hilo = None
    
    def createGroup(self):
        self.Threadsgroup = []
        return self.Threadsgroup
    
    def addToGroup(self, thread):
        self.Threadsgroup.append(thread) # Continuar con el agrupamiento de hilos

    def start(self):
        self.hilo = threading.Thread(target=self.run)
        self.hilo.start()

    def run(self):
        while True:
            print("Hilo en ejecución")
            time.sleep(1)

    def stop(self):
        self.hilo.join()
        print("Hilo detenido")