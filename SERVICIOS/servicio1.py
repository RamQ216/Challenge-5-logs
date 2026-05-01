from estructura import LogSimulator

class GestorIdentidad(LogSimulator):
    def __init__(self, ruta, token):
        # Llamamos al constructor del padre
        super().__init__(ruta, "gestor-identidad")

        self.sesion_abierta.headers.update({
            "Authorization": f"Bearer {token}"
        })
        self.eventos_disponibles = [
            {"nivel": "INFO", "mensaje": "Usuario inició sesión"},
            {"nivel": "WARNING", "mensaje": "Intento de login fallido"},
            {"nivel": "CRITICAL", "mensaje": "Ataque por fuerza bruta detectado"},
            {"nivel": "INFO", "mensaje": "Cierre de sesión exitoso"}
        ]

if __name__ == "__main__":
    URL = "http://127.0.0.1:5000/logs"
    app = GestorIdentidad(URL,"admin123")
    app.simulacion()
