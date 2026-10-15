
import joblib
import pandas as pd

assets = joblib.load("obesity_full_pipeline.joblib")

model = assets["model"]
scaler = assets["scaler"]
imputer = assets["imputer"]
encoders = assets["label_encoders"]

reverse_mapping = {
    0: "Obesity_Type_I",
    1: "Obesity_Type_III",
    2: "Obesity_Type_II",
    3: "Overweight_Level_II",
    4: "Normal_Weight",
    5: "Overweight_Level_I",
    6: "Insufficient_Weight"
}


def make_prediction(data: dict) -> str:
    df = pd.DataFrame([data])

    cols_to_encode = [
        "Gender",
        "family_history_with_overweight",
        "FAVC",
        "SMOKE",
        "SCC"
    ]

    for col in cols_to_encode:
        df[col] = encoders[col].transform(df[col])

    frequency_mapping = {
        "no": 0,
        "Sometimes": 1,
        "Frequently": 2,
        "Always": 3
    }

    for col in ["CAEC", "CALC"]:
        df[col] = df[col].map(frequency_mapping)

    categories = [
        "Automobile",
        "Bike",
        "Motorbike",
        "Public_Transportation",
        "Walking"
    ]

    for category in categories:
        df[f"MTRANS_{category}"] = (
            df["MTRANS"] == category
        ).astype(int)

    df = df.drop("MTRANS", axis=1)

    columns = imputer.feature_names_in_

    if "CH20" in columns and "CH2O" in df.columns:
        df = df.rename(columns={"CH2O": "CH20"})

    df = df[columns]

    imputed = imputer.transform(df)
    imputed = pd.DataFrame(imputed, columns=columns)
    scaled = scaler.transform(imputed)

    prediction = model.predict(scaled)[0]

    return reverse_mapping[prediction]
