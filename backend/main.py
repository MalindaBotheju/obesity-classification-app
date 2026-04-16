import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Response
import csv
import io
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from ml_utils import make_prediction

# Import Pydantic tools for strict data validation
from pydantic import BaseModel, Field, field_validator

# Load environment variables from the .env file
load_dotenv()

# --- DATABASE SETUP ---
# Fetch the URL securely from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If it can't find the URL, throw an error immediately so we know what's wrong
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found. Please set it in your .env file.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Table Model (Now includes ALL inputs + timestamp)
class PredictionRecord(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # All 16 Input Variables
    Gender = Column(String)
    Age = Column(Float) # Leaving as Float in DB to prevent schema errors with existing data
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
    
    # Output
    prediction_result = Column(String)

# Create the tables in the database automatically
Base.metadata.create_all(bind=engine)

# --- FASTAPI APP SETUP ---
app = FastAPI(title="Obesity ML API")

# Allow the frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC SCHEMAS (For Input Validation) ---
class PatientData(BaseModel):
    Gender: str
    Age: int = Field(..., gt=0, lt=120, description="Age must be a whole number between 0 and 120")
    Height: float = Field(..., gt=0.5, lt=3.0, description="Height in meters")
    Weight: float = Field(..., gt=2.0, lt=500.0, description="Weight in kg")
    family_history_with_overweight: str
    FAVC: str
    FCVC: float = Field(..., ge=1, le=3, description="Vegetable consumption must be between 1 and 3")
    NCP: float = Field(..., ge=1, le=4, description="Number of main meals must be between 1 and 4")
    CAEC: str
    SMOKE: str
    CH2O: float = Field(..., ge=1, le=3, description="Daily water intake must be between 1 and 3")
    SCC: str
    FAF: float = Field(..., ge=0, le=3, description="Physical activity must be between 0 and 3")
    TUE: float = Field(..., ge=0, le=2, description="Time using technology must be between 0 and 2")
    CALC: str
    MTRANS: str

    # Automatically round Height and Weight to 2 decimal places
    @field_validator('Height', 'Weight')
    @classmethod
    def round_to_two_decimals(cls, v):
        return round(v, 2)

# --- API ENDPOINTS ---

@app.post("/predict")
def predict(patient: PatientData, db: Session = Depends(get_db)):
    # 1. Convert input to dictionary
    data_dict = patient.model_dump()
    
    # 2. Get the prediction from our ML model
    try:
        result = make_prediction(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Model error: {str(e)}")
    
    # 3. Save ALL inputs + prediction to database
    record_data = data_dict.copy()
    record_data["prediction_result"] = result
    
    db_record = PredictionRecord(**record_data)
    db.add(db_record)
    db.commit()
    
    # 4. Return the result to the frontend
    return {"prediction": result}

@app.post("/predict_batch")
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Read the uploaded CSV file
    content = await file.read()
    decoded_content = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded_content))

    results = []
    db_records = []

    # 2. Process each row in the CSV
    for row in reader:
        try:
            # Convert the CSV text into the correct data types
            # Note: Age uses int(float(...)) so "25.0" securely converts to 25
            data_dict = {
                "Gender": row["Gender"],
                "Age": int(float(row["Age"])),
                "Height": round(float(row["Height"]), 2),
                "Weight": round(float(row["Weight"]), 2),
                "family_history_with_overweight": row["family_history_with_overweight"],
                "FAVC": row["FAVC"],
                "FCVC": float(row["FCVC"]),
                "NCP": float(row["NCP"]),
                "CAEC": row["CAEC"],
                "SMOKE": row["SMOKE"],
                "CH2O": float(row["CH2O"]),
                "SCC": row["SCC"],
                "FAF": float(row["FAF"]),
                "TUE": float(row["TUE"]),
                "CALC": row["CALC"],
                "MTRANS": row["MTRANS"]
            }
            
            # Get prediction
            pred = make_prediction(data_dict)
            
            # Prepare database record
            record_data = data_dict.copy()
            record_data["prediction_result"] = pred
            db_records.append(PredictionRecord(**record_data))
            
            # Add prediction to our output row
            row["prediction_result"] = pred
            results.append(row)
            
        except Exception as e:
            # If a row has missing or bad data, skip it and continue
            print(f"Skipping row due to error: {e}")
            continue

    # 3. Save all 1000+ records to Supabase at once (Bulk Insert)
    if db_records:
        db.bulk_save_objects(db_records)
        db.commit()

    # 4. Generate a new CSV file with the predictions to send back
    output = io.StringIO()
    if results:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # 5. Return the file as a downloadable attachment
    return Response(
        content=output.getvalue(), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=hospital_predictions.csv"}
    )

@app.get("/history")
def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # By default it fetches 100 records. 
    # To get more, you can change the URL to: /history?limit=1000
    records = db.query(PredictionRecord).order_by(PredictionRecord.id.desc()).offset(skip).limit(limit).all()
    return records