import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware de CORS
from pydantic import BaseModel
from models.user import UserCreate
from cruds import RevisionService, users, results, role, analytic
from cruds.RevisionService import get_revision_by_result_id
from cruds.analytic import get_all_results
from cruds.analytic import unified_predict
from cruds.analytic import get_results_by_client_id
from cruds.analytic import update_predict
from cruds.analytic import delete_result
from database import  create_database, create_tables_and_insert_data
from models.revision import RevisionModel
from database import create_connection, create_database, create_tables_and_insert_data
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()

@app.get("/clients/")
def get_clients():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name, ' - DNI: ', DNI) FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'paciente')")
        clients = cursor.fetchall()
        return [{"id": client[0], "name": client[1]} for client in clients]
    except Exception as e:
        print(f"Error fetching clients: {e}")
        raise HTTPException(status_code=500, detail="Error fetching clients")
    finally:
        cursor.close()
        conn.close()

@app.get("/clients/{client_id}/report")
def get_client_report(client_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Obtener el número total de análisis realizados para el cliente
        cursor.execute("""
            SELECT COUNT(*)
            FROM results
            WHERE client_id = %s
        """, (client_id,))
        total_analyses = cursor.fetchone()[0]

        # Obtener el número de análisis positivos (HeartDisease = 1)
        cursor.execute("""
            SELECT COUNT(*)
            FROM results
            WHERE client_id = %s AND HeartDisease = 1
        """, (client_id,))
        positive_analyses = cursor.fetchone()[0]

        # Obtener datos históricos para gráficos
        cursor.execute("""
            SELECT dateRegistration, BMI, MentalHealthDays, PhysicalHealthDays 
            FROM results
            WHERE client_id = %s
            ORDER BY dateRegistration ASC
        """, (client_id,))
        history_data = cursor.fetchall()

        history = {
            "dates": [row[0] for row in history_data],
            "bmi": [row[1] for row in history_data],
            "mentalHealthDays": [row[2] for row in history_data],
            "physicalHealthDays": [row[3] for row in history_data],
        }

        return {
            "totalAnalyses": total_analyses,
            "positiveAnalyses": positive_analyses,
            "history": history,
        }
    except Exception as e:
        print(f"Error fetching client report: {e}")
        raise HTTPException(status_code=500, detail="Error fetching client report")
    finally:
        cursor.close()
        conn.close()

@app.get("/users/count")
def get_user_count():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        print(f"Error fetching user count: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user count")
    finally:
        cursor.close()
        conn.close()

@app.get("/doctors/count")
def get_doctor_count():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'medico')")
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        print(f"Error fetching doctor count: {e}")
        raise HTTPException(status_code=500, detail="Error fetching doctor count")
    finally:
        cursor.close()
        conn.close()

@app.get("/patients/detected/count")
def get_patients_detected_count():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM results WHERE HeartDisease = 1")
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        print(f"Error fetching detected patients count: {e}")
        raise HTTPException(status_code=500, detail="Error fetching detected patients count")
    finally:
        cursor.close()
        conn.close()

