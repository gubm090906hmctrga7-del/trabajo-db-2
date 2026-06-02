import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Gtz214079@m'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG, database="rehabilitacion_db")

def init_db():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="Gtz214079@m")
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS rehabilitacion_db")
        cursor.execute("USE rehabilitacion_db")
        
        # Tabla Usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100),
                edad INT,
                correo VARCHAR(100) UNIQUE,
                password VARCHAR(255)
            )
        """)
        
        # Tabla Boletas (Asegúrate de que tenga ID autoincremental)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boletas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                curso_nombre VARCHAR(100),
                puntuacion FLOAT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)

        # NUEVA: Tabla Favoritos
        cursor.execute("CREATE TABLE IF NOT EXISTS favoritos (user_id INT, curso_nombre VARCHAR(100))")

        # NUEVA: Tabla Notas
        cursor.execute("CREATE TABLE IF NOT EXISTS notas (user_id INT, curso_nombre VARCHAR(100), contenido TEXT)")

        conn.commit()
        print("Base de datos lista.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()