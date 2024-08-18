import os
from fastapi import HTTPException
import mysql.connector
from database import create_connection
from models.role import RoleCreate

def create_role(role: RoleCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO roles (name) VALUES (%s)''', (role.name,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Role created successfully"}

def list_roles():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    conn.close()

    return roles

def get_role(role_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    role = cursor.fetchone()
    conn.close()

    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return role

def update_role(role_id: int, role: RoleCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE roles SET name = %s WHERE id = %s''', (role.name, role_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Role updated successfully"}

def delete_role(role_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Role not found")
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Role deleted successfully"}
