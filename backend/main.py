
import csv
import io
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func

from ml_utils import make_prediction

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    Gender = Column(String)
    Age = Column(Float)
    Height = Column(Float)
    Weight = Column(Float)
    family_history_with_overweight = Column(String)
    FAVC = Column(String)
    FCVC = Column(Float)
    NCP = Column(Float)
    CAEC = Column(String)
    SMOKE = Column(String)
    CH2O = Column(Float)
    SCC = Column(String)
    FAF = Column(Float)
    TUE = Column(Float)
    CALC = Column(String)
    MTRANS = Column(String)

    prediction_result = Column(String)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Obesity ML API")


class PatientData(BaseModel):
    Gender: str
    Age: int = Field(gt=0, lt=120)
    Height: float = Field(gt=0.5, lt=3.0)
    Weight: float = Field(gt=2, lt=500)
    family_history_with_overweight: str
    FAVC: str
    FCVC: float = Field(ge=1, le=3)
    NCP: float = Field(ge=1, le=4)
    CAEC: str
    SMOKE: str
    CH2O: float = Field(ge=1, le=3)
    SCC: str
    FAF: float = Field(ge=0, le=3)
    TUE: float = Field(ge=0, le=2)
    CALC: str
    MTRANS: str

    @field_validator("Height", "Weight")
    @classmethod
    def round_values(cls, value):
        return round(value, 2)


@app.post("/predict")
def predict(patient: PatientData, db: Session = Depends(get_db)):
    data = patient.model_dump()

    try:
        result = make_prediction(data)
        db.add(PredictionRecord(**data, prediction_result=result))
        db.commit()
        return {"prediction": result}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict/batch")
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    required = list(PatientData.model_fields)
    missing = [col for col in required if col not in (reader.fieldnames or [])]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing CSV columns: {', '.join(missing)}"
        )

    records = []
    skipped = 0

    for row in reader:
        try:
            row["Age"] = int(float(row["Age"]))
            data = PatientData(**{key: row[key] for key in required}).model_dump()
            result = make_prediction(data)
            records.append(PredictionRecord(**data, prediction_result=result))
        except (ValidationError, ValueError, KeyError, TypeError):
            skipped += 1

    if not records:
        raise HTTPException(status_code=400, detail="No valid rows found.")

    try:
        db.add_all(records)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save predictions.")

    return {
        "message": f"Saved {len(records)} predictions.",
        "skipped_rows": skipped
    }
