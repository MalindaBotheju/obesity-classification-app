import csv
import io
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func

from ml_utils import make_prediction

# --- DATABASE (Supabase Postgres) ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found. Please set it in your .env file.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PredictionRecord(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 16 inputs
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

    # output
    prediction_result = Column(String)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- APP ---
app = FastAPI(title="Obesity ML API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, use your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


# One input check, used by both single and batch predictions
class PatientData(BaseModel):
    Gender: str
    Age: int = Field(..., gt=0, lt=120)
    Height: float = Field(..., gt=0.5, lt=3.0, description="meters")
    Weight: float = Field(..., gt=2.0, lt=500.0, description="kg")
    family_history_with_overweight: str
    FAVC: str
    FCVC: float = Field(..., ge=1, le=3)
    NCP: float = Field(..., ge=1, le=4)
    CAEC: str
    SMOKE: str
    CH2O: float = Field(..., ge=1, le=3)
    SCC: str
    FAF: float = Field(..., ge=0, le=3)
    TUE: float = Field(..., ge=0, le=2)
    CALC: str
    MTRANS: str

    @field_validator("Height", "Weight")
    @classmethod
    def round_to_two_decimals(cls, v):
        return round(v, 2)


@app.post("/predict")
def predict(patient: PatientData, db: Session = Depends(get_db)):
    data = patient.model_dump()
    try:
        result = make_prediction(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Model error: {e}")

    db.add(PredictionRecord(**data, prediction_result=result))
    db.commit()
    return {"prediction": result}


@app.post("/predict/batch")
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    # Stop early if the CSV is missing any of the 16 columns
    missing = [c for c in PatientData.model_fields if c not in (reader.fieldnames or [])]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing columns: {', '.join(missing)}")

    records = []
    skipped = 0
    for row in reader:
        try:
            # Same checks as the single form (age "25.0" is turned into 25 first)
            row["Age"] = int(float(row["Age"]))
            data = PatientData(**{k: row[k] for k in PatientData.model_fields}).model_dump()
            result = make_prediction(data)
            records.append(PredictionRecord(**data, prediction_result=result))
        except (ValidationError, ValueError, KeyError, TypeError):
            skipped += 1  # bad row: skip it and keep going

    if not records:
        raise HTTPException(status_code=400, detail="No valid rows found in the CSV.")

    db.bulk_save_objects(records)
    db.commit()

    message = f"Saved {len(records)} predictions"
    if skipped:
        message += f" ({skipped} rows skipped because of bad data)"
    return {"message": message}
