import joblib
import pandas as pd
from fastapi import HTTPException
from models.analytic import InputData
from database import create_connection
import os
import mysql.connector

# Cargar el modelo y los datos necesarios
modelo_rf = joblib.load('modelo_rf.joblib')
X_data = joblib.load('X_data.joblib')

def unified_predict(input_data: InputData):
    
    client_id = input_data.client_id  # Guarda el client_id para su uso posterior
    try:
        # Convertir la entrada en un DataFrame
        input_dict = input_data.dict()
        input_dict.pop('client_id')  # Elimina client_id del diccionario
        input_df = pd.DataFrame([input_dict])

        # Realizar la predicción
        prediccion = modelo_rf.predict(input_df)
        probabilidad = modelo_rf.predict_proba(input_df)[:, 1][0]
        
        # Construir mensaje de riesgo
        riesgo_mensaje = f"El riesgo estimado de enfermedad cardíaca es de {probabilidad * 100:.2f}%."

        # Calcular el impacto de las características
        probabilidad_base = modelo_rf.predict_proba(input_df)[:, 1]
        impactos = {}
        for feature in X_data.columns:
            temp_df = input_df.copy()
            valor_medio = X_data[feature].mean()
            temp_df[feature] = valor_medio
            probabilidad_cambiada = modelo_rf.predict_proba(temp_df)[:, 1]
            impacto = abs(probabilidad_cambiada - probabilidad_base)[0]
            impactos[feature] = impacto

        # Convertir los impactos a un DataFrame y ordenar por impacto
        impacto_df = pd.DataFrame(list(impactos.items()), columns=['Feature', 'Impact']).sort_values(by='Impact', ascending=False)

        # Obtener las 5 características más influyentes
        top_5_importances = impacto_df.head(5)
        mensajes_importancias = "\n".join([f"{row['Feature']}: {row['Impact']:.4f}" for _, row in top_5_importances.iterrows()])

        # Construir mensaje de características influyentes
        impacto_mensaje = "Las características más influyentes en la predicción son:\n\n"
        impacto_mensaje += mensajes_importancias

        # Dictamen de la enfermedad cardíaca
        diagnostico_mensaje = "Presentas una enfermedad cardíaca" if prediccion[0] == 1 else "No presentas una enfermedad cardíaca"

        # Registrar el resultado en la base de datos
        factores = ", ".join([f"{row['Feature']}={row['Impact']:.4f}" for _, row in top_5_importances.iterrows()])

        # Crear la conexión a la base de datos
        conn = create_connection()
        conn.database = os.getenv("DB_NAME")
        cursor = conn.cursor()

        try:
            cursor.execute('''INSERT INTO results (client_id, HeartDisease, RiskPercentage, Factors, Sex, GeneralHealth, 
                              PhysicalHealthDays, MentalHealthDays, PhysicalActivities, SleepHours, HadStroke, HadKidneyDisease, 
                              HadDiabetes, DifficultyWalking, SmokerStatus, RaceEthnicityCategory, AgeCategory, BMI, 
                              AlcoholDrinkers, HadHighBloodCholesterol, dateRegistration) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())''',
                           (client_id, prediccion[0], probabilidad * 100, factores, input_data.Sex, 
                            input_data.GeneralHealth, input_data.PhysicalHealthDays, input_data.MentalHealthDays, 
                            input_data.PhysicalActivities, input_data.SleepHours, input_data.HadStroke, 
                            input_data.HadKidneyDisease, input_data.HadDiabetes, input_data.DifficultyWalking, 
                            input_data.SmokerStatus, input_data.RaceEthnicityCategory, input_data.AgeCategory, 
                            input_data.BMI, input_data.AlcoholDrinkers, input_data.HadHighBloodCholesterol))
            conn.commit()
        except mysql.connector.Error as err:
            conn.rollback()
            raise HTTPException(status_code=400, detail=str(err))
        finally:
            conn.close()

        # Construir la respuesta en formato JSON
        respuesta = {
            "riesgo": riesgo_mensaje,
            "impacto": dict(zip(impacto_df['Feature'], impacto_df['Impact'])),
            "diagnostico": diagnostico_mensaje
        }
        
        return respuesta
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error realizando la predicción: {str(e)}")




def get_all_results():
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM results")
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron resultados")
        return results
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        conn.close()


def get_results_by_client_id(client_id: int):
    conn = create_connection()
    conn.database = os.getenv("DB_NAME")
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM results WHERE client_id = %s", (client_id,))
        results = cursor.fetchall()
        if not results:
            raise HTTPException(status_code=404, detail=f"No se encontraron resultados para el client_id: {client_id}")
        return results
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        conn.close()

