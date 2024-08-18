import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware de CORS
from pydantic import BaseModel
import bcrypt
import mysql.connector
from models.user import UserCreate
from cruds import users, results, revision, role, analytic
from cruds import analytic  # Asegúrate de que estás importando correctamente
from cruds.analytic import get_all_results
from cruds.analytic import get_results_by_client_id
from database import create_connection, create_database, create_tables_and_insert_data

app = FastAPI()

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







# REVISIONES
# Listar todas las revisiones
@app.get("/revisions/")
def read_revisions():
    return revision.read_revisions()

# Obtener una revisión por su ID
@app.get("/revisions/{revision_id}")
def select_revision_by_id(revision_id: int):
    return revision.select_revision_by_id(revision_id)

# Crear una nueva revisión
@app.post("/revisions/")
def create_revision(revision: UserCreate):
    return revision.create_revision(revision)

# Actualizar una revisión
@app.put("/revisions/{revision_id}")
def update_revision(revision_id: int, revision: UserCreate):
    return revision.update_revision(revision_id, revision)

# Eliminar una revisión
@app.delete("/revisions/{revision_id}")
def delete_revision(revision_id: int):
    return revision.delete_revision(revision_id)

# Obtener una revisión por su ID resultado
@app.get("/revisionresult/{result_id}")
def get_revision_by_result(result_id: int):
    return revision.get_revision_by_result(result_id)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)