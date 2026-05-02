from flask import Flask, request, jsonify
import pandas
import logging
import sqlite3
from datetime import datetime

app = Flask(__name__)
TOKENS_VALIDOS = {
    "token-identidad": "gestor-identidad",
    "token-pagos": "Pasarela_Pagos",
    "token-centinela": "Centinela_Servidor"
}
logging.basicConfig(
    filename='logs_recibidos.log',
    level=logging.INFO,
    format='%(message)s' # Guardamos el JSON crudo
)

DB_NAME = 'logs_servidor.db'

def guardar_en_base_de_datos(lista_datos):
    """Maneja la persistencia de uno o varios logs de forma eficiente."""
    # Si recibimos un solo diccionario, lo convertimos en lista para unificar el proceso
    if isinstance(lista_datos, dict):
        lista_datos = [lista_datos]
        
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        insert = '''
            INSERT INTO logs (occurred_at, received_at, service, severity, message)
            VALUES (?, ?, ?, ?, ?)
        '''

        valores = [
            (
                d.get('timestamp'),
                datetime.utcnow().isoformat(),
                d.get('service'),
                d.get('level'),
                d.get('message')
            ) for d in lista_datos
        ]
        
        cursor.executemany(insert, valores) # Inserción masiva
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Error crítico al insertar en DB: {e}")
        raise e

@app.route('/logs', methods=['POST'])
def recibir_logs():
    auth_header = request.headers.get('Authorization')
    # 1. Extraer el token del string "Bearer [TOKEN]"
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Quién sos, bro?"}), 401
    
    token_cliente = auth_header.split(" ")[1]

    # 2. Verificar si la llave existe en el diccionario
    if token_cliente not in TOKENS_VALIDOS:
        return jsonify({"error": "Quién sos, bro?"}), 401
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "Cuerpo vacío"}), 400

        # Procesamos la inserción (ya sea lista o dict)
        guardar_en_base_de_datos(datos)
        
        # Calculamos la cantidad para el mensaje
        cantidad = len(datos) if isinstance(datos, list) else 1
        
        # --- ESTE ES EL CAMBIO CLAVE: RESPUESTA UNIFICADA ---
        return jsonify({
            "status": "success",
            "message": "Logs procesados exitosamente",
            "info": {
                "cantidad": cantidad,
                "server_time": datetime.now().isoformat()
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def consultar_logs():
    # 1. Capturar parámetros de la URL
    # Ejemplo: /logs?service=gestor-identidad&level=ERROR
    service = request.args.get('service')
    level = request.args.get('level')
    ts_start = request.args.get('timestamp_start')
    ts_end = request.args.get('timestamp_end')

    try:
        conexion = sqlite3.connect(DB_NAME)
        conexion.row_factory = sqlite3.Row  # Esto permite acceder por nombre de columna
        cursor = conexion.cursor()

        # 2. Construir la consulta base
        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        # 3. Agregar filtros dinámicamente
        if service:
            query += " AND service = ?"
            params.append(service)
        if level:
            query += " AND severity = ?"
            params.append(level)
        if ts_start and ts_end:
            query += " AND occurred_at BETWEEN ? AND ?"
            params.append(ts_start)
            params.append(ts_end)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 4. Formatear resultados como lista de diccionarios
        resultados = [dict(row) for row in rows]
        df_query=pandas.read_sql_query(query, conexion)
        print(df_query)
        conexion.close()
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)