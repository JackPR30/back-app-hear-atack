import os
from fastapi import HTTPException
from database import create_connection
import bcrypt
from models.client import UserCreate
import mysql.connector
def create_cliente(user: UserCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode()

    try:
        cursor.execute('''INSERT INTO clients (first_name, last_name, DNI, age, sex, username, email, password, role_id, date_created) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())''',
                       (user.first_name, user.last_name, user.DNI, user.age, user.sex, user.username, user.email, hashed_password, user.role_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "User created successfully"}

def read_clientes():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()

    return clients

def select_cliente_by_id(client_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
    client = cursor.fetchone()
    conn.close()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    return client

def update_cliente(client_id: int, user: UserCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode()

    try:
        cursor.execute('''UPDATE clients SET first_name = %s, last_name = %s, DNI = %s, age = %s, sex = %s,
                          username = %s, email = %s, password = %s, role_id = %s 
                          WHERE id = %s''',
                       (user.first_name, user.last_name, user.DNI, user.age, user.sex, user.username, user.email, hashed_password, user.role_id, client_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Client updated successfully"}

def delete_cliente(client_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Client deleted successfully"}