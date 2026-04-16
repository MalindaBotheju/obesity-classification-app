import joblib
import pandas as pd

# 1. Load the dictionary containing all our saved assets
model_assets = joblib.load("obesity_full_pipeline.joblib")

# 2. Extract the individual pieces
model = model_assets["model"]
scaler = model_assets["scaler"]
imputer = model_assets["imputer"]
encoders = model_assets["label_encoders"]

# 3. Create a reverse mapping to turn the numeric prediction back into a readable string
NObeyesdad_mapping = {
    "Obesity_Type_I": 0, "Obesity_Type_III": 1, "Obesity_Type_II": 2,
    "Overweight_Level_II": 3, "Normal_Weight": 4, "Overweight_Level_I": 5,
    "Insufficient_Weight": 6
}
reverse_mapping = {v: k for k, v in NObeyesdad_mapping.items()}

def make_prediction(data: dict) -> str:
    # Convert input to DataFrame
    df = pd.DataFrame([data])
    
    # --- PREPROCESSING ---
    
    # 1. Apply Label Encoders
    cols_to_encode = ["Gender", "family_history_with_overweight", "FAVC", "SMOKE", "SCC"]
    for col in cols_to_encode:
        df[col] = encoders[col].transform(df[col])
        
    # 2. Apply Manual Mapping for CAEC and CALC
    frequency_mapping = {'no': 0, 'Sometimes': 1, 'Frequently': 2, 'Always': 3}
    for col in ['CAEC', 'CALC']:
        df[col] = df[col].map(frequency_mapping)
        
    # 3. Handle MTRANS One-Hot Encoding manually
    mtrans_categories = ["Automobile", "Bike", "Motorbike", "Public_Transportation", "Walking"]
    for cat in mtrans_categories:
        df[f"MTRANS_{cat}"] = 1 if df["MTRANS"].iloc[0] == cat else 0
    df = df.drop("MTRANS", axis=1)

    # 4. Ensure column order perfectly matches what the imputer/scaler expect
    expected_columns = imputer.feature_names_in_
    
    # Handle the CH2O vs CH20 typo from the original dataset
    if "CH20" in expected_columns and "CH2O" in df.columns:
        df = df.rename(columns={"CH2O": "CH20"})
        
    df = df[expected_columns]

    # 5. Impute and Scale
    df_imputed_array = imputer.transform(df)
    # Convert back to DataFrame so the scaler gets the column names it expects
    df_imputed = pd.DataFrame(df_imputed_array, columns=expected_columns)
    df_scaled = scaler.transform(df_imputed)
    # --- PREDICTION ---
    
    # 6. Get the numeric prediction
    prediction_num = model.predict(df_scaled)[0]
    
    # 7. Convert number back to text and return
    return reverse_mapping[prediction_num]