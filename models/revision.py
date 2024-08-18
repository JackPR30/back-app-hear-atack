from pydantic import BaseModel
from typing import Optional

class RevisionCreate(BaseModel):
    results_id: int
    start_time: str
    end_time: str
    diagnosis: str
    key_factors: str
    patient_status: str  # 'LEVE', 'MEDIO', 'GRAVE'
    date_created: Optional[str] = None