import os
from fastapi import HTTPException
import mysql.connector
from database import create_connection
from models.result import ResultCreate

def create_result(result: ResultCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO results (client_id, HeartDisease, RiskPercentage, Factors, Sex, GeneralHealth, 
                          PhysicalHealthDays, MentalHealthDays, PhysicalActivities, SleepHours, HadStroke, HadKidneyDisease, 
                          HadDiabetes, DifficultyWalking, SmokerStatus, RaceEthnicityCategory, AgeCategory, BMI, 
                          AlcoholDrinkers, HadHighBloodCholesterol, dateRegistration) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())''',
                       (result.client_id, result.HeartDisease, result.RiskPercentage, result.Factors, result.Sex, 
                        result.GeneralHealth, result.PhysicalHealthDays, result.MentalHealthDays, result.PhysicalActivities, 
                        result.SleepHours, result.HadStroke, result.HadKidneyDisease, result.HadDiabetes, 
                        result.DifficultyWalking, result.SmokerStatus, result.RaceEthnicityCategory, result.AgeCategory, 
                        result.BMI, result.AlcoholDrinkers, result.HadHighBloodCholesterol))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Result created successfully"}

def read_results():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()
    conn.close()

    return results

def select_result_by_id(result_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM results WHERE id = %s", (result_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return result

def update_result(result_id: int, result: ResultCreate):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute('''UPDATE results SET client_id = %s, HeartDisease = %s, RiskPercentage = %s, Factors = %s, 
                          Sex = %s, GeneralHealth = %s, PhysicalHealthDays = %s, MentalHealthDays = %s, 
                          PhysicalActivities = %s, SleepHours = %s, HadStroke = %s, HadKidneyDisease = %s, 
                          HadDiabetes = %s, DifficultyWalking = %s, SmokerStatus = %s, RaceEthnicityCategory = %s, 
                          AgeCategory = %s, BMI = %s, AlcoholDrinkers = %s, HadHighBloodCholesterol = %s 
                          WHERE id = %s''',
                       (result.client_id, result.HeartDisease, result.RiskPercentage, result.Factors, result.Sex, 
                        result.GeneralHealth, result.PhysicalHealthDays, result.MentalHealthDays, result.PhysicalActivities, 
                        result.SleepHours, result.HadStroke, result.HadKidneyDisease, result.HadDiabetes, 
                        result.DifficultyWalking, result.SmokerStatus, result.RaceEthnicityCategory, result.AgeCategory, 
                        result.BMI, result.AlcoholDrinkers, result.HadHighBloodCholesterol, result_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Result updated successfully"}

def delete_result(result_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM results WHERE id = %s", (result_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        conn.close()

    return {"message": "Result deleted successfully"}