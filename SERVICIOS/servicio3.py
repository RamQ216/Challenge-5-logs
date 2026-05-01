from estructura import LogSimulator


class Centinela_Servidor(LogSimulator):
    def __init__(self, ruta, token):
        # Llamamos al constructor del padre
        super().__init__(ruta, "Centinela_Servidor")
        self.sesion_abierta.headers.update({
            "Authorization": f"Bearer {token}"
        })
        self.eventos_disponibles = [
            {"nivel": "INFO", "mensaje": "Estado del sistema: Saludable"},
            {"nivel": "INFO", "mensaje": "Sincronización de reloj NTP completada"},
            {"nivel": "WARNING", "mensaje": "Uso de memoria RAM por encima del 75%"},
            {"nivel": "WARNING", "mensaje": "Espacio en disco bajo en la partición /var/log"},
            {"nivel": "ERROR", "mensaje": "Fallo en el ventilador del CPU - Aumento de temperatura detectado"},
            {"nivel": "ERROR", "mensaje": "Proceso zombie detectado en el kernel"},
            {"nivel": "CRITICAL", "mensaje": "Temperatura del procesador en umbral de riesgo (95°C)"},
            {"nivel": "CRITICAL", "mensaje": "Error de segmentación en el disco principal - Posible fallo de hardware"}
        ]
        

if __name__ == "__main__":
    URL = "http://127.0.0.1:5000/logs"
    app = Centinela_Servidor(URL,'admin123')
    app.simulacion()