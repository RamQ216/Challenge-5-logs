from estructura import LogSimulator

class Pasarela_Pagos(LogSimulator):
    def __init__(self, ruta, token):
        # Llamamos al constructor del padre
        super().__init__(ruta, "Pasarela_Pagos")
        self.sesion_abierta.headers.update({
            "Authorization": f"Bearer {token}"
        })
        self.eventos_disponibles = [
            {"nivel": "INFO", "mensaje": "Transacción iniciada por el cliente"},
            {"nivel": "INFO", "mensaje": "Pago procesado exitosamente - Entidad: Bancard"},
            {"nivel": "WARNING", "mensaje": "Transacción rechazada: Fondos insuficientes"},
            {"nivel": "WARNING", "mensaje": "Monto de transacción excede el límite permitido"},
            {"nivel": "ERROR", "mensaje": "Error de comunicación con el procesador de tarjetas"},
            {"nivel": "ERROR", "mensaje": "Firma digital de la transacción inválida"},
            {"nivel": "CRITICAL", "mensaje": "Fallo total de conexión con el nodo de pagos regional"},
            {"nivel": "CRITICAL", "mensaje": "Detección de posible duplicidad de transacción (Replay Attack)"}
        ]
        

if __name__ == "__main__":
    URL = "http://127.0.0.1:5000/logs"
    app = Pasarela_Pagos(URL,'admin123')
    app.simulacion()