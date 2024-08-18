from pydantic import BaseModel
from typing import Optional

class ResultCreate(BaseModel):
    client_id: int
    HeartDisease: int
    RiskPercentage: float
    Factors: str
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
    dateRegistration: Optional[str] = None