import requests#para hacer las peticiones o envios
import uuid#para generar ids
import time#para tener intervalos de envio
import logging#para configurar nuestros logs
import random#para iterar en la lista de logs
from datetime import datetime#para atrapar el tiempo exacto

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#definimos a partir de que nivel queremos ver y de que manera queremos ver en este caso fecha-nivel-mensaje
token=None
class LogSimulator:#creamos una clase padre que simulara el envio de logs para las clases hijas
    def __init__(self, ruta, nombre_servicio):
        self.ruta = ruta#le decimos en que servidor se va conectar
        self.nombre_servicio = nombre_servicio#el nombre del servicio
        self.sesion_abierta = requests.Session()#realizamos una conexion persistente
        self.sesion_abierta.headers.update({#creamos un token especifico para cada servicio
            "Authorization": f"Bearer {token}"
        })
        self.servicio_run = True#indicador de on
        self.eventos_disponibles = []#diccionario para clases hijas 

    def _generar_logs(self):#generamos los logs con el formato json
        evento = random.choice(self.eventos_disponibles)#iteramos entr los posibles eventos
        
        return {#nuestro log
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.nombre_servicio,
            "level": evento["nivel"],
            "message": evento["mensaje"],
            "metadata": {
                "runtime": "python3.10",
                "region": "py-central-1"
            }
        }

    def envio_logs(self):# definimos a donde queremos enviar,lo que vamos a enviar y el teimpo de espera
        logs = self._generar_logs()#instanciamos el metodo generar logs 
        try:
            response = self.sesion_abierta.post(self.ruta, json=logs, timeout=5)#realizamos un envio a el servidor con 5 de espera y el formato json
            response.raise_for_status()#verificamos el estado 
            logging.info(f"Enviado: {logs['id']} | Estado: {response.status_code}")#mostramos el id y la repsuta del server
        except Exception as e:#en caso de error informamos el causante
            logging.error(f"Fallo en el envío: {e}")

    def simulacion(self):#enviamos los logs con un intervalo de un segundo
        logging.info(f"Iniciando simulador: {self.nombre_servicio}")#indicamos que servicio es
        try:#llamamos a los metodos en un bucle y solo se rompan con un ctl+c
            while self.servicio_run:
                self.envio_logs()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):#nuestro cierre
        self.servicio_run = False 
        self.sesion_abierta.close()
        logging.info(f"Servicio {self.nombre_servicio} detenido.")