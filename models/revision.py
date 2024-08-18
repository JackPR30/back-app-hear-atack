from pydantic import BaseModel
from datetime import datetime

class RevisionModel(BaseModel):
    results_id: int
    start_time: str
    end_time: str
    diagnosis: str
    key_factors: str
    patient_status: str
    date_created: datetime
    
    