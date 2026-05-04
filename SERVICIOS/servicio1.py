from estructura import LogSimulator

class GestorIdentidad(LogSimulator):#generamos la clase hija
    def __init__(self, ruta, token):#definimos el token y ruta
        # Llamamos al constructor del padre
        super().__init__(ruta, "gestor-identidad")

        self.sesion_abierta.headers.update({#generamos el titulo de autorizacion
            "Authorization": f"Bearer {token}"
        })
        self.eventos_disponibles = [#indicamos los eventos posibles con su nivel referente a cada servicio
            {"nivel": "INFO", "mensaje": "Usuario inició sesión"},
            {"nivel": "WARNING", "mensaje": "Intento de login fallido"},
            {"nivel": "CRITICAL", "mensaje": "Ataque por fuerza bruta detectado"},
            {"nivel": "INFO", "mensaje": "Cierre de sesión exitoso"}
        ]

if __name__ == "__main__":#ejecutamos el script
    URL = "http://127.0.0.1:5000/logs"
    app = GestorIdentidad(URL,"token-identidad")#intanciamos la clase
    app.simulacion()#llamamos al metodo que envia los logs
