from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    DNI: str
    age: int
    sex: str
    phone: str
    username: str
    email: str
    password: str
    role_id: int