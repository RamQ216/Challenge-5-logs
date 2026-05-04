import sqlite3

def inicializar_db():#generamos la base de datos 
    # Se conecta al archivo (si no existe, lo crea)
    conexion = sqlite3.connect('logs_servidor.db')
    cursor = conexion.cursor()

    # Adaptación de tu estructura a SQLite
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            occurred_at TIMESTAMP NOT NULL,
            received_at TIMESTAMP NOT NULL,
            service VARCHAR(100) NOT NULL,
            severity VARCHAR(100) NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()
    print("Base de datos SQLite creada y tabla 'logs' lista.")

if __name__ == "__main__":
    inicializar_db()