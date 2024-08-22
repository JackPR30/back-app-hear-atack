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

def read_results_with_state_revision_service(client_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT 
            r.*,
            IF(rv.id IS NULL, 0, 1) AS status_revision
        FROM 
            results r
        LEFT JOIN 
            revision rv 
        ON 
            r.id = rv.results_id
        WHERE 
            r.client_id = %s
    '''
    cursor.execute(query,(client_id,))
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


SEX = {1: 'Male', 2: 'Female'}
GEN_HEALTH = {1: "Excellent", 2: "Very good", 3: "Good", 4: "Fair", 5: "Poor"}
DIABETES = {1: "Yes", 2: "Yes, but only during pregnancy (female)", 3: "No", 4: "No, pre-diabetes or borderline diabetes"}
SMOKER_STATUS = {1: "Current smoker - now smokes every day", 2: "Current smoker - now smokes some days", 3: "Former smoker", 4: "Never smoked"}
RACE = {1: "White only, Non-Hispanic", 2: "Black only, Non-Hispanic", 3: "Other race only, Non-Hispanic", 4: "Multiracial, Non-Hispanic", 5: "Hispanic"}
AGE_CATEGORY = {1: "Age 18 to 24", 2: "Age 25 to 29", 3: "Age 30 to 34", 4: "Age 35 to 39", 5: "Age 40 to 44", 6: "Age 45 to 49", 7: "Age 50 to 54", 8: "Age 55 to 59", 9: "Age 60 to 64", 10: "Age 65 to 69", 11: "Age 70 to 74", 12: "Age 75 to 79", 13: "Age 80 or older"}

def read_results_byName(client_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM results LEFT JOIN revision ON results.id = revision.results_id WHERE results.client_id = %s"
    cursor.execute(query, (client_id,))
    
    results = cursor.fetchall()
    conn.close()

    # Convertir los valores numéricos a sus representaciones de texto y reemplazarlos
    for result in results:
        result['HeartDisease'] = 'Sí' if result.get('HeartDisease') == 1 else 'No'
        result['Sex'] = SEX.get(result.get('Sex'), 'Unknown')
        result['GeneralHealth'] = GEN_HEALTH.get(result.get('GeneralHealth'), 'Unknown')
        result['PhysicalActivities'] = 'Sí' if result.get('PhysicalActivities') == 1 else 'No'
        result['HadStroke'] = 'Sí' if result.get('HadStroke') == 1 else 'No'
        result['HadKidneyDisease'] = 'Sí' if result.get('HadKidneyDisease') == 1 else 'No'
        result['HadDiabetes'] = DIABETES.get(result.get('HadDiabetes'), 'Unknown')
        result['DifficultyWalking'] = 'Sí' if result.get('DifficultyWalking') == 1 else 'No'
        result['SmokerStatus'] = SMOKER_STATUS.get(result.get('SmokerStatus'), 'Unknown')
        result['RaceEthnicityCategory'] = RACE.get(result.get('RaceEthnicityCategory'), 'Unknown')
        result['AgeCategory'] = AGE_CATEGORY.get(result.get('AgeCategory'), 'Unknown')
        result['AlcoholDrinkers'] = 'Sí' if result.get('AlcoholDrinkers') == 1 else 'No'
        result['HadHighBloodCholesterol'] = 'Sí' if result.get('HadHighBloodCholesterol') == 1 else 'No'
    
    return results