from pydantic import BaseModel
from datetime import datetime, time

class RevisionModel(BaseModel):
    results_id: int
    start_time: time
    end_time: time
    diagnosis: str
    key_factors: str
    patient_status: str
    date_created: datetime
