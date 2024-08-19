import os
from dotenv import load_dotenv
import mysql.connector
import bcrypt

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener los valores de las variables de entorno
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# Crear una función para la conexión
def create_connection():
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    return conn

# Crear la base de datos si no existe
def create_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    conn.commit()
    conn.close()

# Crear tablas y datos iniciales
def create_tables_and_insert_data():
    conn = create_connection()
    conn.database = database
    cursor = conn.cursor()

    # Crear tabla de roles
    cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(191) NOT NULL UNIQUE
                    )''')

    # Crear tabla de clientes (usuarios)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        first_name VARCHAR(191),
                        last_name VARCHAR(191),
                        DNI VARCHAR(8),
                        age INT,
                        sex CHAR(1),
                        username VARCHAR(191) NOT NULL UNIQUE,
                        email VARCHAR(191) NOT NULL UNIQUE,
                        password VARCHAR(191) NOT NULL,
                        role_id INT,
                        date_created DATETIME,
                        FOREIGN KEY (role_id) REFERENCES roles(id)
                    )''')

    # Crear tabla de resultados
    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        client_id INT,
                        HeartDisease INTEGER,
                        RiskPercentage FLOAT,
                        Factors TEXT,
                        Sex INTEGER,
                        GeneralHealth INTEGER,
                        PhysicalHealthDays INTEGER,
                        MentalHealthDays INTEGER,
                        PhysicalActivities INTEGER,
                        SleepHours INTEGER,
                        HadStroke INTEGER,
                        HadKidneyDisease INTEGER,
                        HadDiabetes INTEGER,
                        DifficultyWalking INTEGER,
                        SmokerStatus INTEGER,
                        RaceEthnicityCategory INTEGER,
                        AgeCategory INTEGER,
                        BMI REAL,
                        AlcoholDrinkers INTEGER,
                        HadHighBloodCholesterol INTEGER,
                        dateRegistration DATETIME,
                        FOREIGN KEY (client_id) REFERENCES users(id)
                    )''')

    # Crear tabla de revisión
    cursor.execute('''CREATE TABLE IF NOT EXISTS revision (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        results_id INT,
                        start_time TIME,
                        end_time TIME,
                        diagnosis TEXT,
                        key_factors TEXT,
                        patient_status ENUM('LEVE', 'MEDIO', 'GRAVE'),
                        date_created DATETIME,
                        FOREIGN KEY (results_id) REFERENCES results(id)
                    )''')

    # Insertar roles predeterminados
    roles = ['admin', 'medico', 'paciente']
    for role in roles:
        cursor.execute('''INSERT INTO roles (name) 
                          SELECT * FROM (SELECT %s) AS tmp 
                          WHERE NOT EXISTS (
                              SELECT name FROM roles WHERE name = %s
                          ) LIMIT 1''', (role, role))

    # Crear contraseña encriptada para el usuario administrador
    password_plain = 'password'
    password_hash = bcrypt.hashpw(password_plain.encode(), bcrypt.gensalt()).decode()

    # Insertar usuario administrador por defecto si no existe
    cursor.execute('''INSERT INTO users (first_name, last_name, DNI, age, sex, username, email, password, role_id, date_created) 
                      SELECT 'Ricardo', 'Mendoza', '78945612', 50, 'M', 'admin', 'admin@gmail.com', %s, 
                      (SELECT id FROM roles WHERE name = 'admin'), NOW()
                      WHERE NOT EXISTS (
                          SELECT username FROM users WHERE username = 'admin'
                      )''', (password_hash,))

    # Confirmar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    
    # Llamar las funciones al inicio
if __name__ == "__main__":
    create_database()
    create_tables_and_insert_data()
    print("Tablas creadas y datos iniciales insertados correctamente.")