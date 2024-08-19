import os
from fastapi import HTTPException
import mysql.connector
from database import create_connection
from models.revision import RevisionModel

def create_revision(revision: RevisionModel):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO revision (results_id, start_time, end_time, diagnosis, key_factors, 
                          patient_status, date_created) 
                          VALUES (%s, %s, %s, %s, %s, %s, NOW())''',
                       (revision.results_id, revision.start_time, revision.end_time, revision.diagnosis, 
                        revision.key_factors, revision.patient_status))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Revision created successfully"}

def read_revisions():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM revision")
    revisions = cursor.fetchall()
    conn.close()

    return revisions

def select_revision_by_id(revision_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM revision WHERE id = %s", (revision_id,))
    revision = cursor.fetchone()
    conn.close()

    if revision is None:
        raise HTTPException(status_code=404, detail="Revision not found")

    return revision

def update_revision(revision_id: int, revision: RevisionModel):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE revision SET results_id = %s, start_time = %s, end_time = %s, diagnosis = %s, 
                          key_factors = %s, patient_status = %s 
                          WHERE id = %s''',
                       (revision.results_id, revision.start_time, revision.end_time, revision.diagnosis, 
                        revision.key_factors, revision.patient_status, revision_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Revision updated successfully"}

def delete_revision(revision_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM revision WHERE id = %s", (revision_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Revision not found")
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Revision deleted successfully"}

def get_revision_by_result(result_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM revision WHERE results_id = %s", (result_id,))
    revision = cursor.fetchone()
    conn.close()

    if revision is None:
        raise HTTPException(status_code=404, detail="No se encotro la revision")

    return revision
