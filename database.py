# Importamos el conector oficial de MySQL para Python
import mysql.connector
# Importamos la clase de error para poder capturar fallos de conexión/consultas
from mysql.connector import Error

# Datos de conexión al servidor MySQL (host, usuario y contraseña)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Gtz214079@m'
}

# Devuelve una conexión activa a la base de datos del proyecto
def get_db():
    # Nos conectamos usando los datos de DB_CONFIG y seleccionamos la base "rehabilitacion_db"
    return mysql.connector.connect(**DB_CONFIG, database="rehabilitacion_db")

# Crea la base de datos y las tablas necesarias si todavía no existen
def init_db():
    try:
        # Conexión inicial sin seleccionar base de datos (todavía no existe)
        conn = mysql.connector.connect(host="localhost", user="root", password="Gtz214079@m")
        cursor = conn.cursor()
        # Creamos la base de datos del proyecto si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS rehabilitacion_db")
        # Nos cambiamos a la base de datos recién creada (o ya existente)
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
        # ^ Tabla con los datos de cada usuario registrado: id único, nombre, edad,
        #   correo (no se puede repetir) y contraseña (guardada encriptada)

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
        # ^ Tabla que guarda cada examen aprobado: a qué usuario pertenece,
        #   de qué curso, qué calificación obtuvo y en qué fecha

        # NUEVA: Tabla Favoritos
        cursor.execute("CREATE TABLE IF NOT EXISTS favoritos (user_id INT, curso_nombre VARCHAR(100))")
        # ^ Relaciona usuarios con los cursos que marcaron como favoritos

        # NUEVA: Tabla Notas
        cursor.execute("CREATE TABLE IF NOT EXISTS notas (user_id INT, curso_nombre VARCHAR(100), contenido TEXT)")
        # ^ Guarda las notas personales que cada usuario escribe dentro de un curso

        # Confirmamos (guardamos) la creación de la base de datos y tablas
        conn.commit()
        print("Base de datos lista.")
    except Error as e:
        # Si algo falla (por ejemplo, credenciales incorrectas), mostramos el error en consola
        print(f"Error: {e}")
    finally:
        # Cerramos siempre el cursor y la conexión, haya habido error o no
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()