def get_diagnosis_accuracy_rate():
    conn = create_connection()
    cursor = conn.cursor()
    query = '''
    SELECT ((SELECT COUNT(RD.id) 
             FROM results RD
             INNER JOIN revision R ON R.results_id = RD.id
             WHERE diagnosis = "CORRECTO") / 
            (SELECT COUNT(RD.id) 
             FROM results RD
             INNER JOIN revision R ON R.results_id = RD.id)) * 100;
    '''
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except Exception as e:
        print(f"Error executing query: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_severe_case_reduction_rate():
    conn = create_connection()
    cursor = conn.cursor()
    query = '''
    SELECT (((SELECT COUNT(id)
             FROM (
                SELECT id, ROW_NUMBER() OVER (ORDER BY date_created ASC) AS orden
                FROM revision
                WHERE patient_status = "GRAVE"
             ) AS sq
             WHERE orden <= (SELECT COUNT(*) * 0.5 FROM revision)) - 
             (SELECT COUNT(id)
             FROM (
                SELECT id, ROW_NUMBER() OVER (ORDER BY date_created DESC) AS orden
                FROM revision
                WHERE patient_status = "GRAVE"
             ) AS sq
             WHERE orden <= (SELECT COUNT(*) * 0.5 FROM revision))) / 
            (SELECT COUNT(id)
             FROM (
                SELECT id, ROW_NUMBER() OVER (ORDER BY date_created ASC) AS orden
                FROM revision
                WHERE patient_status = "GRAVE"
             ) AS sq
             WHERE orden <= (SELECT COUNT(*) * 0.5 FROM revision))) * 100;
    '''
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except Exception as e:
        print(f"Error executing query: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_diagnosis_time_reduction_rate():
    conn = create_connection()
    cursor = conn.cursor()
    query = '''
    SELECT (((SELECT AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) 
             FROM revision 
             ORDER BY date_created DESC LIMIT 10) -
            (SELECT AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) 
             FROM revision)) / 
            (SELECT AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) 
             FROM revision)) * 100;
    '''
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except Exception as e:
        print(f"Error executing query: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_kpi_emoji(kpi_value, kpi_number):
    if kpi_number == 1:
        if kpi_value > 60:
            return "🟢"
        elif 40 <= kpi_value <= 60:
            return "🟡"
        else:
            return "🔴"
    elif kpi_number == 2:
        if kpi_value > 50:
            return "🟢"
        elif 20 <= kpi_value <= 50:
            return "🟡"
        else:
            return "🔴"
    elif kpi_number == 3:
        if kpi_value >= 60:
            return "🟢"
        elif 20 <= kpi_value < 60:
            return "🟡"
        else:
            return "🔴"

@app.get("/kpi/diagnosis-accuracy-rate/")
def diagnosis_accuracy_rate():
    kpi_value = get_diagnosis_accuracy_rate()
    emoji = get_kpi_emoji(kpi_value, 1)
    return kpi_value

@app.get("/kpi/severe-case-reduction-rate/")
def severe_case_reduction_rate():
    kpi_value = get_severe_case_reduction_rate()
    emoji = get_kpi_emoji(kpi_value, 2)
    return kpi_value

@app.get("/kpi/diagnosis-time-reduction-rate/")
def diagnosis_time_reduction_rate():
    kpi_value = get_diagnosis_time_reduction_rate()
    emoji = get_kpi_emoji(kpi_value, 3)
    return kpi_value

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las orígenes. Cambia esto a un dominio específico en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Permite todos los encabezados.
)

# Inicializar la base de datos al arrancar la aplicación utilizando el nuevo esquema Lifespan
@app.on_event("startup")
async def startup_event():
    create_database()
    create_tables_and_insert_data()

# Ruta raíz para verificar que la API está funcionando
@app.get("/")
def read_root():
    return {"message": "API is up and running!"}

# Modelo de datos para predicción (asegúrate de que esté correctamente importado)
class InputData(BaseModel):
    client_id: int  # Incluye client_id en el modelo
    Sex: int
    GeneralHealth: int
    PhysicalHealthDays: int
    MentalHealthDays: int
    PhysicalActivities: int
    SleepHours: int
    HadStroke: int
    HadKidneyDisease: int
    HadDiabetes: int
    DifficultyWalking: int
    SmokerStatus: int
    RaceEthnicityCategory: int
    AgeCategory: int
    BMI: float
    AlcoholDrinkers: int
    HadHighBloodCholesterol: int

# Ruta para realizar la predicción unificada
@app.post("/predict/")
def unified_predict_route(analytic_data: InputData):
    return unified_predict(analytic_data)

# Ruta para obtener todos los resultados
@app.get("/results/")
def get_all_results_route():
    return get_all_results()

# Ruta para obtener resultados por client_id
@app.get("/results/{client_id}")
def get_results_by_client_id_route(client_id: int):
    return get_results_by_client_id(client_id)


# Ruta para actualizar un resultado por client_id
@app.put("/predict/{id}")
def update_predict_route(id: int, updated_data: InputData):
    return update_predict(id, updated_data)


# Ruta para eliminar un resultado por id
@app.delete("/results/{id}")
def delete_result_route(id: int):
    return delete_result(id)


# Iniciar sesión de usuario
class LoginData(BaseModel):
    email: str
    password: str
@app.post("/login/")
def login(login_data: LoginData):
    return users.login_users(login_data.email, login_data.password)

# Crear un nuevo usuario
@app.post("/users/")
def create_user(user: UserCreate):
    return users.create_user(user)


# CLIENTES
# Listar todos los users
@app.get("/users/")
def read_users():
    return users.read_users()

#listar clientes
@app.get("/clients/")
def read_users():
    return users.read_clients()

# Obtener un user por su ID
@app.get("/users/{client_id}")
def select_user_by_id(client_id: int):
    return users.select_user_by_id(client_id)

# Actualizar un user
@app.put("/users/{client_id}")
def update_user(client_id: int, user: UserCreate):
    return users.update_user(client_id, user)

# Eliminar un user
@app.delete("/users/{client_id}")
def delete_user(client_id: int):
    return users.delete_user(client_id)


# ----------------------------- REVISIONES ----------------
# Listar todas las revisiones
@app.get("/api/revision/list")
def read_revisions():
    return RevisionService.read_revisions()

# Crear una nueva revisión
@app.post("/api/revision/save")
def create_revision(revision: RevisionModel):
    return RevisionService.create_revision(revision)

# Obtener una revisión por su ID
@app.get("/api/revision/get/{revision_id}")
def select_revision_by_id(revision_id: int):
    return RevisionService.select_revision_by_id(revision_id)

@app.get("/api/revision/by_result_id/{results_id}")
def get_revision(results_id: int):
    revision = get_revision_by_result_id(results_id)
    if revision is None:
        raise HTTPException(status_code=404, detail="Revision not found")
    return revision

# Actualizar una revisión
@app.put("/api/revision/update/{revision_id}")
def update_revision(revision_id: int, revision: RevisionModel):
    return RevisionService.update_revision(revision_id, revision)

# Eliminar una revisión
@app.delete("/api/revision/delete/{revision_id}")
def delete_revision(revision_id: int):
    return RevisionService.delete_revision(revision_id)

# Obtener una revisión por su ID resultado
@app.get("/api/revision/get/result/{result_id}")
def get_revision_by_result(result_id: int):
    return RevisionService.get_revision_by_result(result_id)

# ROLES
# Listar todos los roles
@app.get("/roles/")
def list_roles():
    return role.list_roles()

# Obtener un rol por su ID
@app.get("/roles/{role_id}")
def get_role(role_id: int):
    return role.get_role(role_id)

# Crear un nuevo rol
@app.post("/roles/")
def create_role(role: UserCreate):
    return role.create_role(role)

# Actualizar un rol
@app.put("/roles/{role_id}")
def update_role(role_id: int, role: UserCreate):
    return role.update_role(role_id, role)

# Eliminar un rol
@app.delete("/roles/{role_id}")
def delete_role(role_id: int):
    return role.delete_role(role_id)

@app.get("/historial/{client_id}")
def get_historial(client_id: int):
    return results.read_results_byName(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
