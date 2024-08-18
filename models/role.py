from pydantic import BaseModel

class RoleCreate(BaseModel):
    name: str