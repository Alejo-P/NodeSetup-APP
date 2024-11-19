from plyer import notification
import time

if __name__ == "__main__":
    # Mostrar notificación
    notification.notify( #type: ignore
        title = "¡Hora de trabajar!",
        message = "¡Es hora de trabajar! ¡No te distraigas!",
        app_name = "Work Timer",
        timeout = 10
    )
    
    # Esperar 10 segundos
    time.sleep(10)