from pydantic import BaseModel


class InputData(BaseModel):
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