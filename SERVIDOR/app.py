from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
TOKENS_VALIDOS = {
    "token-identidad": "gestor-identidad",
    "token-pagos": "Pasarela_Pagos",
    "token-centinela": "Centinela_Servidor"
}


DB_NAME = 'logs_servidor.db'

def guardar_en_base_de_datos(lista_datos):
   
    if isinstance(lista_datos, dict):#nos aseguramos que lista de datos ea un diccionario
        lista_datos = [lista_datos]#metemos en una lista el diccionario para tener un formato definido
        
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        insert = '''
            INSERT INTO logs (occurred_at, received_at, service, severity, message)
            VALUES (?, ?, ?, ?, ?)
        '''

        valores = [#recolectamos los valores iterando en la lista comprimida
            (
                d.get('timestamp'),#tiempo en que ocurrio el evento
                datetime.utcnow().isoformat(),#generamos un sello de tiempo exacto de insercion
                d.get('service'),#el nombre del servicio
                d.get('level'),#la severidad del reporte
                d.get('message')#descripcion del error
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
    auth_header = request.headers.get('Authorization')#accedemos al header de autorizacion
    if not auth_header or not auth_header.startswith("Bearer "):#verificamos si tiene autorizacion
        return jsonify({"error": "Quién sos, bro?"}), 401#token ivalido
    
    token_cliente = auth_header.split(" ")[1]#acedmos al valor del token

    # 2. Verificar si la llave existe en el diccionario
    if token_cliente not in TOKENS_VALIDOS:
        return jsonify({"error": "Quién sos, bro?"}), 401#token invalido
    try:
        datos = request.get_json()#transforma el logs en un diccionario
        if not datos:
            return jsonify({"error": "Cuerpo vacío"}), 400#datos invalidos

        # Procesamos la inserción (ya sea lista o dict)
        guardar_en_base_de_datos(datos)
        
        # Calculamos la cantidad de datos dentro de las lista sino quiere decir que solo hay un elemento
        cantidad = len(datos) if isinstance(datos, list) else 1

        if isinstance(datos, list):
            print(f">>> Recibido BATCH de {len(datos)} logs")
        else:
        # Mostramos Service, Level y el Mensaje específico
            print(f"[{datos.get('service')}] {datos.get('level')}: {datos.get('message')}")
        
        return jsonify({#transformamos un objeto de python a una respuesta http con formato json
            "status": "success",
            "message": "Logs procesados exitosamente",
            "info": {
                "cantidad": cantidad,
                "server_time": datetime.now().isoformat()
            }
        }), 201#se procesp correctamente
    

    except Exception as e:
        return jsonify({"error": str(e)}), 500#erros interno

@app.route('/logs', methods=['GET'])
def consultar_logs():
    # 1. Capturar parámetros de la URL despues del ?
    service = request.args.get('service')#accedemos al parametro de la consulta
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
        rows = cursor.fetchall()#obtenemos los datos de el excute anterior
        
        # 4. Formatear resultados como lista de diccionarios
        resultados = [dict(row) for row in rows]
    
        conexion.close()
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)