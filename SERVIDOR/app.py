from flask import Flask, request, jsonify
import logging
import sqlite3
from datetime import datetime

app = Flask(__name__)


logging.basicConfig(
    filename='logs_recibidos.log',
    level=logging.INFO,
    format='%(message)s' # Guardamos el JSON crudo
)

DB_NAME = 'logs_servidor.db'

def guardar_en_base_de_datos(datos):
    """Función auxiliar para manejar la persistencia en SQLite."""
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        insert = '''
            INSERT INTO logs (occurred_at, received_at, service, severity, message)
            VALUES (?, ?, ?, ?, ?)
        '''

        valores = (
            datos.get('timestamp'),          # occurred_at
            datetime.utcnow().isoformat(),   # received_at (generado por el servidor)
            datos.get('service'),            # nombre del servicio
            datos.get('level'),              # severity
            datos.get('message')             # mensaje
        )
        
        cursor.execute(insert, valores)
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error crítico al insertar en DB: {e}")
        raise e

TOKEN_SECRETO = "admin123" # Define tu token aquí

@app.route('/logs', methods=['POST'])
def recibir_logs():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {TOKEN_SECRETO}":
        return jsonify({"status": "error", "message": "No autorizado"}), 401

    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"status": "error", "message": "Cuerpo vacío"}), 400
        logging.info(datos)
        if datos:
            guardar_en_base_de_datos(datos)
            return(f"[{datetime.now()}] Log Guardado - Servicio: {datos.get('service')}")


        
        return jsonify({"status": "success", "message": "Log autenticado y procesado"}), 201

    except Exception as e:
        print(f"Error procesando log: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)